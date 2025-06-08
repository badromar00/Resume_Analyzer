import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button, Box, Typography, TextField, CircularProgress, Paper, Alert, Grid } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ReactMarkdown from 'react-markdown';
import './App.css';
import EnhanceResume from './components/EnhanceResume';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

function ResumeAnalyzer() {
  const [resumeText, setResumeText] = useState('');
  const [jobDescriptionText, setJobDescriptionText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [placeholderVisible, setPlaceholderVisible] = useState(true);
  const [showEnhanceResume, setShowEnhanceResume] = useState(false);

  // Use effect to hide placeholder when we have results
  useEffect(() => {
    if (analysisResult) {
      setPlaceholderVisible(false);
    } else {
      setPlaceholderVisible(true);
    }
  }, [analysisResult]);

  const handleAnalyze = async () => {
    if (!resumeText.trim() || !jobDescriptionText.trim()) {
      setError('Please provide both resume text and job description text.');
      setAnalysisResult(null);
      return;
    }

    setIsLoading(true);
    setError('');
    setAnalysisResult(null);
    setShowEnhanceResume(false);

    try {
      const response = await api.post('/analyze/', {
        resume_text: resumeText,
        job_description_text: jobDescriptionText,
      });

      setAnalysisResult(response.data);
    } catch (err) {
      if (err.response) {
        console.error('Error response:', err.response.data);
        setError(`Error: ${err.response.data.detail || 'Failed to analyze.'} (Status: ${err.response.status})`);
      } else if (err.request) {
        console.error('Error request:', err.request);
        setError('Error: No response from server. Is the backend running?');
      } else {
        console.error('Error message:', err.message);
        setError(`Error: ${err.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Resume Analyzer</h1>
        <p>Get instant feedback on your resume's match with job descriptions</p>
      </header>
      <main className="App-main">
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="resumeText">
              <span role="img" aria-label="resume">📄</span> Paste Your Resume Text
            </label>
            <textarea
              id="resumeText"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste the full text of your resume here..."
              disabled={isLoading}
            />
          </div>

          <div className="input-group">
            <label htmlFor="jobDescriptionText">
              <span role="img" aria-label="job">💼</span> Paste Job Description Text
            </label>
            <textarea
              id="jobDescriptionText"
              value={jobDescriptionText}
              onChange={(e) => setJobDescriptionText(e.target.value)}
              placeholder="Paste the full text of the job description here..."
              disabled={isLoading}
            />
          </div>

          <button 
            onClick={handleAnalyze} 
            disabled={isLoading} 
            className="analyze-button"
          >
            {isLoading ? (
              <>
                <span role="img" aria-label="loading">⏳</span> Analyzing...
              </>
            ) : (
              <>
                <span role="img" aria-label="analyze">🔍</span> Analyze Resume
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="error-message">
            <p>
              <span role="img" aria-label="error">⚠️</span> {error}
            </p>
          </div>
        )}

        {analysisResult ? (
          <div className="results-section">
            <h2>
              <span role="img" aria-label="results">📊</span> Analysis Results
            </h2>
            <div className="score">
              <strong>Compatibility Score:</strong>{' '}
              <span className="score-value">
                {analysisResult.compatibility_score.toFixed(1)}%
              </span>
            </div>

            {/* Keywords Section */}
            <div className="keywords-section">
              <div className="keywords-group">
                <h3>
                  <span role="img" aria-label="matched">✅</span> Matched Keywords
                </h3>
                <div className="keywords-list">
                  {analysisResult.matched_keywords.map((keyword, index) => (
                    <span key={index} className="keyword matched">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div className="keywords-group">
                <h3>
                  <span role="img" aria-label="missing">❌</span> Missing Keywords
                </h3>
                <div className="keywords-list">
                  {analysisResult.missing_keywords.map((keyword, index) => (
                    <span key={index} className="keyword missing">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="summary">
              <strong>
                <span role="img" aria-label="suggestions">💡</span> Improvement Suggestions
              </strong>
              <pre>{analysisResult.improvement_summary}</pre>
            </div>

            {/* Enhance Resume Button */}
            <div className="enhance-resume-button">
              <Button
                variant="contained"
                color="primary"
                onClick={() => setShowEnhanceResume(!showEnhanceResume)}
                startIcon={<PictureAsPdfIcon />}
              >
                {showEnhanceResume ? 'Hide Resume Enhancement' : 'Enhance Your Resume'}
              </Button>
            </div>

            {/* Enhance Resume Section */}
            {showEnhanceResume && (
              <div className="enhance-resume-section">
                <EnhanceResume 
                  initialResumeText={resumeText}
                  initialJobDescriptionText={jobDescriptionText}
                  improvementSuggestions={analysisResult.improvement_summary}
                />
              </div>
            )}
          </div>
        ) : (
          placeholderVisible && (
            <div className="results-section placeholder-results">
              <h2>
                <span role="img" aria-label="results">📊</span> Analysis Results
              </h2>
              <div className="score">
                <strong>Compatibility Score:</strong>{' '}
                <span className="score-value">
                  --.--%
                </span>
              </div>
              <div className="keywords-section">
                <div className="keywords-group">
                  <h3>
                    <span role="img" aria-label="matched">✅</span> Matched Keywords
                  </h3>
                  <div className="keywords-list">
                    <span className="placeholder-text">Keywords will appear here after analysis</span>
                  </div>
                </div>
                <div className="keywords-group">
                  <h3>
                    <span role="img" aria-label="missing">❌</span> Missing Keywords
                  </h3>
                  <div className="keywords-list">
                    <span className="placeholder-text">Keywords will appear here after analysis</span>
                  </div>
                </div>
              </div>
              <div className="summary">
                <strong>
                  <span role="img" aria-label="suggestions">💡</span> Improvement Suggestions
                </strong>
                <pre>Enter your resume and job description, then click "Analyze Resume" to see suggestions here.</pre>
              </div>
            </div>
          )
        )}
      </main>
      <footer className="App-footer">
        <p>
          Resume Analyzer (In Progress)
        </p>
      </footer>
    </div>
  );
}

export default ResumeAnalyzer;