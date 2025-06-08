import os
from dotenv import load_dotenv
import tempfile

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DOCRAPTOR_API_KEY = os.getenv("DOCRAPTOR_API_KEY")

# Base URL for backend
BASE_BACKEND_URL = os.getenv("BASE_BACKEND_URL", "http://localhost:8000")

# CORS Settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://storage.googleapis.com",
    "https://resume-analyzer-123.storage.googleapis.com",
    "https://*.storage.googleapis.com"  # Allow all subdomains
]

# PDF Settings
PDF_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "resume_pdfs")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# API Settings
API_TITLE = "Resume Analyzer API"
API_DESCRIPTION = "API for analyzing resumes against job descriptions and generating enhanced resumes."
API_VERSION = "0.4.0" 