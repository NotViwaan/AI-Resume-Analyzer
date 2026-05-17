from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.candidate import ExperienceEntry, EducationEntry


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: List[str] = []
    tags: List[str] = []
    notes: Optional[str] = None
    source: str = "manual"


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    current_title: Optional[str] = None
    years_of_experience: Optional[float] = None
    skills: Optional[List[str]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class CandidateResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    current_title: Optional[str]
    years_of_experience: Optional[float]
    skills: List[str]
    languages: List[str]
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    summary: Optional[str]
    status: str
    tags: List[str]
    notes: Optional[str]
    source: str
    created_at: datetime
    updated_at: datetime
    # Enriched fields (joined from resumes collection)
    latest_score: Optional[float] = None
    resume_count: Optional[int] = None


class CandidateListResponse(BaseModel):
    items: List[CandidateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatusUpdate(BaseModel):
    status: str  # new | reviewing | shortlisted | rejected | hired
