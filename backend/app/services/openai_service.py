# app/services/openai_service.py
import openai
from fastapi import HTTPException
from ..core.config import OPENAI_API_KEY
import traceback
import os

print("=== Initializing OpenAI Service ===")
print(f"OpenAI SDK version: {openai.__version__}")
print(f"OPENAI_API_KEY from environment: {os.getenv('OPENAI_API_KEY')[:10] if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"OPENAI_API_KEY from config: {OPENAI_API_KEY[:10] if OPENAI_API_KEY else 'Not set'}")

# Initialize OpenAI client
try:
    print("Attempting to initialize OpenAI client...")
    openai.api_key = OPENAI_API_KEY
    print("OpenAI client initialized successfully")
except Exception as e:
    print("=== ERROR INITIALIZING OPENAI CLIENT ===")
    print(f"Error type: {type(e)}")
    print(f"Error message: {str(e)}")
    print("Full traceback:")
    print(traceback.format_exc())
    raise HTTPException(status_code=503, detail="OpenAI client not initialized. API key might be missing or invalid.")

def analyze_resume(resume_text: str, job_description_text: str):
    """Analyze resume against job description using OpenAI."""
    print("=== Starting analyze_resume ===")
    if not openai.api_key:
        print("OpenAI API key is not set")
        raise HTTPException(status_code=503, detail="OpenAI API key is not set.")

    system_prompt = (
        "You are an expert resume analyzer and career coach. "
        "Your task is to analyze a candidate's resume against a provided job description, "
        "with special attention to years of experience requirements. "
        "Provide a compatibility score and actionable improvement suggestions, "
        "including specific guidance about experience gaps if they exist.\n\n"
        "SCORING FORMULA:\n"
        "1. Keyword Matching (40% of total score):\n"
        "   - Required Skills Match (25%):\n"
        "     * Each required skill found in resume = +5 points\n"
        "     * Maximum 25 points for required skills\n"
        "   - Preferred Skills Match (15%):\n"
        "     * Each preferred skill found in resume = +3 points\n"
        "     * Maximum 15 points for preferred skills\n\n"
        "2. Experience Level Match (30% of total score):\n"
        "   - Years of Experience (15%):\n"
        "     * If resume meets or exceeds required years = 15 points\n"
        "     * If within 1 year of requirement = 10 points\n"
        "     * If within 2 years = 5 points\n"
        "     * If more than 2 years below = 0 points\n"
        "   - Role Level Match (15%):\n"
        "     * Senior/Lead roles match = 15 points\n"
        "     * Mid-level roles match = 10 points\n"
        "     * Junior roles match = 5 points\n\n"
        "3. Education Match (15% of total score):\n"
        "   - Required Degree Match = 15 points\n"
        "   - Preferred Degree Match = 10 points\n"
        "   - Related Degree = 5 points\n\n"
        "4. Achievement Quantification (15% of total score):\n"
        "   - Each quantified achievement = +3 points\n"
        "   - Maximum 15 points\n"
        "   - Must have specific numbers/metrics\n\n"
        "Calculate the final score by adding all points and converting to a percentage.\n\n"
        "Provide your analysis in this exact format:\n"
        "Score: [calculated percentage]%\n"
        "Score Breakdown:\n"
        "- Required Skills: [X/25 points]\n"
        "- Preferred Skills: [X/15 points]\n"
        "- Experience Years: [X/15 points]\n"
        "- Role Level: [X/15 points]\n"
        "- Education: [X/15 points]\n"
        "- Achievements: [X/15 points]\n\n"
        "Summary:\n"
        "- [Suggestion 1]\n"
        "- [Suggestion 2]\n"
        "- [Suggestion 3]\n"
        "- [Suggestion 4]\n"
        "- [Suggestion 5]\n\n"
        "Matched Keywords:\n"
        "- [keyword1]\n"
        "- [keyword2]\n"
        "- [keyword3]\n\n"
        "Missing Keywords:\n"
        "- [keyword1]\n"
        "- [keyword2]\n"
        "- [keyword3]\n"
    )
    
    user_prompt = f"""
    Please analyze the following resume and job description:

    **Job Description:**
    ---
    {job_description_text}
    ---

    **Resume:**
    ---
    {resume_text}
    ---

    Based on this analysis, provide:
    1. A compatibility score as a percentage (e.g., "Score: 85%"). The score should reflect how well the resume matches the job description's requirements and desired qualifications.
    2. A concise summary of 5-7 bullet-pointed improvement suggestions. These suggestions should be actionable and specific to enhancing the resume for this particular job description. Focus on:
       - Missing keywords and skills to highlight
       - Experiences to rephrase or emphasize
       - If years of experience don't meet requirements, include this specific suggestion:
         "Your experience is less than the role requires. If you're confident you can perform the job and meet other criteria, consider applying. Include a strong summary explaining why you're a great fit despite having fewer years of experience. Be aware that experience is often an initial screening factor."
    3. List of matched keywords found in both resume and job description
    4. List of important keywords from job description that are missing in the resume

    Format your response as:
    Score: [percentage]%
    Summary:
    - Suggestion 1
    - Suggestion 2
    - ...

    Matched Keywords:
    - keyword1
    - keyword2
    - ...

    Missing Keywords:
    - keyword1
    - keyword2
    - ...

    Ensure your entire response strictly follows this format. Do not add any extra conversational text or introductions beyond the requested sections.
    """

    try:
        print("Preparing to call OpenAI API...")
        print(f"Resume text length: {len(resume_text)}")
        print(f"Job description length: {len(job_description_text)}")
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4095
        )
        print("OpenAI API call completed successfully")
        return response.choices[0].message.content

    except Exception as e:
        print("=== ERROR IN OPENAI ANALYSIS ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

def generate_enhanced_resume(resume_text: str, job_description: str, improvement_suggestions: str = None):
    """Enhance a resume based on a job description using OpenAI."""
    if not openai.api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key is not set.")

    system_prompt = (
        "You are an expert resume writer with 15+ years of experience helping job seekers optimize their resumes. "
        "Your task is to enhance a candidate's resume to better match a specific job description. "
        "You should maintain the candidate's original experience and qualifications, but improve the wording, "
        "emphasis, and relevance to better align with the target job description. "
        "IMPORTANT RULES:\n"
        "1. STRICT RULE: Only include languages and certifications that were EXPLICITLY mentioned in the original resume. "
        "   DO NOT add new ones, even if they seem relevant to the job.\n"
        "2. Format the enhanced resume with clear section headers and proper spacing.\n"
        "3. Each section should be separated by two newlines, and each bullet point should be on its own line.\n"
        "4. For work experience and project bullet points:\n"
        "   - ALWAYS add specific numbers and metrics, even if not in the original resume\n"
        "   - Use industry-standard metrics that would be believable for the role\n"
        "   - Examples of quantification:\n"
        "     * For development: 'reduced load time by 40%', 'decreased bug reports by 25%'\n"
        "     * For management: 'led team of 5 developers', 'managed $500K project budget'\n"
        "     * For sales: 'increased revenue by 30%', 'expanded client base by 50%'\n"
        "     * For operations: 'improved efficiency by 35%', 'reduced costs by 20%'\n"
        "   - Use strong action verbs at the start of each bullet point\n"
        "   - Keep bullet points concise but impactful\n"
        "5. Professional Summary must be concise and impactful, limited to 3 lines maximum.\n"
        "6. Use bullet points (•) for ALL items within sections, including:\n"
        "   - Each work experience entry\n"
        "   - Each project entry\n"
        "   - Each education entry\n"
        "   - Each skill category\n"
        "   - Each language\n"
        "   - Each certification\n"
        "   - Each interest\n"
        "7. Use this exact format:\n\n"
        "Professional Summary:\n"
        "[3-line maximum summary highlighting key qualifications and achievements]\n\n"
        "Work Experience:\n"
        "• [Job Title] (Location, Date Range)\n"
        "  - [Achievement with numbers/metrics]\n"
        "  - [Achievement with numbers/metrics]\n\n"
        "Education:\n"
        "• [Degree] (School, Location, Date)\n\n"
        "Skills:\n"
        "• [Skill Category]: [Skill 1], [Skill 2], [Skill 3]\n\n"
        "Projects:\n"
        "• [Project Name] (Technologies, Date)\n"
        "  - [Achievement with numbers/metrics]\n"
        "  - [Achievement with numbers/metrics]\n\n"
        "Languages:\n"
        "• [Language 1] (Proficiency), [Language 2] (Proficiency)\n\n"
        "Certifications:\n"
        "• [Certification 1], [Certification 2]\n\n"
        "Interests:\n"
        "• [Interest 1], [Interest 2], [Interest 3]\n\n"
        "Maintain consistent formatting throughout. "
        "For skills, languages, certifications, and interests, place multiple items on the same line separated by commas."
    )
    
    improvement_context = ""
    if improvement_suggestions:
        improvement_context = f"""
        Additionally, please specifically address these improvement suggestions in your enhancement:
        {improvement_suggestions}
        """
    
    user_prompt = f"""
    Please enhance the following resume to better match this specific job description:

    **Job Description:**
    ```
    {job_description}
    ```

    **Original Resume:**
    ```
    {resume_text}
    ```

    Please create an enhanced version of this resume that:
    1. Maintains the candidate's actual experience and education
    2. Incorporates relevant keywords from the job description
    3. Emphasizes transferable skills relevant to the position
    4. CRITICAL: Add specific numbers and metrics to ALL achievements, even if not in the original resume:
       - Use industry-standard metrics that would be believable for the role
       - Quantify everything: time saved, money saved, efficiency improved, team size, project scope
       - Make numbers realistic and specific to the industry and role
       - If original achievement lacks numbers, add reasonable metrics based on typical industry standards
    5. Uses stronger action verbs at the start of each bullet point, and make sure to rewrite the bullet points to be more impactful
    6. Updates the summary to better match the job requirements
    7. Follows the exact formatting template provided in the system prompt
    8. Uses bullet points (•) for main items and dashes (-) for sub-items
    9. Includes all relevant sections with proper spacing and formatting
    10. Groups multiple skills, languages, certifications, and interests on the same line separated by commas
    11. STRICT: Only include languages and certifications that were EXPLICITLY mentioned in the original resume
    {improvement_context}
    
    Return the enhanced resume in a clear, well-formatted text structure with proper section headers, bullet points, and spacing.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )

        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error enhancing resume: {e}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error enhancing resume: {str(e)}")

def generate_improvement_summary(original_resume: str, enhanced_resume: str, job_description: str):
    """Generate a summary of improvements made to the resume."""
    if not openai.api_key:
        raise HTTPException(status_code=503, detail="OpenAI API key is not set.")

    system_prompt = (
        "You are an expert resume writer with 15+ years of experience helping job seekers optimize their resumes. "
        "Your task is to explain the improvements made to a candidate's resume for a specific job position."
    )
    
    user_prompt = f"""
    Compare the original resume and enhanced resume below, and explain the key improvements made to better match the job description.

    **Job Description:**
    ```
    {job_description}
    ```

    **Original Resume:**
    ```
    {original_resume}
    ```

    **Enhanced Resume:**
    ```
    {enhanced_resume}
    ```

    Provide a summary of 5-7 bullet points explaining the key improvements made and why they matter for this specific job.
    Your response should be in Markdown format with bullet points.
    Start your response with "## Improvement Summary" and then list the improvements as bullet points.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1500
        )

        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error generating improvement summary: {e}")
        print("Full traceback:")
        print(traceback.format_exc())
        return "## Improvement Summary\n- Enhanced resume to better match job requirements\n- Highlighted relevant skills and experiences\n- Used stronger action verbs\n- Added quantifiable achievements where possible\n- Aligned summary with job description"