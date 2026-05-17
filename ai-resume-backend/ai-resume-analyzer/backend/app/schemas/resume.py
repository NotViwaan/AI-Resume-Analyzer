from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.resume import AIAnalysis, SkillMatch


class ResumeUploadResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: Optional[str]
    filename: str
    file_size_bytes: int
    analysis_status: str
    created_at: datetime


class ResumeAnalysisResponse(BaseModel):
    id: str
    candidate_id: str
    job_id: Optional[str]
    filename: str
    analysis_status: str
    analysis: Optional[AIAnalysis]
    created_at: datetime
    updated_at: datetime


class AnalyzeRequest(BaseModel):
    """Trigger (re-)analysis of an already-uploaded resume against a job."""
    job_id: str


class BulkAnalyzeRequest(BaseModel):
    resume_ids: List[str]
    job_id: str


class ResumeListResponse(BaseModel):
    items: List[ResumeAnalysisResponse]
    total: int
