from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .api.routes import router
from .core.config import CORS_ORIGINS, API_TITLE, API_DESCRIPTION, API_VERSION

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/")
@limiter.limit("5/minute")
async def read_root(request: Request):
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the Resume Analyzer API!",
        "version": API_VERSION,
        "endpoints": {
            "analyze": "POST /analyze/ - Analyze resume against job description",
            "enhance": "POST /enhance-resume/ - Generate an enhanced resume PDF",
            "download": "GET /download-pdf/{filename} - Download generated PDF"
        }
    } 