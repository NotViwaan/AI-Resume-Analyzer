from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional
from app.core.dependencies import DBDep, CurrentUser, CurrentUserID
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse,
    StatusUpdate,
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


def _serialize(doc: dict) -> CandidateResponse:
    return CandidateResponse(
        id=str(doc["_id"]),
        first_name=doc["first_name"],
        last_name=doc["last_name"],
        email=doc["email"],
        phone=doc.get("phone"),
        location=doc.get("location"),
        linkedin_url=doc.get("linkedin_url"),
        portfolio_url=doc.get("portfolio_url"),
        current_title=doc.get("current_title"),
        years_of_experience=doc.get("years_of_experience"),
        skills=doc.get("skills", []),
        languages=doc.get("languages", []),
        experience=doc.get("experience", []),
        education=doc.get("education", []),
        summary=doc.get("summary"),
        status=doc.get("status", "new"),
        tags=doc.get("tags", []),
        notes=doc.get("notes"),
        source=doc.get("source", "manual"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        latest_score=doc.get("latest_score"),
        resume_count=doc.get("resume_count"),
    )


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    db: DBDep,
    _: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    sort_by: str = Query("created_at"),
    sort_dir: int = Query(-1, description="-1 desc, 1 asc"),
):
    query: dict = {}

    if search:
        query["$text"] = {"$search": search}

    if status:
        query["status"] = status

    if skills:
        skill_list = [s.strip() for s in skills.split(",")]
        query["skills"] = {"$all": skill_list}

    # Join latest score from resumes collection using aggregation
    pipeline = [
        {"$match": query},
        {
            "$lookup": {
                "from": "resumes",
                "let": {"cid": {"$toString": "$_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$candidate_id", "$$cid"]}}},
                    {"$sort": {"analysis.overall_score": -1}},
                    {"$limit": 1},
                    {"$project": {"_id": 0, "score": "$analysis.overall_score"}},
                ],
                "as": "resume_data",
            }
        },
        {
            "$addFields": {
                "latest_score": {"$arrayElemAt": ["$resume_data.score", 0]},
                "resume_count": {"$size": "$resume_data"},
            }
        },
        {"$unset": "resume_data"},
    ]

    if min_score is not None:
        pipeline.append({"$match": {"latest_score": {"$gte": min_score}}})

    # Count total (before pagination)
    count_pipeline = pipeline + [{"$count": "total"}]
    count_result = await db["candidates"].aggregate(count_pipeline).to_list(1)
    total = count_result[0]["total"] if count_result else 0

    # Sort + paginate
    pipeline += [
        {"$sort": {sort_by: sort_dir}},
        {"$skip": (page - 1) * page_size},
        {"$limit": page_size},
    ]

    docs = await db["candidates"].aggregate(pipeline).to_list(page_size)

    return CandidateListResponse(
        items=[_serialize(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    db: DBDep,
    user_id: CurrentUserID,
):
    existing = await db["candidates"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate with this email already exists",
        )

    now = datetime.now(timezone.utc)
    doc = {
        **payload.model_dump(),
        "languages": [],
        "experience": [],
        "education": [],
        "summary": None,
        "created_by": user_id,
        "created_at": now,
        "updated_at": now,
    }

    result = await db["candidates"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str, db: DBDep, _: CurrentUser):
    doc = await db["candidates"].find_one({"_id": ObjectId(candidate_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return _serialize(doc)


@router.patch("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    payload: CandidateUpdate,
    db: DBDep,
    _: CurrentUser,
):
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    result = await db["candidates"].find_one_and_update(
        {"_id": ObjectId(candidate_id)},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return _serialize(result)


@router.patch("/{candidate_id}/status", response_model=CandidateResponse)
async def update_status(
    candidate_id: str,
    payload: StatusUpdate,
    db: DBDep,
    _: CurrentUser,
):
    valid_statuses = {"new", "reviewing", "shortlisted", "rejected", "hired"}
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Choose from: {valid_statuses}",
        )

    result = await db["candidates"].find_one_and_update(
        {"_id": ObjectId(candidate_id)},
        {"$set": {"status": payload.status, "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return _serialize(result)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(candidate_id: str, db: DBDep, _: CurrentUser):
    result = await db["candidates"].delete_one({"_id": ObjectId(candidate_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    # Cascade delete resumes
    await db["resumes"].delete_many({"candidate_id": candidate_id})
