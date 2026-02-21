import React, { useState } from 'react';
import { API_BASE } from '../config.js';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, Eye, EyeOff, Download, CheckCircle, AlertTriangle,
  Trash2, PlusCircle, MinusCircle, FileText, Lock, BarChart3,
  Search, ChevronRight
} from 'lucide-react';

// PII category colors
const getPIICategory = (type) => {
  const categories = {
    'EMAIL': { color: 'bg-blue-100 border-blue-500/40 text-blue-700', icon: '📧', label: 'Email' },
    'PHONE': { color: 'bg-green-100 border-green-500/40 text-green-700', icon: '📱', label: 'Phone' },
    'NAME': { color: 'bg-purple-100 border-purple-500/40 text-gray-600', icon: '👤', label: 'Name' },
    'LOCATION': { color: 'bg-yellow-100 border-yellow-500/40 text-yellow-700', icon: '📍', label: 'Location' },
    'DATE': { color: 'bg-pink-100 border-pink-500/40 text-pink-700', icon: '📅', label: 'Date' },
    'SSN': { color: 'bg-red-100 border-red-500/40 text-gray-600', icon: '🔢', label: 'SSN' },
    'ADDRESS': { color: 'bg-orange-100 border-orange-500/40 text-orange-700', icon: '🏠', label: 'Address' },
    'OTHER': { color: 'bg-gray-100 border-gray-400/40 text-gray-600', icon: '🔒', label: 'Other PII' }
  };
  
  return categories[type] || categories['OTHER'];
};

