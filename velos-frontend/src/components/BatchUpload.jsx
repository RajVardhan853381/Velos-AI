import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileArchive, CheckCircle, XCircle, Clock, TrendingUp, Users, Download } from 'lucide-react';
import { API_BASE } from '../config.js';

const BatchUpload = () => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [fileError, setFileError] = useState('');
  
  // Use ref to track interval and prevent memory leaks
  const progressIntervalRef = useRef(null);
  const fileInputRef = useRef(null);
  const isMountedRef = useRef(true);

  // Cleanup interval on component unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.zip')) {
        setFile(droppedFile);
        setFileError('');
      } else {
        setFileError('Please upload a ZIP file');
      }
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.endsWith('.zip')) {
        setFile(selectedFile);
        setFileError('');
      } else {
        setFileError('Please upload a ZIP file');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    // Simulate progress with proper cleanup
    progressIntervalRef.current = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          if (progressIntervalRef.current) {
            clearInterval(progressIntervalRef.current);
            progressIntervalRef.current = null;
          }
          return prev;
        }
        return Math.min(prev + 10, 100); // Ensure progress doesn't exceed 100%
      });
    }, 200);

    try {
      const response = await fetch(`${API_BASE}/api/batch-upload`, {
        method: 'POST',
        body: formData,
      });

      // Clear interval on completion
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setProgress(100);

      if (response.ok) {
        const data = await response.json();
        // Backend returns { success, batch_result: { total, processed, passed, failed, ... } }
        // Normalize to the shape the UI expects
        const raw = data.batch_result || data;
        const normalized = {
          total_processed: raw.processed ?? raw.total_processed ?? 0,
          passed: raw.passed ?? 0,
          failed: raw.failed ?? 0,
          average_score: raw.average_score ?? null,
          results: raw.results ?? [],
          summary: raw.summary ?? '',
        };
        setTimeout(() => {
          if (isMountedRef.current) {
            setResults(normalized);
            setUploading(false);
          }
        }, 500);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      // Ensure interval is cleared on error
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
        progressIntervalRef.current = null;
      }
      setUploading(false);
      setFileError('Upload failed. Please try again.');
    }
  };

  const handleReset = () => {
    setFile(null);
    setResults(null);
    setProgress(0);
    setFileError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const downloadReport = () => {
    if (!results) return;
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `batch-results-${Date.now()}.json`;
    link.click();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-50/70 to-pink-50/70 backdrop-blur-xl border border-purple-100/50 rounded-3xl p-8 shadow-lg"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-lg animate-float">
            <FileArchive className="text-white" size={32} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Batch Upload</h1>
            <p className="text-slate-600 mt-1">Upload ZIP files with multiple resumes for bulk verification</p>
          </div>
        </div>
      </motion.div>

      {!results ? (
        <>
          {/* Upload Zone */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white/60 backdrop-blur-xl border border-purple-100/50 rounded-3xl p-8 shadow-sm"
          >
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 ${
                dragActive
                  ? 'border-purple-400 bg-purple-50/80'
                  : 'border-purple-200 bg-purple-50/30 hover:border-purple-300 hover:bg-purple-50/50'
              }`}
            >
              <input
                type="file"
                id="file-upload"
                ref={fileInputRef}
                accept=".zip"
                onChange={handleChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />

              <div className="text-center">
                <motion.div
                  animate={{
                    y: dragActive ? -10 : 0,
                    scale: dragActive ? 1.1 : 1,
                  }}
                  className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-400 mb-6 shadow-lg"
                >
                  <Upload className="text-white" size={40} />
                </motion.div>

                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  {file ? file.name : 'Drop your ZIP file here'}
                </h3>
                <p className="text-slate-600 mb-4">
                  {file ? `Size: ${(file.size / 1024 / 1024).toFixed(2)} MB` : 'or click to browse'}
                </p>

                {!file && (
                  <p className="text-sm text-slate-500">
                    Supported format: ZIP files containing resumes and job descriptions
                  </p>
                )}
              </div>
            </div>

            {fileError && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm"
              >
                <XCircle size={16} className="flex-shrink-0" />
                {fileError}
              </motion.div>
            )}

            {file && !uploading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4 mt-6"
              >
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleUpload}
                  className="flex-1 py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold rounded-xl shadow-lg transition-all"
                >
                  Start Batch Verification
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleReset}
                  className="px-6 py-4 bg-white/80 hover:bg-white backdrop-blur-sm border border-purple-200 text-slate-700 font-medium rounded-xl shadow-sm transition-all"
                >
                  Clear
                </motion.button>
              </motion.div>
            )}

            {uploading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-6 space-y-4"
              >
                <div className="flex items-center justify-between text-sm text-slate-700">
                  <span className="font-medium">Processing...</span>
                  <span className="font-bold">{progress}%</span>
                </div>
                <div className="h-3 bg-purple-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-shimmer"
                  />
                </div>
                <p className="text-center text-sm text-slate-600">
                  Extracting files and running verification pipeline...
                </p>
              </motion.div>
            )}
          </motion.div>

          {/* Instructions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/60 backdrop-blur-xl border border-purple-100/50 rounded-2xl p-6 shadow-sm"
          >
            <h3 className="font-bold text-slate-800 mb-4 text-lg">How to prepare your ZIP file:</h3>
            <ul className="space-y-3">
              {[
                'Create a ZIP archive containing resume files (PDF, DOC, DOCX, TXT)',
                'Optionally include a job_description.txt file for targeted matching',
                'Each resume will be processed through the 3-agent verification pipeline',
                'Maximum file size: 50MB | Maximum files: 100 resumes per batch',
                'Results include trust scores, skill matching, and verification questions',
              ].map((instruction, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="flex items-start gap-3 text-slate-700"
                >
                  <CheckCircle className="text-purple-500 flex-shrink-0 mt-0.5" size={20} />
                  <span>{instruction}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </>
      ) : (
        /* Results */
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Processed', value: results.total_processed || 0, color: 'from-blue-400 to-cyan-400', icon: Users },
              { label: 'Passed', value: results.passed || 0, color: 'from-emerald-400 to-green-400', icon: CheckCircle },
              { label: 'Failed', value: results.failed || 0, color: 'from-red-400 to-rose-400', icon: XCircle },
              { label: 'Avg Score', value: `${results.average_score || 0}%`, color: 'from-purple-400 to-pink-400', icon: TrendingUp },
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white/60 backdrop-blur-xl border border-purple-100/50 rounded-2xl p-6 shadow-sm"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mb-3 shadow-md`}>
                  <stat.icon className="text-white" size={24} />
                </div>
                <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-slate-800">{stat.value}</p>
              </motion.div>
            ))}
          </div>

          {/* Results Table */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/60 backdrop-blur-xl border border-purple-100/50 rounded-2xl p-6 shadow-sm"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-800">Verification Results</h2>
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={downloadReport}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-xl shadow-md transition-all"
                >
                  <Download size={18} />
                  Download Report
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleReset}
                  className="px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm border border-purple-200 text-slate-700 font-medium rounded-xl shadow-sm transition-all"
                >
                  Upload Another
                </motion.button>
              </div>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {(results.results || []).map((result, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.03 }}
                  className="bg-purple-50/50 backdrop-blur-sm border border-purple-100 rounded-xl p-4"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg ${
                        result.status === 'passed'
                          ? 'bg-emerald-100'
                          : result.status === 'failed'
                          ? 'bg-red-100'
                          : 'bg-amber-100'
                      } flex items-center justify-center`}>
                        {result.status === 'passed' ? (
                          <CheckCircle className="text-emerald-600" size={20} />
                        ) : result.status === 'failed' ? (
                          <XCircle className="text-red-600" size={20} />
                        ) : (
                          <Clock className="text-amber-600" size={20} />
                        )}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-800">
                          {result.candidate_id || `Candidate ${index + 1}`}
                        </div>
                        <div className="text-sm text-slate-600">
                          {result.filename || 'Unknown file'}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-600">
                        {result.trust_score || 0}%
                      </div>
                      <div className="text-xs text-slate-600">Trust Score</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default BatchUpload;
