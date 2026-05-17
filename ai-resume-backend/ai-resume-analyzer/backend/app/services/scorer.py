import logging
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.groq_service import analyze_resume, extract_candidate_info
from app.models.resume import AIAnalysis

logger = logging.getLogger(__name__)


async def run_analysis_pipeline(
    db: AsyncIOMotorDatabase,
    resume_id: str,
    job_id: str,
) -> AIAnalysis:
    """
    Full pipeline:
    1. Load resume + job from DB
    2. Call GroqCloud for analysis
    3. Persist result back to resume document
    4. Update job's shortlisted_count if hire
    """
    # Load resume
    resume = await db["resumes"].find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise ValueError(f"Resume {resume_id} not found")

    if not resume.get("raw_text"):
        raise ValueError("Resume has no extracted text. Re-upload the file.")

    # Load job
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise ValueError(f"Job {job_id} not found")

    # Mark as processing
    await db["resumes"].update_one(
        {"_id": ObjectId(resume_id)},
        {"$set": {"analysis_status": "processing", "updated_at": datetime.now(timezone.utc)}},
    )

    try:
        analysis = await analyze_resume(
            resume_text=resume["raw_text"],
            job_title=job["title"],
            job_description=job["description"],
            required_skills=job.get("required_skills", []),
            preferred_skills=job.get("preferred_skills", []),
            min_experience=job.get("min_experience_years"),
        )
        analysis.analyzed_at = datetime.now(timezone.utc)

        # Persist analysis result
        await db["resumes"].update_one(
            {"_id": ObjectId(resume_id)},
            {
                "$set": {
                    "job_id": job_id,
                    "analysis": analysis.model_dump(),
                    "analysis_status": "done",
                    "analysis_error": None,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        # Update job stats
        if analysis.recommendation == "hire":
            await db["jobs"].update_one(
                {"_id": ObjectId(job_id)},
                {"$inc": {"shortlisted_count": 1}},
            )

        logger.info(
            f"Analysis complete for resume={resume_id}, score={analysis.overall_score:.1f}"
        )
        return analysis

    except Exception as e:
        logger.error(f"Analysis pipeline failed for resume={resume_id}: {e}")
        await db["resumes"].update_one(
            {"_id": ObjectId(resume_id)},
            {
                "$set": {
                    "analysis_status": "failed",
                    "analysis_error": str(e),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        raise


async def enrich_candidate_from_resume(
    db: AsyncIOMotorDatabase,
    candidate_id: str,
    resume_text: str,
) -> None:
    """
    After a resume upload, auto-fill candidate fields from AI extraction
    if they are currently empty.
    """
    try:
        extracted = await extract_candidate_info(resume_text)

        # Only update fields that are currently null/empty
        candidate = await db["candidates"].find_one({"_id": ObjectId(candidate_id)})
        if not candidate:
            return

        updates: dict = {}
        fill_if_empty = [
            "phone", "location", "linkedin_url", "portfolio_url",
            "current_title", "years_of_experience", "summary",
        ]
        for field in fill_if_empty:
            if not candidate.get(field) and extracted.get(field):
                updates[field] = extracted[field]

        # Always merge skills (union)
        existing_skills = set(candidate.get("skills", []))
        new_skills = set(extracted.get("skills", []))
        merged = list(existing_skills | new_skills)
        if merged != candidate.get("skills", []):
            updates["skills"] = merged

        # Overwrite experience & education if they were empty
        if not candidate.get("experience") and extracted.get("experience"):
            updates["experience"] = extracted["experience"]
        if not candidate.get("education") and extracted.get("education"):
            updates["education"] = extracted["education"]

        if updates:
            updates["updated_at"] = datetime.now(timezone.utc)
            await db["candidates"].update_one(
                {"_id": ObjectId(candidate_id)},
                {"$set": updates},
            )
            logger.info(
                f"Enriched candidate {candidate_id} with {len(updates)} fields from resume"
            )

    except Exception as e:
        # Non-fatal - enrichment is a bonus, not required
        logger.warning(f"Candidate enrichment failed for {candidate_id}: {e}")