// Redaction statistics card
const RedactionStats = ({ stats }) => {
  const categories = [
    { key: 'email', label: 'Emails', icon: '📧', color: 'from-blue-500/20 to-indigo-500/20 border-blue-200/60' },
    { key: 'phone', label: 'Phone Numbers', icon: '📱', color: 'from-green-500/20 to-emerald-500/20 border-green-200/60' },
    { key: 'name', label: 'Names', icon: '👤', color: 'from-purple-500/20 to-pink-500/20 border-purple-200/60' },
    { key: 'location', label: 'Locations', icon: '📍', color: 'from-yellow-500/20 to-orange-500/20 border-yellow-200/60' }
  ];

  const totalRedacted = Object.values(stats || {}).reduce((sum, val) => sum + (typeof val === 'number' ? val : 0), 0);

  return (
    <div className="space-y-4">
      {/* Total */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-br from-white/40 to-white/30 border border-red-200/60 rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <Trash2 className="text-red-600" size={24} />
            </div>
            <div>
              <p className="text-gray-600 text-sm">Total PII Redacted</p>
              <p className="text-gray-900 text-3xl font-bold">{totalRedacted}</p>
            </div>
          </div>
          <CheckCircle className="text-red-600" size={32} />
        </div>
      </motion.div>

      {/* Category breakdown */}
      <div className="grid grid-cols-2 gap-3">
        {categories.map((cat, index) => (
          <motion.div
            key={cat.key}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`bg-gradient-to-br ${cat.color} border rounded-lg p-4`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{cat.icon}</span>
              <p className="text-gray-900/70 text-xs">{cat.label}</p>
            </div>
            <p className="text-gray-900 text-xl font-bold">{stats?.[cat.key] || 0}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Diff line component
const DiffLine = ({ line, index }) => {
  const isAddition = line.type === 'addition';
  const isDeletion = line.type === 'deletion';
  const isUnchanged = line.type === 'unchanged';

  const bgColor = isDeletion 
    ? 'bg-red-500/10 border-l-4 border-red-500'
    : isAddition 
    ? 'bg-green-500/10 border-l-4 border-green-500'
    : 'bg-transparent';

  const icon = isDeletion ? MinusCircle : isAddition ? PlusCircle : null;
  const iconColor = isDeletion ? 'text-red-600' : 'text-green-600';

  return (
    <motion.div
      initial={{ opacity: 0, x: isDeletion ? -10 : isAddition ? 10 : 0 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.01 }}
      className={`${bgColor} px-4 py-2 font-mono text-sm hover:bg-white/5 transition-all`}
    >
      <div className="flex items-start gap-3">
        <span className="text-gray-900/30 text-xs mt-1 w-8 flex-shrink-0">{index + 1}</span>
        {icon && <span className={`${iconColor} mt-1 flex-shrink-0`}>{React.createElement(icon, { size: 14 })}</span>}
        <span className={`flex-1 ${isDeletion ? 'text-gray-600 line-through' : isAddition ? 'text-green-700' : 'text-gray-900/70'}`}>
          {line.text}
        </span>
        {line.pii_type && (
          <span className={`px-2 py-0.5 ${getPIICategory(line.pii_type).color} border rounded text-xs font-semibold`}>
            {getPIICategory(line.pii_type).icon} {getPIICategory(line.pii_type).label}
          </span>
        )}
      </div>
    </motion.div>
  );
};

// Side-by-side view
const SideBySideView = ({ original, redacted }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Original */}
      <div className="bg-red-50 border border-red-200 rounded-xl overflow-hidden">
        <div className="bg-red-100 border-b border-red-200 px-4 py-3 flex items-center gap-2">
          <EyeOff className="text-red-600" size={18} />
          <h3 className="text-gray-700 font-semibold">Original (With PII)</h3>
        </div>
        <div className="p-4 max-h-96 overflow-y-auto">
          <pre className="text-gray-800 text-sm font-mono whitespace-pre-wrap leading-relaxed">
            {original}
          </pre>
        </div>
      </div>

      {/* Redacted */}
      <div className="bg-green-50 border border-green-200 rounded-xl overflow-hidden">
        <div className="bg-green-100 border-b border-green-200 px-4 py-3 flex items-center gap-2">
          <Eye className="text-green-600" size={18} />
          <h3 className="text-gray-700 font-semibold">Redacted (Zero-Bias)</h3>
        </div>
        <div className="p-4 max-h-96 overflow-y-auto">
          <pre className="text-gray-800 text-sm font-mono whitespace-pre-wrap leading-relaxed">
            {redacted}
          </pre>
        </div>
      </div>
    </div>
  );
};

// Unified diff view
const UnifiedDiffView = ({ diffLines }) => {
  return (
    <div className="bg-gray-50 border border-indigo-200 rounded-xl overflow-hidden">
      <div className="bg-indigo-50 border-b border-indigo-200 px-4 py-3 flex items-center gap-2">
        <FileText className="text-indigo-600" size={18} />
        <h3 className="text-gray-700 font-semibold">Unified Diff (Line-by-Line)</h3>
      </div>
      <div className="max-h-96 overflow-y-auto">
        {diffLines.map((line, index) => (
          <DiffLine key={index} line={line} index={index} />
        ))}
      </div>
    </div>
  );
};

// Main component
const ZeroBiasProof = () => {
  const [candidateId, setCandidateId] = useState('');
  const [diffData, setDiffData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('side-by-side'); // 'side-by-side' or 'unified'

  const fetchDiffData = async () => {
    if (!candidateId.trim()) {
      setError('Please enter a candidate ID');
      return;
    }

    setLoading(true);
    setError(null);
    setDiffData(null);

    try {
      // Use the richer trust-packet endpoint
      const response = await fetch(`${API_BASE}/api/candidates/${candidateId}/trust-packet`);

      if (response.ok) {
        const data = await response.json();

        // The endpoint returns { success, trust_packet: { diff_report, diff_stats, ... } }
        const tp = data.trust_packet;

        if (!tp) {
          setError('No trust packet found for this candidate. Run verification first.');
          return;
        }

        const diffReport = tp.diff_report;
        const diffStats = tp.diff_stats;

        if (!diffReport) {
          setError('No diff report found for this candidate. Redaction data may not be available.');
          return;
        }

        // Build redaction_stats from diff_report changes
        const changes = diffReport.changes || [];
        const redactionStats = { email: 0, phone: 0, name: 0, location: 0 };
        changes.forEach(change => {
          const piiType = (change.pii_type || '').toLowerCase();
          if (piiType === 'email') redactionStats.email++;
          else if (piiType === 'phone') redactionStats.phone++;
          else if (piiType === 'name') redactionStats.name++;
          else if (piiType === 'location') redactionStats.location++;
        });

        // Parse diff lines for unified view
        const diffLines = [];
        changes.forEach(change => {
          if (change.type === 'deletion') {
            diffLines.push({ type: 'deletion', text: change.original, pii_type: change.pii_type });
          } else if (change.type === 'addition') {
            diffLines.push({ type: 'addition', text: change.redacted, pii_type: change.pii_type });
          }
        });

        setDiffData({
          candidate_id: candidateId,
          original: tp.original_text || 'Original text not available',
          redacted: tp.redacted_text || 'Redacted text not available',
          diff_report: diffReport,
          diff_stats: diffStats,
          redaction_stats: redactionStats,
          diff_lines: diffLines
        });
      } else {
        setError(`Failed to fetch diff data for candidate ${candidateId}`);
      }
    } catch (err) {
      console.error('Failed to fetch diff data:', err);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const downloadDiffReport = () => {
    if (!diffData) return;

    try {
      const report = {
        candidate_id: diffData.candidate_id,
        diff_stats: diffData.diff_stats,
        redaction_stats: diffData.redaction_stats,
        changes: diffData.diff_report?.changes,
        generated_at: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${diffData.candidate_id}_zero_bias_proof.json`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to generate diff report download:', err);
    }
  };

  return (
    <div className="p-0">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-2">
          <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-2xl">
            <Shield className="text-white" size={32} />
          </div>
          <div>
            <h1 className="text-3xl md:text-5xl font-bold text-gray-900">Zero-Bias Proof</h1>
            <p className="text-gray-600 text-lg">Visual proof of PII redaction and bias removal</p>
          </div>
        </div>
      </motion.div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/40 backdrop-blur-xl border border-white/60 rounded-2xl p-6 mb-8"
      >
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            placeholder="Enter Candidate ID (e.g., CAND-A1B2C3D4)"
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchDiffData()}
            className="flex-1 px-6 py-4 bg-white border border-indigo-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
          <button
            onClick={fetchDiffData}
            disabled={loading}
            className="px-8 py-4 bg-gradient-to-r from-red-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-2xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Search size={20} />
            {loading ? 'Loading...' : 'Load Diff'}
          </button>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 border border-red-300 rounded-lg flex items-center gap-3"
          >
            <AlertTriangle className="text-red-500" size={20} />
            <p className="text-red-700">{error}</p>
          </motion.div>
        )}
      </motion.div>

      {/* Results */}
      {diffData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Stats sidebar */}
            <div className="lg:col-span-1">
              <RedactionStats stats={diffData.redaction_stats} />
              
              {/* Controls */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-4 space-y-3"
              >
                <div className="bg-white/40 backdrop-blur-xl border border-white/60 rounded-xl p-4">
                  <p className="text-gray-600 text-sm mb-3">View Mode</p>
                  <div className="space-y-2">
                    <button
                      onClick={() => setViewMode('side-by-side')}
                      className={`w-full flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                        viewMode === 'side-by-side'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white/60 text-gray-700 hover:bg-white'
                      }`}
                    >
                      <ChevronRight size={16} />
                      Side-by-Side
                    </button>
                    <button
                      onClick={() => setViewMode('unified')}
                      className={`w-full flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                        viewMode === 'unified'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white/60 text-gray-700 hover:bg-white'
                      }`}
                    >
                      <ChevronRight size={16} />
                      Unified Diff
                    </button>
                  </div>
                </div>

                <button
                  onClick={downloadDiffReport}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl transition-all shadow-lg"
                >
                  <Download size={18} />
                  Download Report
                </button>
              </motion.div>
            </div>

            {/* Diff viewer */}
            <div className="lg:col-span-2">
              <AnimatePresence mode="wait">
                {viewMode === 'side-by-side' ? (
                  <motion.div
                    key="side-by-side"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <SideBySideView
                      original={diffData.original}
                      redacted={diffData.redacted}
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    key="unified"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <UnifiedDiffView diffLines={diffData.diff_lines} />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Diff stats summary */}
              {diffData.diff_stats && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mt-6 bg-gradient-to-br from-white/40 to-white/30 border border-indigo-500/30 rounded-xl p-6"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <BarChart3 className="text-indigo-400" size={24} />
                    <h3 className="text-gray-900 text-xl font-bold">Redaction Summary</h3>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <MinusCircle className="text-red-600" size={16} />
                        <p className="text-gray-600 text-sm">Deletions</p>
                      </div>
                      <p className="text-gray-900 text-2xl font-bold">{diffData.diff_stats.deletions || 0}</p>
                    </div>
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <PlusCircle className="text-green-600" size={16} />
                        <p className="text-green-700 text-sm">Insertions</p>
                      </div>
                      <p className="text-gray-900 text-2xl font-bold">{diffData.diff_stats.insertions || 0}</p>
                    </div>
                    <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Lock className="text-purple-600" size={16} />
                        <p className="text-gray-600 text-sm">Redaction Rate</p>
                      </div>
                      <p className="text-gray-900 text-2xl font-bold">{diffData.diff_stats.redaction_rate || 0}%</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ZeroBiasProof;
