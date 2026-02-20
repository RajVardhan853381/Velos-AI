import React, { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, Upload, Sparkles, CheckCircle2, AlertTriangle,
  Target, Star, Brain, Zap, ChevronRight, X,
  Award, Search, RefreshCw
} from 'lucide-react';
import { API_BASE } from '../config.js';

const glass = {
  background: 'rgba(255,255,255,0.35)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.6)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
};

const ScoreRing = ({ score }) => {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color =
    score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <div className="relative flex items-center justify-center">
      <svg viewBox="0 0 140 140" className="w-32 h-32 sm:w-[140px] sm:h-[140px] -rotate-90">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="rgba(0,0,0,0.06)" strokeWidth="10" />
        <motion.circle
          cx="70" cy="70" r={radius}
          fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <motion.span
          className="text-4xl font-black"
          style={{ color }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, type: 'spring' }}
        >
          {score}
        </motion.span>
        <span className="text-xs text-gray-500 font-medium">/ 100</span>
      </div>
    </div>
  );
};

const SkillTag = ({ skill, type }) => (
  <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${
    type === 'match'
      ? 'bg-green-100/80 text-green-700 border border-green-200'
      : 'bg-red-100/80 text-red-600 border border-red-200'
  }`}>
    {type === 'match' ? <CheckCircle2 size={11} /> : <X size={11} />}
    {skill}
  </span>
);

export default function ResumeScreener() {
  const [jd, setJd] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const fileRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setResumeFile(file);
      setInputMode('file');
    }
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setResumeFile(file);
      setInputMode('file');
    }
  };

  const handleScreen = async () => {
    setError('');
    setResult(null);
    setLoading(true);

    try {
      if (inputMode === 'file' && resumeFile) {
        const formData = new FormData();
        formData.append('job_description', jd);
        formData.append('resume_file', resumeFile);
        const res = await fetch(`${API_BASE}/api/screen-resume-file`, {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Screening failed');
        setResult(data);
      } else {
        const res = await fetch(`${API_BASE}/api/screen-resume`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume_text: resumeText, job_description: jd }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Screening failed');
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const canSubmit = jd.trim().length >= 20 && (
    (inputMode === 'text' && resumeText.trim().length >= 50) ||
    (inputMode === 'file' && resumeFile)
  );

  const verdictColor = result ? (
    result.compatibility_score >= 80 ? 'text-green-600' :
    result.compatibility_score >= 60 ? 'text-blue-600' :
    result.compatibility_score >= 40 ? 'text-amber-600' : 'text-red-600'
  ) : '';

  const verdictBg = result ? (
    result.compatibility_score >= 80 ? 'from-green-50 to-emerald-50 border-green-200' :
    result.compatibility_score >= 60 ? 'from-blue-50 to-indigo-50 border-blue-200' :
    result.compatibility_score >= 40 ? 'from-amber-50 to-yellow-50 border-amber-200' :
    'from-red-50 to-rose-50 border-red-200'
  ) : '';

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30">
            <Search className="text-white" size={20} />
          </div>
          <div>
            <h2 className="text-2xl font-black text-gray-900">GenAI Resume Screener</h2>
            <p className="text-sm text-gray-500">Context-aware matching — finds hidden gem candidates</p>
          </div>
        </div>
      </motion.div>

      {!result ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Job Description */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
            <div className="rounded-2xl p-5" style={glass}>
              <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                <Target size={15} className="text-purple-500" /> Job Description
              </label>
              <textarea
                value={jd}
                onChange={e => setJd(e.target.value)}
                rows={14}
                placeholder="Paste the job description here..."
                className="w-full rounded-xl p-3 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-purple-300 resize-none text-gray-800 placeholder-gray-400"
              />
              <p className="text-xs text-gray-400 mt-1 text-right">{jd.length} chars</p>
            </div>
          </motion.div>

          {/* Right: Resume */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}>
            <div className="rounded-2xl p-5 h-full" style={glass}>
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                  <FileText size={15} className="text-indigo-500" /> Resume
                </label>
                <div className="flex gap-2">
                  {['text', 'file'].map(m => (
                    <button
                      key={m}
                      onClick={() => setInputMode(m)}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                        inputMode === m
                          ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow'
                          : 'bg-white/60 text-gray-600 border border-white/80'
                      }`}
                    >
                      {m === 'text' ? 'Paste Text' : 'Upload File'}
                    </button>
                  ))}
                </div>
              </div>

              <AnimatePresence mode="wait">
                {inputMode === 'text' ? (
                  <motion.div key="text" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <textarea
                      value={resumeText}
                      onChange={e => setResumeText(e.target.value)}
                      rows={13}
                      placeholder="Paste resume text here..."
                      className="w-full rounded-xl p-3 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-indigo-300 resize-none text-gray-800 placeholder-gray-400"
                    />
                    <p className="text-xs text-gray-400 mt-1 text-right">{resumeText.length} chars</p>
                  </motion.div>
                ) : (
                  <motion.div key="file" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <div
                      onClick={() => fileRef.current?.click()}
                      onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                      onDragLeave={() => setDragOver(false)}
                      onDrop={handleDrop}
                      className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
                        dragOver ? 'border-purple-400 bg-purple-50/50' : 'border-gray-200/80 hover:border-purple-300 bg-white/30'
                      }`}
                    >
                      {resumeFile ? (
                        <div className="space-y-2">
                          <CheckCircle2 className="mx-auto text-green-500" size={36} />
                          <p className="font-semibold text-gray-800">{resumeFile.name}</p>
                          <p className="text-sm text-gray-500">{(resumeFile.size / 1024).toFixed(1)} KB</p>
                          <button
                            onClick={e => { e.stopPropagation(); setResumeFile(null); }}
                            className="text-xs text-red-500 hover:underline"
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <Upload className="mx-auto text-gray-400" size={36} />
                          <p className="text-gray-600 font-medium">Drop PDF, DOCX, or TXT here</p>
                          <p className="text-xs text-gray-400">or click to browse</p>
                        </div>
                      )}
                    </div>
                    <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFileSelect} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      ) : null}

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="flex items-center gap-3 p-4 rounded-xl bg-red-50/80 border border-red-200 text-red-700 text-sm">
            <AlertTriangle size={16} />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Screen Button */}
      {!result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="flex justify-center">
          <motion.button
            onClick={handleScreen}
            disabled={!canSubmit || loading}
            whileHover={canSubmit && !loading ? { scale: 1.04 } : {}}
            whileTap={canSubmit && !loading ? { scale: 0.97 } : {}}
            className="flex items-center gap-3 px-10 py-4 rounded-2xl font-bold text-white text-lg shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
              boxShadow: '0 6px 24px rgba(124, 58, 237, 0.4)'
            }}
          >
            {loading ? (
              <>
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                  <RefreshCw size={20} />
                </motion.div>
                Analyzing with AI...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Screen Resume
                <ChevronRight size={20} />
              </>
            )}
          </motion.button>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-5">
            {/* Score + Verdict Hero */}
            <div className={`rounded-2xl p-6 bg-gradient-to-br border ${verdictBg}`}>
              <div className="flex flex-col md:flex-row items-center gap-8">
                <ScoreRing score={result.compatibility_score} />
                <div className="flex-1 text-center md:text-left">
                  <p className="text-sm font-semibold text-gray-500 mb-1">Compatibility Score</p>
                  <h3 className={`text-3xl font-black ${verdictColor} mb-2`}>{result.verdict}</h3>
                  <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold ${
                    result.recommendation === 'Strongly Recommend' ? 'bg-green-500 text-white' :
                    result.recommendation === 'Recommend' ? 'bg-blue-500 text-white' :
                    result.recommendation === 'Consider' ? 'bg-amber-500 text-white' : 'bg-gray-400 text-white'
                  }`}>
                    <Award size={14} />
                    {result.recommendation}
                  </div>
                  {result.experience_years_estimated != null && (
                    <p className="text-sm text-gray-500 mt-2">
                      Est. experience: ~{result.experience_years_estimated} year{result.experience_years_estimated !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>

                {/* Hidden Gem Badge */}
                {result.hidden_gem && (
                  <motion.div
                    initial={{ scale: 0, rotate: -10 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: 'spring', delay: 0.3 }}
                    className="relative"
                  >
                    <div className="flex flex-col items-center gap-2 p-5 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-lg shadow-amber-400/40">
                      <motion.div animate={{ rotate: [0, 15, -15, 0] }} transition={{ duration: 2, repeat: Infinity }}>
                        <Star size={32} fill="white" />
                      </motion.div>
                      <span className="text-lg font-black">Hidden Gem!</span>
                      <span className="text-xs text-amber-100 text-center max-w-[140px]">
                        {result.hidden_gem_reason}
                      </span>
                    </div>
                    <motion.div
                      animate={{ opacity: [0.4, 1, 0.4] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="absolute inset-0 bg-amber-400/30 rounded-2xl blur-xl -z-10"
                    />
                  </motion.div>
                )}
              </div>
            </div>

            {/* 3-Bullet Summary */}
            <div className="rounded-2xl p-5" style={glass}>
              <h4 className="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2">
                <Brain size={15} className="text-purple-500" /> AI Analysis Summary
              </h4>
              <div className="space-y-3">
                {(result.summary_bullets || []).map((bullet, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * i }}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white/50"
                  >
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0 ${
                      i === 0 ? 'bg-purple-500' : i === 1 ? 'bg-indigo-500' : 'bg-blue-500'
                    }`}>
                      {i + 1}
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed">{bullet}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="rounded-2xl p-5" style={glass}>
                <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                  <CheckCircle2 size={14} className="text-green-500" /> Matching Skills
                </h4>
                <div className="flex flex-wrap gap-2">
                  {(result.key_matching_skills || []).length > 0 ? (result.key_matching_skills || []).map(s => (
                    <SkillTag key={s} skill={s} type="match" />
                  )) : <p className="text-sm text-gray-400">None identified</p>}
                </div>
              </div>
              <div className="rounded-2xl p-5" style={glass}>
                <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                  <AlertTriangle size={14} className="text-red-400" /> Missing Skills
                </h4>
                <div className="flex flex-wrap gap-2">
                  {(result.missing_skills || []).length > 0 ? (result.missing_skills || []).map(s => (
                    <SkillTag key={s} skill={s} type="missing" />
                  )) : <p className="text-sm text-green-600 font-medium">No critical gaps!</p>}
                </div>
              </div>
            </div>

            {/* Re-screen button */}
            <div className="flex justify-center">
              <button
                onClick={() => { setResult(null); setError(''); }}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/60 border border-white/80 text-gray-700 font-semibold hover:bg-white/80 transition-all text-sm"
              >
                <RefreshCw size={15} />
                Screen Another Resume
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
