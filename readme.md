# AI Resume Analyzer

A powerful web application that helps job seekers optimize their resumes by analyzing them against job descriptions using AI. The application provides detailed feedback, improvement suggestions, and can generate enhanced versions of resumes.

🔗 **Live Demo**: [Resume Analyzer](https://storage.googleapis.com/resume-analyzer-123/index.html)

## Features

- 📊 **Resume Analysis**: Get instant feedback on how well your resume matches a job description
- 💡 **AI-Powered Suggestions**: Receive actionable improvement suggestions
- 🔍 **Keyword Matching**: Identify matched and missing keywords from the job description
- 📝 **Resume Enhancement**: Generate an enhanced version of your resume optimized for the target position
- 📄 **PDF Generation**: Download your enhanced resume as a professionally formatted PDF
- 🎯 **Compatibility Score**: Get a detailed breakdown of how well your resume matches the job requirements

## Tech Stack

### Frontend
- React.js
- Material-UI
- Axios for API calls

### Backend
- FastAPI (Python)
- OpenAI GPT-4 for AI analysis
- DocRaptor for PDF generation

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- OpenAI API key
- DocRaptor API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_openai_api_key
DOCRAPTOR_API_KEY=your_docraptor_api_key
```

5. Create a `.env` file in the frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

## API Endpoints

- `POST /analyze/`: Analyze resume against job description
- `POST /enhance-resume/`: Generate an enhanced resume PDF
- `GET /download-pdf/{filename}`: Download generated PDF
