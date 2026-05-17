from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field
from app.models._base import PyObjectId


class ExperienceEntry(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None   # None = "present"
    description: Optional[str] = None
    location: Optional[str] = None


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class CandidateModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    # Personal info
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Professional profile
    current_title: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: List[str] = []
    languages: List[str] = []

    # Structured resume data (AI-extracted)
    experience: List[ExperienceEntry] = []
    education: List[EducationEntry] = []
    summary: Optional[str] = None

    # Pipeline status
    status: str = "new"              # new | reviewing | shortlisted | rejected | hired
    tags: List[str] = []
    notes: Optional[str] = None      # recruiter notes

    # Metadata
    source: str = "manual"           # manual | upload | linkedin
    created_by: Optional[str] = None # user_id of recruiter
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }
