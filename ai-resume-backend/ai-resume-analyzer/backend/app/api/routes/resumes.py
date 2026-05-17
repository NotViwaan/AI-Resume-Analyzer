import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, status
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional
from app.core.dependencies import DBDep, CurrentUser, CurrentUserID
from app.services.resume_parser import save_and_extract
from app.services.scorer import run_analysis_pipeline, enrich_candidate_from_resume
from app.schemas.resume import (
    ResumeUploadResponse,
    ResumeAnalysisResponse,
    AnalyzeRequest,
    BulkAnalyzeRequest,
    ResumeListResponse,
)
from app.models.resume import AIAnalysis

router = APIRouter(prefix="/resumes", tags=["Resumes"])


def _serialize(doc: dict) -> ResumeAnalysisResponse:
    analysis_data = doc.get("analysis")
    analysis = AIAnalysis(**analysis_data) if analysis_data else None
    return ResumeAnalysisResponse(
        id=str(doc["_id"]),
        candidate_id=doc["candidate_id"],
        job_id=doc.get("job_id"),
        filename=doc["filename"],
        analysis_status=doc.get("analysis_status", "pending"),
        analysis=analysis,
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    db: DBDep,
    user_id: CurrentUserID,
    file: UploadFile = File(...),
    candidate_id: str = Form(...),
    job_id: Optional[str] = Form(None),
    auto_analyze: bool = Form(False),
):
    """
    Upload a resume PDF/DOCX for a candidate.
    Optionally trigger AI analysis immediately if job_id is provided.
    """
    # Validate candidate exists
    candidate = await db["candidates"].find_one({"_id": ObjectId(candidate_id)})
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found",
        )

    if job_id:
        job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    # Save file + extract text
    file_path, raw_text, file_size, page_count = await save_and_extract(file, candidate_id)

    now = datetime.now(timezone.utc)
    doc = {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "filename": file.filename,
        "file_path": file_path,
        "file_size_bytes": file_size,
        "mime_type": file.content_type or "application/pdf",
        "raw_text": raw_text,
        "page_count": page_count,
        "analysis": None,
        "analysis_status": "pending",
        "analysis_error": None,
        "uploaded_by": user_id,
        "created_at": now,
        "updated_at": now,
    }

    result = await db["resumes"].insert_one(doc)
    resume_id = str(result.inserted_id)

    # Update job applicant count
    if job_id:
        await db["jobs"].update_one(
            {"_id": ObjectId(job_id)},
            {"$inc": {"applicant_count": 1}},
        )

    # Run enrichment and analysis in background (non-blocking)
    if raw_text:
        asyncio.create_task(
            enrich_candidate_from_resume(db, candidate_id, raw_text)
        )

    if auto_analyze and job_id:
        asyncio.create_task(run_analysis_pipeline(db, resume_id, job_id))

    return ResumeUploadResponse(
        id=resume_id,
        candidate_id=candidate_id,
        job_id=job_id,
        filename=file.filename or "",
        file_size_bytes=file_size,
        analysis_status="pending" if not auto_analyze else "processing",
        created_at=now,
    )


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str,
    payload: AnalyzeRequest,
    db: DBDep,
    _: CurrentUser,
):
    """Trigger AI analysis of an uploaded resume against a job description."""
    resume = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    if resume.get("analysis_status") == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis already in progress",
        )

    try:
        await run_analysis_pipeline(db, resume_id, payload.job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    updated = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    return _serialize(updated)


@router.post("/bulk-analyze", response_model=dict)
async def bulk_analyze(payload: BulkAnalyzeRequest, db: DBDep, _: CurrentUser):
    """Queue AI analysis for multiple resumes against one job."""
    tasks = []
    for rid in payload.resume_ids:
        tasks.append(
            asyncio.create_task(
                run_analysis_pipeline(db, rid, payload.job_id)
            )
        )

    return {
        "queued": len(tasks),
        "resume_ids": payload.resume_ids,
        "job_id": payload.job_id,
        "message": "Analysis queued. Poll individual resume endpoints for results.",
    }


@router.get("/candidate/{candidate_id}", response_model=ResumeListResponse)
async def get_candidate_resumes(
    candidate_id: str,
    db: DBDep,
    _: CurrentUser,
):
    docs = await db["resumes"].find(
        {"candidate_id": candidate_id}
    ).sort("created_at", -1).to_list(100)

    return ResumeListResponse(items=[_serialize(d) for d in docs], total=len(docs))


@router.get("/{resume_id}", response_model=ResumeAnalysisResponse)
async def get_resume(resume_id: str, db: DBDep, _: CurrentUser):
    doc = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return _serialize(doc)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, db: DBDep, _: CurrentUser):
    doc = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    from app.services.resume_parser import delete_resume_file
    delete_resume_file(doc.get("file_path", ""))

    await db["resumes"].delete_one({"_id": ObjectId(resume_id)})

    # Decrement job applicant count
    if doc.get("job_id"):
        await db["jobs"].update_one(
            {"_id": ObjectId(doc["job_id"])},
            {"$inc": {"applicant_count": -1}},
        )
