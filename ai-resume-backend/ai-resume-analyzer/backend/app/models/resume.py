from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models._base import PyObjectId


class SkillMatch(BaseModel):
    skill: str
    matched: bool
    proficiency: Optional[str] = None   # beginner | intermediate | expert


class AIAnalysis(BaseModel):
    """Structured result from GroqCloud analysis."""
    overall_score: float = 0.0          # 0-100
    skill_match_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    communication_score: float = 0.0    # based on writing quality

    # Matched skills breakdown
    matched_skills: List[SkillMatch] = []
    missing_skills: List[str] = []
    bonus_skills: List[str] = []        # skills not required but impressive

    # Narrative feedback
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str = ""            # hire | maybe | reject
    recommendation_reason: str = ""
    interview_questions: List[str] = [] # AI-generated screening questions

    # Red flags
    red_flags: List[str] = []
    employment_gaps: bool = False

    analyzed_at: Optional[datetime] = None


class ResumeModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    # Relations
    candidate_id: str
    job_id: Optional[str] = None        # None = general resume, not for a specific job

    # File info
    filename: str
    file_path: str                       # server-side path or S3 key
    file_size_bytes: int
    mime_type: str = "application/pdf"

    # Extracted content
    raw_text: Optional[str] = None      # full text extracted from PDF
    page_count: Optional[int] = None

    # AI analysis result
    analysis: Optional[AIAnalysis] = None
    analysis_status: str = "pending"    # pending | processing | done | failed
    analysis_error: Optional[str] = None

    # Metadata
    uploaded_by: Optional[str] = None   # user_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }

    @property
    def ai_score(self) -> Optional[float]:
        return self.analysis.overall_score if self.analysis else None
