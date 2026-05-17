from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models._base import PyObjectId


class JobModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    # Core info
    title: str
    department: Optional[str] = None
    location: str
    employment_type: str = "full_time"  # full_time | part_time | contract | internship
    work_mode: str = "onsite"           # onsite | remote | hybrid
    description: str
    responsibilities: List[str] = []

    # Requirements
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    education_requirement: Optional[str] = None  # "Bachelor's" | "Master's" | "PhD" | "Any"

    # Compensation
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    benefits: List[str] = []

    # Pipeline
    status: str = "open"             # draft | open | paused | closed
    deadline: Optional[datetime] = None
    headcount: int = 1               # number of openings

    # Stats (denormalized for quick dashboard reads)
    applicant_count: int = 0
    shortlisted_count: int = 0
    hired_count: int = 0

    # Metadata
    created_by: Optional[str] = None  # user_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
