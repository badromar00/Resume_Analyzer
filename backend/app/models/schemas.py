from pydantic import BaseModel
from typing import Optional, List

class AnalysisRequest(BaseModel):
    resume_text: str
    job_description_text: str

class AnalysisResponse(BaseModel):
    compatibility_score: float
    improvement_summary: str
    matched_keywords: List[str]
    missing_keywords: List[str]

class EnhancedResumeRequest(BaseModel):
    resume_text: str
    job_description_text: str
    applicant_name: str
    contact_info: str
    github_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    portfolio_link: Optional[str] = None
    improvement_suggestions: Optional[str] = None

class EnhancedResumeResponse(BaseModel):
    pdf_url: str
    improvement_summary: str 