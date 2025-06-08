from fastapi import APIRouter, HTTPException, Request
from ..models.schemas import AnalysisRequest, AnalysisResponse, EnhancedResumeRequest, EnhancedResumeResponse
from ..services.openai_service import analyze_resume, generate_enhanced_resume, generate_improvement_summary
from ..services.pdf_service import generate_pdf_from_text
from ..utils.response_parser import parse_ai_response
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from ..core.config import PDF_OUTPUT_DIR, BASE_BACKEND_URL

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/analyze/", response_model=AnalysisResponse)
@limiter.limit("5/minute")
async def analyze_resume_and_job_description(request: Request, request_data: AnalysisRequest):
    """Analyze resume against job description."""
    print("=== Starting analyze_resume_and_job_description ===")
    print(f"Request data received: {request_data}")
    
    if not request_data.resume_text or not request_data.job_description_text:
        print("Error: Empty resume or job description")
        raise HTTPException(status_code=400, detail="Resume text and job description text cannot be empty.")

    try:
        print("Calling analyze_resume function...")
        # Get AI analysis
        ai_response_text = analyze_resume(request_data.resume_text, request_data.job_description_text)
        print("Successfully got response from analyze_resume")
        
        print("Parsing response...")
        # Parse the response
        parsed_response = parse_ai_response(ai_response_text)
        print("Successfully parsed response")

        return AnalysisResponse(
            compatibility_score=parsed_response["compatibility_score"],
            improvement_summary=parsed_response["improvement_summary"],
            matched_keywords=parsed_response["matched_keywords"],
            missing_keywords=parsed_response["missing_keywords"]
        )

    except Exception as e:
        print("=== ERROR OCCURRED ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print("Full traceback:")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during analysis: {str(e)}")

@router.post("/enhance-resume/", response_model=EnhancedResumeResponse)
@limiter.limit("5/minute")
async def enhance_resume(request: Request, request_data: EnhancedResumeRequest):
    """Generate an enhanced resume in PDF format based on the job description."""
    if not request_data.job_description_text:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")
    
    if not request_data.resume_text:
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")
    
    try:
        # Enhance the resume based on job description and improvement suggestions
        enhanced_resume_text = generate_enhanced_resume(
            request_data.resume_text, 
            request_data.job_description_text,
            request_data.improvement_suggestions
        )
        
        # Generate improvement summary
        improvement_summary = generate_improvement_summary(
            request_data.resume_text,
            enhanced_resume_text,
            request_data.job_description_text
        )
        
        # Generate PDF from enhanced resume text
        pdf_filename = generate_pdf_from_text(
            enhanced_resume_text,
            request_data.applicant_name,
            request_data.contact_info,
            request_data.github_link,
            request_data.linkedin_link,
            request_data.portfolio_link
        )
        
        # Create a fully qualified URL for the PDF
        pdf_url = f"{BASE_BACKEND_URL}/download-pdf/{pdf_filename}"
        print(f"Generated PDF URL: {pdf_url}")
        
        return EnhancedResumeResponse(
            pdf_url=pdf_url,
            improvement_summary=improvement_summary
        )
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during resume enhancement: {str(e)}")

@router.get("/download-pdf/{filename}")
@limiter.limit("5/minute")
async def download_pdf(request: Request, filename: str):
    """Download a generated PDF file."""
    filepath = os.path.join(PDF_OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        filepath, 
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Allow-Origin": "*",  # Add CORS header
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    ) 