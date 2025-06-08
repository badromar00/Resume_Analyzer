# app/utils/response_parser.py
import re

def parse_ai_response(ai_response_text: str) -> dict:
    """Parse the structured response from OpenAI."""
    compatibility_score = 0.0
    improvement_summary = "Could not parse improvement suggestions from AI response."
    matched_keywords = []
    missing_keywords = []

    # Parse score
    score_match = re.search(r"Score:\s*(\d+(\.\d+)?)\s*%", ai_response_text)
    if score_match:
        try:
            compatibility_score = float(score_match.group(1))
        except ValueError:
            print(f"Warning: Could not convert score '{score_match.group(1)}' to float.")
    else:
        print("Warning: Could not find 'Score:' pattern in AI response.")

    # Parse summary
    summary_parts = ai_response_text.split("Summary:", 1)
    if len(summary_parts) > 1:
        summary_text = summary_parts[1].split("Matched Keywords:", 1)[0].strip()
        bullet_points = [line.strip() for line in summary_text.split('\n') if line.strip().startswith('-') or line.strip()]
        if bullet_points:
            improvement_summary = "\n".join(bullet_points)
        else:
            improvement_summary = summary_text

    # Parse matched keywords
    matched_section = re.search(r"Matched Keywords:(.*?)(?:Missing Keywords:|$)", ai_response_text, re.DOTALL)
    if matched_section:
        matched_keywords = [line.strip('- ').strip() for line in matched_section.group(1).split('\n') if line.strip().startswith('-')]

    # Parse missing keywords
    missing_section = re.search(r"Missing Keywords:(.*?)$", ai_response_text, re.DOTALL)
    if missing_section:
        missing_keywords = [line.strip('- ').strip() for line in missing_section.group(1).split('\n') if line.strip().startswith('-')]

    return {
        "compatibility_score": compatibility_score,
        "improvement_summary": improvement_summary.strip(),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    } 