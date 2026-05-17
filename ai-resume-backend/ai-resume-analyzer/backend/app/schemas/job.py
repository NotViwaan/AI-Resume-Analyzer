from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    location: str
    employment_type: str = "full_time"
    work_mode: str = "onsite"
    description: str
    responsibilities: List[str] = []
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    education_requirement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    benefits: List[str] = []
    status: str = "open"
    deadline: Optional[datetime] = None
    headcount: int = 1


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_experience_years: Optional[float] = None
    max_experience_years: Optional[float] = None
    education_requirement: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    benefits: Optional[List[str]] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    headcount: Optional[int] = None


class JobResponse(BaseModel):
    id: str
    title: str
    department: Optional[str]
    location: str
    employment_type: str
    work_mode: str
    description: str
    responsibilities: List[str]
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: Optional[float]
    max_experience_years: Optional[float]
    education_requirement: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    benefits: List[str]
    status: str
    deadline: Optional[datetime]
    headcount: int
    applicant_count: int
    shortlisted_count: int
    hired_count: int
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
