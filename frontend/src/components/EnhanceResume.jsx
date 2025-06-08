import React, { useState } from 'react';
import { Button, Box, Typography, TextField, CircularProgress, Paper, Alert, Grid } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

const EnhanceResume = ({ initialResumeText = '', initialJobDescriptionText = '', improvementSuggestions = '' }) => {
  const [resumeText, setResumeText] = useState(initialResumeText);
  const [jobDescriptionText, setJobDescriptionText] = useState(initialJobDescriptionText);
  const [applicantName, setApplicantName] = useState('');
  const [contactInfo, setContactInfo] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [location, setLocation] = useState('');
  const [githubLink, setGithubLink] = useState('');
  const [linkedinLink, setLinkedinLink] = useState('');
  const [portfolioLink, setPortfolioLink] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [pdfUrl, setPdfUrl] = useState('');
  const [improvementSummary, setImprovementSummary] = useState('');

  const handleResumeUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      setResumeText(e.target.result);
    };
    reader.readAsText(file);
  };

  const handleJobDescriptionUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      setJobDescriptionText(e.target.result);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resumeText || !jobDescriptionText || !applicantName || !phoneNumber || !location) {
      setError('Please fill in all required fields (Name, Phone Number, Location)');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await api.post('/enhance-resume/', {
        resume_text: resumeText,
        job_description_text: jobDescriptionText,
        applicant_name: applicantName,
        contact_info: `${contactInfo} | ${phoneNumber} | ${location}`,
        github_link: githubLink,
        linkedin_link: linkedinLink,
        portfolio_link: portfolioLink,
        improvement_suggestions: improvementSuggestions
      });

      // The backend now returns a fully qualified URL, so we can use it directly
      setPdfUrl(response.data.pdf_url);
      setImprovementSummary(response.data.improvement_summary);
      setSuccess(true);
    } catch (err) {
      console.error('Error enhancing resume:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to enhance resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
        Enhance Your Resume
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Personal Information
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                label="Your Name *"
                fullWidth
                required
                value={applicantName}
                onChange={(e) => setApplicantName(e.target.value)}
                margin="normal"
                placeholder="John Doe"
              />
              
              <TextField
                label="Email Address *"
                fullWidth
                required
                value={contactInfo}
                onChange={(e) => setContactInfo(e.target.value)}
                margin="normal"
                placeholder="email@example.com"
              />

              <TextField
                label="Phone Number *"
                fullWidth
                required
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                margin="normal"
                placeholder="(555) 123-4567"
              />

              <TextField
                label="Location *"
                fullWidth
                required
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                margin="normal"
                placeholder="City, State"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                label="GitHub Profile (Optional)"
                fullWidth
                value={githubLink}
                onChange={(e) => setGithubLink(e.target.value)}
                margin="normal"
                placeholder="https://github.com/username"
              />

              <TextField
                label="LinkedIn Profile (Optional)"
                fullWidth
                value={linkedinLink}
                onChange={(e) => setLinkedinLink(e.target.value)}
                margin="normal"
                placeholder="https://linkedin.com/in/username"
              />

              <TextField
                label="Portfolio Website (Optional)"
                fullWidth
                value={portfolioLink}
                onChange={(e) => setPortfolioLink(e.target.value)}
                margin="normal"
                placeholder="https://your-portfolio.com"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Resume Text"
                multiline
                rows={6}
                fullWidth
                required
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                margin="normal"
                placeholder="Paste your resume text here..."
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Job Description"
                multiline
                rows={6}
                fullWidth
                required
                value={jobDescriptionText}
                onChange={(e) => setJobDescriptionText(e.target.value)}
                margin="normal"
                placeholder="Paste the job description here..."
              />
            </Grid>
            
            <Grid item xs={12}>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={loading || !resumeText || !jobDescriptionText || !applicantName || !phoneNumber || !location}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PictureAsPdfIcon />}
                >
                  {loading ? 'Enhancing Resume...' : 'Generate Enhanced Resume PDF'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Alert severity="success" sx={{ mb: 3 }}>
            Your enhanced resume has been generated successfully!
          </Alert>
          
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="success"
              href={pdfUrl}
              target="_blank"
              startIcon={<PictureAsPdfIcon />}
            >
              Download Enhanced Resume PDF
            </Button>
          </Box>
          
          <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
            <ReactMarkdown>
              {improvementSummary}
            </ReactMarkdown>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default EnhanceResume; 