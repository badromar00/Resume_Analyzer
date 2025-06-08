import os
import uuid
import base64
import requests
from fastapi import HTTPException
from ..core.config import DOCRAPTOR_API_KEY, PDF_OUTPUT_DIR

def create_resume_html(resume_text: str, applicant_name: str, contact_info: str, github_link: str = None, linkedin_link: str = None, portfolio_link: str = None) -> str:
    """Create a modern, minimalist HTML template for the resume."""
    # Parse contact info
    contact_parts = contact_info.split('|')
    email = contact_parts[0].strip() if len(contact_parts) > 0 else ""
    phone = contact_parts[1].strip() if len(contact_parts) > 1 else ""
    location = contact_parts[2].strip() if len(contact_parts) > 2 else ""
    
    # Create social links HTML
    social_links = []
    if github_link:
        social_links.append(f'<a href="{github_link}" target="_blank"><i class="icon">💻</i> GitHub</a>')
    if linkedin_link:
        social_links.append(f'<a href="{linkedin_link}" target="_blank"><i class="icon">💼</i> LinkedIn</a>')
    if portfolio_link:
        social_links.append(f'<a href="{portfolio_link}" target="_blank"><i class="icon">🌐</i> Portfolio</a>')
    
    # Create a single line for contact info and social links
    contact_items = []
    if email:
        contact_items.append(f'<div><i>📧</i> {email}</div>')
    if phone:
        contact_items.append(f'<div><i>📞</i> {phone}</div>')
    if location:
        contact_items.append(f'<div><i>📍</i> {location}</div>')
    
    # Add social links to the same line
    contact_items.extend(social_links)
    
    header_content_html = f'<div class="header-content">{" | ".join(contact_items)}</div>' if contact_items else ""
    
    # Split the resume text into sections
    sections = {}
    current_section = None
    current_content = []
    
    # Process line by line for better section detection
    lines = resume_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header (ends with : and has no bullet points)
        if line.endswith(':') and not line.startswith('•') and not line.startswith('-'):
            # Save previous section if exists
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line.rstrip(':').lower()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
            else:
                # If no section header found yet, treat as professional summary
                if not 'professional summary' in sections:
                    sections['professional summary'] = line
                    current_section = 'professional summary'
                else:
                    # Append to existing summary
                    sections['professional summary'] += '\n' + line
    
    # Save the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    # Process work experience
    work_experience_html = ""
    if 'work experience' in sections:
        work_exp_content = sections['work experience']
        job_blocks = []
        current_job = []
        
        for line in work_exp_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('•'):  # Main job entry
                if current_job:  # Save previous job if exists
                    job_blocks.append('\n'.join(current_job))
                current_job = [line]
            else:
                current_job.append(line)
                
        # Add the last job
        if current_job:
            job_blocks.append('\n'.join(current_job))
            
        # Create HTML for each job block
        for job_block in job_blocks:
            lines = job_block.split('\n')
            job_title = lines[0].lstrip('• ').strip()
            
            # Parse job details and format them properly
            job_details_html = "<div class='job-description'>"
            for i, line in enumerate(lines[1:]):
                if line.startswith('-'):
                    job_details_html += f"<p class='achievement'><span class='bullet'>•</span>{line.lstrip('- ')}</p>"
                else:
                    class_name = 'company' if i == 0 else 'date' if i == 1 else ''
                    job_details_html += f"<p class='{class_name}'>{line}</p>"
            job_details_html += "</div>"
            
            work_experience_html += f"""
            <div class="experience-item">
                <div class="job-title">{job_title}</div>
                {job_details_html}
            </div>
            """
    
    # Process education
    education_html = ""
    if 'education' in sections:
        edu_content = sections['education']
        edu_blocks = []
        current_edu = []
        
        for line in edu_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('•'):  # Main education entry
                if current_edu:  # Save previous education if exists
                    edu_blocks.append('\n'.join(current_edu))
                current_edu = [line]
            else:
                current_edu.append(line)
                
        # Add the last education entry
        if current_edu:
            edu_blocks.append('\n'.join(current_edu))
            
        # Create HTML for each education block
        for edu_block in edu_blocks:
            lines = edu_block.split('\n')
            degree = lines[0].lstrip('• ').strip()
            
            school_details = ""
            if len(lines) > 1:
                school_details = f"<p class='school'>{lines[1]}</p>"
            
            if len(lines) > 2:
                school_details += f"<p class='date'>{lines[2]}</p>"
            
            education_html += f"""
            <div class="education-item">
                <div class="degree">{degree}</div>
                {school_details}
            </div>
            """
    
    # Process skills - place multiple skills on same line
    skills_html = ""
    if 'skills' in sections:
        skills_content = sections['skills']
        skills_by_category = {}
        current_category = "General"
        current_skills = []
        
        for line in skills_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('•'):
                # If we have accumulated skills, save them
                if current_skills:
                    if current_category not in skills_by_category:
                        skills_by_category[current_category] = []
                    skills_by_category[current_category].extend(current_skills)
                    current_skills = []
                
                skill_text = line.lstrip('• ').strip()
                if ":" in skill_text:
                    parts = skill_text.split(":", 1)
                    current_category = parts[0].strip()
                    skill_value = parts[1].strip()
                    if skill_value:  # Only add if there's actual skill content after the colon
                        # Split multiple skills if they're comma-separated
                        for skill in skill_value.split(','):
                            skill = skill.strip()
                            if skill:
                                current_skills.append(skill)
                else:
                    current_skills.append(skill_text)
            elif line.startswith('-'):
                skill_text = line.lstrip('- ').strip()
                current_skills.append(skill_text)
            else:
                # If line doesn't start with bullet or dash, it might be a continuation
                if current_skills:
                    # Append to the last skill if it's a continuation
                    current_skills[-1] = current_skills[-1] + " " + line
        
        # Add any remaining skills
        if current_skills:
            if current_category not in skills_by_category:
                skills_by_category[current_category] = []
            skills_by_category[current_category].extend(current_skills)
        
        # Create HTML for skills by category
        for category, skills in skills_by_category.items():
            if category == "General":
                skills_html += f"<li class='skill-item'>{', '.join(skills)}</li>"
            else:
                # Remove any "Proficient in" or "Experienced with" prefixes
                category = category.replace("Proficient in", "").replace("Experienced with", "").replace("Proficient with", "").strip()
                # Clean up any trailing colons
                category = category.rstrip(':')
                # Create simple list item without any skill bars
                skills_html += f"<li class='skill-item'><span class='skill-category'>{category}:</span> {', '.join(skills)}</li>"
    
    # Process projects
    projects_html = ""
    if 'projects' in sections:
        projects_content = sections['projects']
        project_blocks = []
        current_project = []
        
        for line in projects_content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('•'):  # Main project entry
                if current_project:  # Save previous project if exists
                    project_blocks.append('\n'.join(current_project))
                current_project = [line]
            else:
                current_project.append(line)
                
        # Add the last project
        if current_project:
            project_blocks.append('\n'.join(current_project))
            
        # Create HTML for each project block
        for project_block in project_blocks:
            # Split the project block into title and description
            lines = project_block.split('\n')
            title = lines[0].lstrip('• ').strip()
            
            # Process project details
            project_details_html = "<div class='project-details'>"
            for line in lines[1:]:
                if line.startswith('-'):
                    project_details_html += f"<p class='achievement'><span class='bullet'>•</span>{line.lstrip('- ').strip()}</p>"
                else:
                    project_details_html += f"<p class='project-info'>{line}</p>"
            project_details_html += "</div>"
            
            projects_html += f"""
            <div class="project-item">
                <div class="project-title">{title}</div>
                {project_details_html}
            </div>
            """
    
    # Process languages, certifications, interests - place multiple items on same line
    languages_html = ""
    certifications_html = ""
    interests_html = ""
    
    for section_name in ['languages', 'certifications', 'interests']:
        if section_name in sections:
            section_content = sections[section_name]
            items = []
            
            for line in section_content.split('\n'):
                line = line.strip()
                if line:
                    # Check if line has bullet points or dash
                    if line.startswith('•') or line.startswith('-'):
                        text = line.lstrip('•- ').strip()
                        # Split by commas in case multiple items are on one line
                        for item in text.split(','):
                            item = item.strip()
                            if item:
                                items.append(item)
                    else:
                        # No bullet, but still add it
                        items.append(line)
            
            # Join all items with commas and create list item
            item_html = f"<li class='item'>{', '.join(items)}</li>" if items else ""
            
            # Assign to the correct variable
            if section_name == 'languages':
                languages_html = item_html
            elif section_name == 'certifications':
                certifications_html = item_html
            elif section_name == 'interests':
                interests_html = item_html
    
    # Create HTML content using the template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Professional Resume - {applicant_name}</title>
        <style>
            /* DocRaptor/PDF-specific page settings */
            @page {{
                size: letter;
                margin: 0.5in;
            }}
            
            /* Reset and base styles */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #2d3748;
                background-color: #fff;
            }}
            
            /* Resume container */
            .resume {{
                max-width: 7.5in;
                margin: 0 auto;
                background-color: white;
            }}
            
            /* Header section */
            .header {{
                margin-bottom: 30px;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 20px;
                text-align: center;
            }}
            
            .header::after {{
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background: linear-gradient(to right, #4299e1, #ebf8ff);
            }}
            
            .name {{
                font-size: 28px;
                font-weight: 700;
                color: #2b6cb0;
                margin-bottom: 5px;
                letter-spacing: 0.5px;
            }}
            
            .header-content {{
                display: flex;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
                gap: 15px;
                font-size: 14px;
                margin-top: 15px;
            }}
            
            .header-content div {{
                display: inline-flex;
                align-items: center;
            }}
            
            .header-content i {{
                margin-right: 5px;
                color: #3498db;
            }}
            
            .header-content a {{
                color: #3498db;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
            }}
            
            .header-content a:hover {{
                text-decoration: underline;
            }}
            
            /* Main content layout */
            .content {{
                display: grid;
                grid-template-columns: 65% 35%;
                gap: 25px;
            }}
            
            /* Section styling */
            .section {{
                margin-bottom: 20px;
                page-break-inside: avoid;
            }}
            
            .section-title {{
                font-size: 16px;
                font-weight: 700;
                color: #2b6cb0;
                margin-bottom: 12px;
                padding-bottom: 4px;
                border-bottom: 1px solid #e2e8f0;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            /* Experience items */
            .experience-item, .education-item, .project-item {{
                margin-bottom: 16px;
                page-break-inside: avoid;
            }}
            
            .job-title, .degree, .project-title {{
                font-weight: 600;
                font-size: 14px;
                color: #1a202c;
                margin-bottom: 3px;
            }}
            
            .company, .school {{
                font-weight: 500;
                color: #4299e1;
                font-size: 13px;
            }}
            
            .date {{
                font-size: 12px;
                color: #718096;
                margin-bottom: 6px;
                font-style: italic;
            }}
            
            .job-description p, .project-details p {{
                font-size: 12px;
                margin-bottom: 4px;
                line-height: 1.5;
            }}
            
            .achievement {{
                position: relative;
                padding-left: 12px;
            }}
            
            .bullet {{
                position: absolute;
                left: 0;
                color: #4299e1;
            }}
            
            /* Skills section */
            .skills-list {{
                list-style-type: none;
                padding: 0;
                margin: 0;
            }}
            
            .skill-item {{
                margin-bottom: 8px;
                font-size: 12px;
                line-height: 1.5;
                word-wrap: break-word;
            }}
            
            .skill-category {{
                font-weight: 600;
                color: #1a202c;
                margin-right: 4px;
            }}
            
            /* Languages, certifications, interests */
            .languages-list, .interests-list {{
                list-style-type: none;
                padding: 0;
                margin: 0;
            }}
            
            .item {{
                margin-bottom: 8px;
                font-size: 12px;
                line-height: 1.5;
            }}
            
            /* Summary section */
            .summary {{
                font-size: 12px;
                line-height: 1.6;
                margin-bottom: 10px;
                text-align: justify;
            }}
            
            /* Project info */
            .project-info {{
                font-size: 12px;
                color: #718096;
                font-style: italic;
                margin-bottom: 5px;
            }}
            
            /* Print styles */
            @media print {{
                body {{
                    background-color: white;
                    padding: 0;
                }}
                
                .resume {{
                    box-shadow: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="resume">
            <!-- Header Section -->
            <div class="header">
                <h1 class="name">{applicant_name}</h1>
                {header_content_html}
            </div>
            
            <!-- Main Content -->
            <div class="content">
                <!-- Left Column -->
                <div class="left-column">
                    <!-- Professional Summary -->
                    {f'<div class="section"><h2 class="section-title">Professional Summary</h2><p class="summary">{sections.get("professional summary", "")}</p></div>' if "professional summary" in sections else ''}
                    
                    <!-- Education -->
                    {f'<div class="section"><h2 class="section-title">Education</h2>{education_html}</div>' if education_html else ''}
                    
                    <!-- Work Experience -->
                    {f'<div class="section"><h2 class="section-title">Work Experience</h2>{work_experience_html}</div>' if work_experience_html else ''}
                    
                    <!-- Projects -->
                    {f'<div class="section"><h2 class="section-title">Key Projects</h2>{projects_html}</div>' if projects_html else ''}
                </div>
                
                <!-- Right Column -->
                <div class="right-column">
                    <!-- Skills -->
                    {f'<div class="section"><h2 class="section-title">Skills</h2><ul class="skills-list">{skills_html}</ul></div>' if skills_html else ''}
                    
                    <!-- Languages -->
                    {f'<div class="section"><h2 class="section-title">Languages</h2><ul class="languages-list">{languages_html}</ul></div>' if languages_html else ''}
                    
                    <!-- Certifications -->
                    {f'<div class="section"><h2 class="section-title">Certifications</h2><ul class="languages-list">{certifications_html}</ul></div>' if certifications_html else ''}
                    
                    <!-- Interests -->
                    {f'<div class="section"><h2 class="section-title">Interests</h2><ul class="interests-list">{interests_html}</ul></div>' if interests_html else ''}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generate_pdf_with_docraptor(html_content: str) -> str:
    """Generate PDF using DocRaptor API."""
    url = "https://api.docraptor.com/docs"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "pdf",
        "document_content": html_content,
        "test": False,  # Set to True for testing to avoid using credits
        "prince_options": {
            "media": "print",
            "pdf_profile": "PDF/UA-1"
        }
    }
    
    try:
        print("=== Starting DocRaptor PDF Generation ===")
        print(f"HTML content size: {len(html_content)} bytes")
        print(f"DOCRAPTOR_API_KEY prefix: {DOCRAPTOR_API_KEY[:10] if DOCRAPTOR_API_KEY else 'Not set'}")
        
        # Encode API key for basic auth
        auth_string = f"{DOCRAPTOR_API_KEY}:"
        auth_bytes = auth_string.encode('ascii')
        base64_auth = base64.b64encode(auth_bytes).decode('ascii')
        headers['Authorization'] = f'Basic {base64_auth}'
        
        print("Sending request to DocRaptor API...")
        response = requests.post(
            url, 
            headers=headers, 
            json=data
        )
        print(f"DocRaptor API response status code: {response.status_code}")
        
        response.raise_for_status()
        print("DocRaptor API request successful")
        
        # Save the PDF
        filename = f"enhanced_resume_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_OUTPUT_DIR, filename)
        print(f"Saving PDF to: {filepath}")
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"PDF saved successfully: {filename}")
        
        return filename
    
    except requests.exceptions.RequestException as e:
        print("=== ERROR IN DOCRAPTOR API REQUEST ===")
        print(f"RequestException type: {type(e)}")
        print(f"RequestException message: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        print("Full traceback:")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    except Exception as e:
        print("=== UNEXPECTED ERROR IN PDF GENERATION ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print("Full traceback:")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unexpected error generating PDF: {str(e)}")

def generate_pdf_from_text(resume_text: str, applicant_name: str, contact_info: str, github_link: str = None, linkedin_link: str = None, portfolio_link: str = None) -> str:
    """Generate a professional PDF resume from text using DocRaptor."""
    # Create HTML content
    html_content = create_resume_html(
        resume_text,
        applicant_name,
        contact_info,
        github_link,
        linkedin_link,
        portfolio_link
    )
    
    # Generate PDF using DocRaptor
    return generate_pdf_with_docraptor(html_content)
