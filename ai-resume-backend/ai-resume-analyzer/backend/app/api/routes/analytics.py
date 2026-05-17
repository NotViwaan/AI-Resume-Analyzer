from fastapi import APIRouter, Query
from datetime import datetime, timezone, timedelta
from app.core.dependencies import DBDep, CurrentUser

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_overview(db: DBDep, _: CurrentUser):
    """Top-level KPI cards for the recruiter dashboard."""
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    # Run all counts concurrently
    import asyncio
    (
        total_candidates,
        total_jobs_open,
        total_resumes,
        candidates_this_month,
        shortlisted,
        hired,
        avg_score_result,
    ) = await asyncio.gather(
        db["candidates"].count_documents({}),
        db["jobs"].count_documents({"status": "open"}),
        db["resumes"].count_documents({}),
        db["candidates"].count_documents({"created_at": {"$gte": thirty_days_ago}}),
        db["candidates"].count_documents({"status": "shortlisted"}),
        db["candidates"].count_documents({"status": "hired"}),
        db["resumes"].aggregate([
            {"$match": {"analysis_status": "done"}},
            {"$group": {"_id": None, "avg": {"$avg": "$analysis.overall_score"}}},
        ]).to_list(1),
    )

    avg_score = avg_score_result[0]["avg"] if avg_score_result else 0.0

    return {
        "total_candidates": total_candidates,
        "open_jobs": total_jobs_open,
        "total_resumes_analyzed": total_resumes,
        "new_candidates_this_month": candidates_this_month,
        "shortlisted": shortlisted,
        "hired": hired,
        "average_ai_score": round(avg_score, 1),
        "shortlist_rate": round((shortlisted / total_candidates * 100) if total_candidates else 0, 1),
        "hire_rate": round((hired / total_candidates * 100) if total_candidates else 0, 1),
    }


@router.get("/pipeline-funnel")
async def get_pipeline_funnel(db: DBDep, _: CurrentUser):
    """Hiring funnel stages: total → reviewed → shortlisted → hired."""
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
            }
        }
    ]
    results = await db["candidates"].aggregate(pipeline).to_list(20)
    counts = {r["_id"]: r["count"] for r in results}

    order = ["new", "reviewing", "shortlisted", "hired", "rejected"]
    funnel = [{"stage": s, "count": counts.get(s, 0)} for s in order]
    return {"funnel": funnel}


@router.get("/score-distribution")
async def get_score_distribution(
    db: DBDep,
    _: CurrentUser,
    job_id: str = Query(None),
):
    """Histogram of AI scores in buckets of 10."""
    match: dict = {"analysis_status": "done"}
    if job_id:
        match["job_id"] = job_id

    pipeline = [
        {"$match": match},
        {
            "$bucket": {
                "groupBy": "$analysis.overall_score",
                "boundaries": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                "default": "other",
                "output": {"count": {"$sum": 1}},
            }
        },
    ]
    results = await db["resumes"].aggregate(pipeline).to_list(20)
    return {"distribution": results}


@router.get("/hiring-trend")
async def get_hiring_trend(
    db: DBDep,
    _: CurrentUser,
    days: int = Query(90, ge=7, le=365),
):
    """Daily candidate intake + hired count over the past N days."""
    start = datetime.now(timezone.utc) - timedelta(days=days)

    pipeline = [
        {"$match": {"created_at": {"$gte": start}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"},
                },
                "total": {"$sum": 1},
                "hired": {
                    "$sum": {"$cond": [{"$eq": ["$status", "hired"]}, 1, 0]}
                },
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
    ]

    results = await db["candidates"].aggregate(pipeline).to_list(days)
    trend = [
        {
            "date": f"{r['_id']['year']}-{r['_id']['month']:02d}-{r['_id']['day']:02d}",
            "total": r["total"],
            "hired": r["hired"],
        }
        for r in results
    ]
    return {"trend": trend, "days": days}


@router.get("/top-skills")
async def get_top_skills(db: DBDep, _: CurrentUser, limit: int = Query(15, ge=5, le=50)):
    """Most common skills across all candidates."""
    pipeline = [
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    results = await db["candidates"].aggregate(pipeline).to_list(limit)
    return {"skills": [{"skill": r["_id"], "count": r["count"]} for r in results]}


@router.get("/jobs-performance")
async def get_jobs_performance(db: DBDep, _: CurrentUser):
    """Per-job stats: applicants, shortlisted, avg score."""
    pipeline = [
        {"$match": {"status": {"$in": ["open", "paused"]}}},
        {
            "$lookup": {
                "from": "resumes",
                "let": {"jid": {"$toString": "$_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$job_id", "$$jid"]}}},
                    {
                        "$group": {
                            "_id": None,
                            "count": {"$sum": 1},
                            "avg_score": {"$avg": "$analysis.overall_score"},
                            "hire_recommendations": {
                                "$sum": {
                                    "$cond": [
                                        {"$eq": ["$analysis.recommendation", "hire"]},
                                        1, 0,
                                    ]
                                }
                            },
                        }
                    },
                ],
                "as": "stats",
            }
        },
        {
            "$project": {
                "title": 1,
                "status": 1,
                "applicant_count": 1,
                "hired_count": 1,
                "resume_count": {"$ifNull": [{"$arrayElemAt": ["$stats.count", 0]}, 0]},
                "avg_score": {"$ifNull": [{"$arrayElemAt": ["$stats.avg_score", 0]}, 0]},
                "hire_recommendations": {
                    "$ifNull": [{"$arrayElemAt": ["$stats.hire_recommendations", 0]}, 0]
                },
            }
        },
        {"$sort": {"applicant_count": -1}},
        {"$limit": 10},
    ]

    results = await db["jobs"].aggregate(pipeline).to_list(10)
    return {
        "jobs": [
            {
                "id": str(r["_id"]),
                "title": r["title"],
                "status": r["status"],
                "applicant_count": r.get("applicant_count", 0),
                "resume_count": r.get("resume_count", 0),
                "avg_score": round(r.get("avg_score") or 0, 1),
                "hire_recommendations": r.get("hire_recommendations", 0),
                "hired_count": r.get("hired_count", 0),
            }
            for r in results
        ]
    }
