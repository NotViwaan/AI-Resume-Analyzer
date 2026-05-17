from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional
from app.core.dependencies import DBDep, CurrentUser, CurrentUserID
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _serialize(doc: dict) -> JobResponse:
    return JobResponse(
        id=str(doc["_id"]),
        title=doc["title"],
        department=doc.get("department"),
        location=doc["location"],
        employment_type=doc.get("employment_type", "full_time"),
        work_mode=doc.get("work_mode", "onsite"),
        description=doc["description"],
        responsibilities=doc.get("responsibilities", []),
        required_skills=doc.get("required_skills", []),
        preferred_skills=doc.get("preferred_skills", []),
        min_experience_years=doc.get("min_experience_years"),
        max_experience_years=doc.get("max_experience_years"),
        education_requirement=doc.get("education_requirement"),
        salary_min=doc.get("salary_min"),
        salary_max=doc.get("salary_max"),
        salary_currency=doc.get("salary_currency", "USD"),
        benefits=doc.get("benefits", []),
        status=doc.get("status", "open"),
        deadline=doc.get("deadline"),
        headcount=doc.get("headcount", 1),
        applicant_count=doc.get("applicant_count", 0),
        shortlisted_count=doc.get("shortlisted_count", 0),
        hired_count=doc.get("hired_count", 0),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: DBDep,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    work_mode: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: int = Query(-1),
):
    query: dict = {}
    if search:
        query["$text"] = {"$search": search}
    if status:
        query["status"] = status
    if work_mode:
        query["work_mode"] = work_mode

    total = await db["jobs"].count_documents(query)
    cursor = (
        db["jobs"]
        .find(query)
        .sort(sort_by, sort_dir)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    docs = await cursor.to_list(page_size)

    return JobListResponse(
        items=[_serialize(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(payload: JobCreate, db: DBDep, user_id: CurrentUserID):
    now = datetime.now(timezone.utc)
    doc = {
        **payload.model_dump(),
        "applicant_count": 0,
        "shortlisted_count": 0,
        "hired_count": 0,
        "created_by": user_id,
        "created_at": now,
        "updated_at": now,
    }
    result = await db["jobs"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: DBDep, _: CurrentUser):
    doc = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _serialize(doc)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, payload: JobUpdate, db: DBDep, _: CurrentUser):
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    result = await db["jobs"].find_one_and_update(
        {"_id": ObjectId(job_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _serialize(result)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, db: DBDep, _: CurrentUser):
    result = await db["jobs"].delete_one({"_id": ObjectId(job_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")


@router.get("/{job_id}/candidates", response_model=dict)
async def get_job_candidates(
    job_id: str,
    db: DBDep,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_score: Optional[float] = Query(None),
):
    """Get all candidates who applied to a specific job, sorted by AI score."""
    query: dict = {"job_id": job_id, "analysis_status": "done"}
    if min_score is not None:
        query["analysis.overall_score"] = {"$gte": min_score}

    total = await db["resumes"].count_documents(query)
    pipeline = [
        {"$match": query},
        {"$sort": {"analysis.overall_score": -1}},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size},
        {
            "$lookup": {
                "from": "candidates",
                "let": {"cid": "$candidate_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {"$eq": [{"$toString": "$_id"}, "$$cid"]}
                        }
                    }
                ],
                "as": "candidate",
            }
        },
        {"$unwind": "$candidate"},
    ]
    docs = await db["resumes"].aggregate(pipeline).to_list(page_size)

    results = []
    for doc in docs:
        c = doc["candidate"]
        results.append({
            "resume_id": str(doc["_id"]),
            "candidate_id": str(c["_id"]),
            "name": f"{c['first_name']} {c['last_name']}",
            "email": c["email"],
            "current_title": c.get("current_title"),
            "status": c.get("status", "new"),
            "ai_score": doc.get("analysis", {}).get("overall_score"),
            "recommendation": doc.get("analysis", {}).get("recommendation"),
            "analysis_status": doc["analysis_status"],
        })

    return {
        "items": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
