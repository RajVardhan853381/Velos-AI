import React, { useState, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, CheckCircle, Loader2, AlertCircle, FileText, Sparkles, Award, Shield, Eye, Target, TrendingUp, Clock, Code } from 'lucide-react';
import Pipeline3D from './Pipeline3D'; // Import the new 3D component
import { API_BASE } from '../config.js';

const VerificationPipeline = () => {
  // State: 'idle' -> 'gatekeeper' -> 'validator' -> 'inquisitor' -> 'done'
  const [pipelineState, setPipelineState] = useState('idle');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [fileExtracting, setFileExtracting] = useState(false);

  // Load sample data
  const loadSampleData = async () => {
    const sampleResume = `Name: Aarvex Nolin
Target Role: Applied AI Engineer / GenAI Engineer (Entry Level)
Email: aarvex.nolin@samplemail.com

GitHub: github.com/aarvex-ai
LinkedIn: linkedin.com/in/aarvexnolin

EDUCATION
Bachelor of Technology in Computer Science
University Name, 2020-2024
CGPA: 8.5/10

SKILLS
Programming Languages: Python, JavaScript, Java
AI/ML Frameworks: TensorFlow, PyTorch, Hugging Face Transformers
GenAI Tools: LangChain, OpenAI API, Llama, GPT-4
Cloud: AWS, Google Cloud Platform
Databases: PostgreSQL, MongoDB, Vector DBs
Version Control: Git, GitHub

EXPERIENCE
AI Research Intern | Tech Startup | Jan 2024 - Jun 2024
- Developed fine-tuned LLMs for domain-specific applications
- Built RAG (Retrieval Augmented Generation) pipelines
- Implemented prompt engineering strategies
- Created chatbot applications using LangChain

PROJECTS
1. Resume Verification System
   - Built AI-powered resume verification tool
   - Implemented multi-agent system for fraud detection
   - Technologies: Python, FastAPI, LangChain, ChromaDB

2. Sentiment Analysis Dashboard
   - Created real-time sentiment analysis for customer reviews
   - Technologies: React, Python, TensorFlow

CERTIFICATIONS
- Deep Learning Specialization - Coursera
- AWS Certified Cloud Practitioner`;

    const sampleJob = `Position: Junior Applied AI Engineer

Type: Full-Time / Contract
Mode: Remote / Hybrid
Experience: 0-1 year (Project experience accepted)

ABOUT THE ROLE:
We are seeking a passionate Junior Applied AI Engineer to join our growing AI team. You'll work on cutting-edge GenAI applications and LLM-powered solutions.

REQUIRED SKILLS:
- Strong Python programming
- Experience with LLMs (OpenAI, Llama, etc.)
- Knowledge of RAG pipelines and vector databases
- Understanding of prompt engineering
- Familiarity with LangChain or similar frameworks
- Basic ML/DL knowledge
- Git/GitHub proficiency

PREFERRED SKILLS:
- Experience with FastAPI or Flask
- Cloud platform knowledge (AWS/GCP)
- Frontend skills (React/Vue)
- Experience with fine-tuning models

RESPONSIBILITIES:
- Develop and deploy AI-powered applications
- Build RAG pipelines and chatbot systems
- Optimize LLM prompts and responses
- Collaborate with cross-functional teams
- Document technical solutions

WHAT WE OFFER:
- Competitive salary
- Remote work flexibility
- Learning & development opportunities
- Mentorship from senior engineers
- Cutting-edge AI projects`;

    setResumeText(sampleResume);
    setJobDescription(sampleJob);
  };

  // Handle file upload — sends PDF/DOCX to backend for text extraction
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const ext = file.name.toLowerCase();
    const isBinary =
      file.type === 'application/pdf' ||
      ext.endsWith('.pdf') ||
      ext.endsWith('.doc') ||
      ext.endsWith('.docx');

    setResumeFile(file);
    setError(null);

    if (isBinary) {
      // Send to backend parser — never try to read binary as text client-side
      setFileExtracting(true);
      try {
        const fd = new FormData();
        fd.append('resume_file', file);
        const res = await fetch(`${API_BASE}/api/extract-resume-text`, { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Could not extract text from file');
        setResumeText(data.text || '');
      } catch (err) {
        setError(err.message + ' Please paste the resume text manually.');
        setResumeFile(null);
      } finally {
        setFileExtracting(false);
      }
    } else {
      // Plain text file — read client-side
      const reader = new FileReader();
      reader.onload = (event) => setResumeText(event.target.result);
      reader.readAsText(file);
    }
  };

  // Real API Integration
  const startRealAnalysis = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError('Please provide both resume text and job description');
      return;
    }

    setLoading(true);
    setError(null);
    setPipelineState('gatekeeper');

    try {
      // Call the actual backend API
      const response = await fetch(`${API_BASE}/api/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description: jobDescription,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API Error: ${response.status}`);
      }

      const data = await response.json();

      // Animate through stages based on real data
      if (data.stages?.gatekeeper) {
        setPipelineState('validator');
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      if (data.stages?.validator) {
        setPipelineState('inquisitor');
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Always transition to done after animations complete
      setPipelineState('done');
      setResult(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      setPipelineState('idle');
    }
  };

  // Demo simulation (for testing without backend)
  const startDemoAnalysis = () => {
    if (pipelineState !== 'idle') return; // guard against double-click
    setPipelineState('gatekeeper');
    setTimeout(() => setPipelineState('validator'), 2500);
    setTimeout(() => setPipelineState('inquisitor'), 5000);
    setTimeout(() => {
      setPipelineState('done');
      setResult({
        id: 'CAND-DEMO',
        status: 'passed',
        trust_score: 92,
        skill_match: 88,
        stages: {
          gatekeeper: { status: 'passed', pii_removed: true },
          validator: { status: 'passed', skill_match: 88 },
          inquisitor: { status: 'passed', trust_score: 92 },
        },
      });
    }, 8000);
  };

  const resetPipeline = () => {
    setPipelineState('idle');
    setResult(null);
    setError(null);
    setResumeText('');
    setJobDescription('');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">

      {/* 1. Control Panel / Upload Area */}
      {pipelineState === 'idle' ? (
        <motion.div
          layout
          className="bg-gradient-to-br from-emerald-50/70 to-green-50/70 backdrop-blur-xl border border-emerald-100/50 rounded-3xl p-8 shadow-lg"
        >
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-400 to-green-400 text-white rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg animate-float">
                <Upload size={32} />
              </div>
              <h2 className="text-2xl font-bold text-slate-800">Initiate Verification</h2>
              <p className="text-slate-600 mt-2">Enter candidate details to begin 3 AI Agents Analysis</p>
            </div>

            {/* Quick Actions */}
            <div className="flex gap-3 justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={loadSampleData}
                className="flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm border border-emerald-200 text-slate-700 font-medium rounded-xl shadow-sm transition-all"
              >
                <Sparkles size={16} className="text-emerald-600" />
                Load Sample Data
              </motion.button>
              <label className="cursor-pointer">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm border border-emerald-200 text-slate-700 font-medium rounded-xl shadow-sm transition-all"
                >
                  {fileExtracting
                    ? <><Loader2 size={16} className="text-emerald-600 animate-spin" /> Extracting...</>
                    : <><FileText size={16} className="text-emerald-600" /> Upload Resume File</>
                  }
                </motion.div>
                <input
                  type="file"
                  accept=".txt,.pdf,.doc,.docx"
                  onChange={handleFileUpload}
                  disabled={fileExtracting}
                  className="hidden"
                />
              </label>
            </div>

            {resumeFile && (
              <div className="text-center text-sm text-emerald-700 bg-emerald-100/50 backdrop-blur-sm px-4 py-2 rounded-xl">
                📄 {resumeFile.name} uploaded
              </div>
            )}

            {/* Resume Input */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Resume Text
              </label>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste resume content here or use 'Load Sample Data' button above..."
                className="w-full h-40 p-4 bg-white/80 backdrop-blur-sm border border-emerald-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none transition-all"
              />
            </div>

            {/* Job Description Input */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste job description here or use 'Load Sample Data' button above..."
                className="w-full h-32 p-4 bg-white/80 backdrop-blur-sm border border-emerald-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none transition-all"
              />
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-4 bg-red-50/80 backdrop-blur-sm border border-red-200 rounded-xl text-red-700"
              >
                <AlertCircle size={20} />
                <span className="text-sm">{error}</span>
              </motion.div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={startRealAnalysis}
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white px-8 py-4 rounded-xl font-bold shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 size={20} className="animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <CheckCircle size={20} />
                    Start Verification
                  </>
                )}
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={startDemoAnalysis}
                disabled={loading}
                className="flex-1 bg-white/60 hover:bg-white/80 backdrop-blur-sm border-2 border-dashed border-amber-300 text-amber-700 px-8 py-4 rounded-xl font-medium shadow-sm transition-all active:scale-95 disabled:opacity-50"
              >
                🎭 Demo Mode
              </motion.button>
            </div>
          </div>
        </motion.div>
      ) : (
        <div className="bg-emerald-50/70 backdrop-blur-xl border border-emerald-200 p-6 rounded-2xl shadow-md flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Analysis in Progress</h3>
            <p className="text-sm text-slate-600">Processing candidate ID: <span className="font-mono text-emerald-600">8f7a...3b21</span></p>
          </div>
          <div className="px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg text-sm font-semibold animate-pulse">
            Live Protocol
          </div>
        </div>
      )}

      {/* 2. THE 3D VISUALIZATION */}
      {/* We always render the scene so it looks cool even when idle */}
      <Suspense fallback={<div className="h-96 flex items-center justify-center"><div className="text-slate-500">Loading 3D scene...</div></div>}>
        <Pipeline3D currentStep={pipelineState} />
      </Suspense>

      {/* 3. Enhanced Results Panel (Only shows when done) */}
      <AnimatePresence>
        {pipelineState === 'done' && result && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="space-y-8"
          >
            {/* Success Banner */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className={`relative overflow-hidden rounded-3xl p-8 shadow-2xl ${result.status === 'passed'
                ? 'bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500'
                : 'bg-gradient-to-r from-red-500 via-rose-500 to-pink-500'
                }`}
            >
              <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>
              <div className="relative flex items-center justify-between">
                <div className="flex items-center gap-6">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, ease: "linear", repeat: Infinity }}
                    className="w-20 h-20 rounded-full bg-white/20 backdrop-blur flex items-center justify-center"
                  >
                    {result.status === 'passed' ? (
                      <CheckCircle size={40} className="text-white" />
                    ) : (
                      <AlertCircle size={40} className="text-white" />
                    )}
                  </motion.div>
                  <div>
                    <motion.h2
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="text-3xl font-black text-white mb-2"
                    >
                      {result.status === 'passed' ? 'Verification Successful!' : 'Verification Failed'}
                    </motion.h2>
                    <motion.p
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 0.4 }}
                      className="text-white/90 text-lg"
                    >
                      Candidate ID: <span className="font-mono font-bold">{result.id || 'CAND-DEMO'}</span>
                    </motion.p>
                  </div>
                </div>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
                  className="text-center"
                >
                  <div className="text-6xl font-black text-white mb-1">{result.trust_score || 0}%</div>
                  <div className="text-white/80 text-sm font-semibold">Trust Score</div>
                </motion.div>
              </div>
            </motion.div>

            {/* Main Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Trust Score Card */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="bg-white/90 backdrop-blur-xl border-2 border-emerald-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-green-500 flex items-center justify-center">
                    <Shield size={24} className="text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Overall Trust</p>
                    <p className="text-2xl font-bold text-gray-800">{result.trust_score || 0}%</p>
                  </div>
                </div>
                <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${result.trust_score || 0}%` }}
                    transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
                    className="absolute h-full bg-gradient-to-r from-emerald-400 to-green-500 rounded-full"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {result.trust_score >= 80 ? 'Excellent - Highly Trustworthy' : result.trust_score >= 60 ? 'Good - Generally Reliable' : 'Needs Review'}
                </p>
              </motion.div>

              {/* Skill Match Card */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="bg-white/90 backdrop-blur-xl border-2 border-blue-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center">
                    <Target size={24} className="text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Skill Match</p>
                    <p className="text-2xl font-bold text-gray-800">{result.skill_match || 0}%</p>
                  </div>
                </div>
                <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${result.skill_match || 0}%` }}
                    transition={{ delay: 0.6, duration: 1, ease: "easeOut" }}
                    className="absolute h-full bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {result.skill_match >= 80 ? 'Excellent Fit' : result.skill_match >= 60 ? 'Moderate Fit' : 'Poor Fit'}
                </p>
              </motion.div>

              {/* Experience Years Card */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="bg-white/90 backdrop-blur-xl border-2 border-violet-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center">
                    <Clock size={24} className="text-white" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 font-medium">Experience</p>
                    <p className="text-2xl font-bold text-gray-800">{result.years_exp || 0} Years</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-4">
                  <TrendingUp size={16} className="text-violet-500" />
                  <p className="text-xs text-gray-600">
                    {result.years_exp >= 5 ? 'Senior Level' : result.years_exp >= 2 ? 'Mid Level' : 'Junior Level'}
                  </p>
                </div>
              </motion.div>
            </div>

            {/* Agent Breakdown Section */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="bg-white/90 backdrop-blur-xl border-2 border-gray-200 rounded-2xl p-8 shadow-lg"
            >
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                <Sparkles className="text-violet-500" size={28} />
                3 AI Agents Verification Breakdown
              </h3>

              <div className="space-y-4">
                {/* Gatekeeper */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.7 }}
                  className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-500 flex items-center justify-center">
                        <Shield size={20} className="text-white" />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-800">Gatekeeper Agent</h4>
                        <p className="text-xs text-gray-500">PII Removal & Anonymization</p>
                      </div>
                    </div>
                    <span className={`px-4 py-2 rounded-lg font-semibold ${result.stages?.gatekeeper?.status === 'passed'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                      }`}>
                      {result.stages?.gatekeeper?.status === 'passed' ? '✓ Passed' : '✗ Failed'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <CheckCircle size={16} className="text-green-500" />
                    <span>Personal information successfully anonymized</span>
                  </div>
                </motion.div>

                {/* Validator */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.8 }}
                  className="p-5 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-200"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-emerald-500 flex items-center justify-center">
                        <Target size={20} className="text-white" />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-800">Validator Agent</h4>
                        <p className="text-xs text-gray-500">Skill Matching & Verification</p>
                      </div>
                    </div>
                    <span className={`px-4 py-2 rounded-lg font-semibold ${result.stages?.validator?.status === 'passed'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                      }`}>
                      {result.stages?.validator?.status === 'passed' ? '✓ Passed' : '✗ Failed'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mt-3">
                    <div className="text-sm">
                      <p className="text-gray-500">Match Score</p>
                      <p className="text-lg font-bold text-emerald-600">{result.stages?.validator?.skill_match || result.skill_match || 0}%</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-gray-500">Verified Skills</p>
                      <p className="text-lg font-bold text-gray-800">{result.verified_skills?.length || 0}</p>
                    </div>
                  </div>
                </motion.div>

                {/* Inquisitor */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.9 }}
                  className="p-5 bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl border border-violet-200"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-violet-500 flex items-center justify-center">
                        <Eye size={20} className="text-white" />
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-800">Inquisitor Agent</h4>
                        <p className="text-xs text-gray-500">Fraud Detection & Deep Analysis</p>
                      </div>
                    </div>
                    <span className={`px-4 py-2 rounded-lg font-semibold ${result.stages?.inquisitor?.status === 'passed'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                      }`}>
                      {result.stages?.inquisitor?.status === 'passed' ? '✓ Passed' : '✗ Failed'}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mt-3">
                    <div className="text-sm">
                      <p className="text-gray-500">Trust Score</p>
                      <p className="text-lg font-bold text-violet-600">{result.stages?.inquisitor?.trust_score || result.trust_score || 0}%</p>
                    </div>
                    <div className="text-sm">
                      <p className="text-gray-500">Fraud Risk</p>
                      <p className="text-lg font-bold text-gray-800">{result.fraud_risk || 'Low'}</p>
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>

            {/* Verified Skills Section */}
            {result.verified_skills && result.verified_skills.length > 0 && (
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 1.0 }}
                className="bg-white/90 backdrop-blur-xl border-2 border-gray-200 rounded-2xl p-8 shadow-lg"
              >
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <Code className="text-blue-500" size={28} />
                  Verified Skills ({result.verified_skills.length})
                </h3>
                <div className="flex flex-wrap gap-3">
                  {result.verified_skills.map((skill, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ delay: 1.1 + idx * 0.05 }}
                      className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg font-medium shadow-md hover:shadow-lg transition-all"
                    >
                      {skill}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Questions Section */}
            {result.questions && result.questions.length > 0 && (
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 1.2 }}
                className="bg-white/90 backdrop-blur-xl border-2 border-amber-200 rounded-2xl p-8 shadow-lg"
              >
                <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                  <Award className="text-amber-500" size={28} />
                  Suggested Interview Questions
                </h3>
                <div className="space-y-3">
                  {result.questions.slice(0, 5).map((question, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: 1.3 + idx * 0.1 }}
                      className="flex items-start gap-3 p-4 bg-amber-50 rounded-lg border border-amber-200"
                    >
                      <div className="w-6 h-6 rounded-full bg-amber-500 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
                        {idx + 1}
                      </div>
                      <p className="text-gray-700 text-sm leading-relaxed">{question}</p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Reset Button */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5 }}
              className="text-center"
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={resetPipeline}
                className="px-12 py-4 bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white rounded-2xl font-bold shadow-lg transition-all"
              >
                Verify Another Candidate
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VerificationPipeline;
