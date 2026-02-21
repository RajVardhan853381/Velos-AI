import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Search, Filter, Download, Eye, CheckCircle, XCircle, Clock, TrendingUp, Award, WifiOff } from 'lucide-react';
import { API_BASE } from '../config.js';

const CandidateCard = ({ candidate, onClick }) => {
  const statusColors = {
    passed: 'from-emerald-400 to-green-400',
    failed: 'from-red-400 to-rose-400',
    pending: 'from-amber-400 to-orange-400',
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02, y: -4 }}
      onClick={onClick}
      className="bg-white/60 backdrop-blur-xl border border-cyan-100/50 rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all cursor-pointer group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${statusColors[candidate.status] || 'from-slate-400 to-slate-500'} flex items-center justify-center shadow-md`}>
            <span className="text-white font-bold text-lg">{(candidate.id || '?').charAt(0).toUpperCase()}</span>
          </div>
          <div>
            <h3 className="font-bold text-slate-800 text-lg group-hover:text-cyan-600 transition-colors">
              {candidate.id}
            </h3>
            <p className="text-sm text-slate-500">{candidate.timestamp}</p>
          </div>
        </div>
        
        {candidate.status === 'passed' ? (
          <CheckCircle className="text-emerald-500" size={24} />
        ) : candidate.status === 'failed' ? (
          <XCircle className="text-red-500" size={24} />
        ) : (
          <Clock className="text-amber-500" size={24} />
        )}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-cyan-50/50 backdrop-blur-sm rounded-xl p-3 border border-cyan-100/50">
          <div className="text-xs text-slate-600 mb-1">Trust Score</div>
          <div className="text-2xl font-bold text-cyan-600">{candidate.trust_score}%</div>
        </div>
        <div className="bg-cyan-50/50 backdrop-blur-sm rounded-xl p-3 border border-cyan-100/50">
          <div className="text-xs text-slate-600 mb-1">Skill Match</div>
          <div className="text-2xl font-bold text-cyan-600">{candidate.skill_match}%</div>
        </div>
      </div>

      <div className="flex gap-2">
        {Object.entries(candidate.stages || {}).map(([agent, data]) => (
          <div
            key={agent}
            className={`flex-1 px-2 py-1 rounded-lg text-center text-xs font-semibold ${
              data.status === 'passed'
                ? 'bg-emerald-100/80 text-emerald-700'
                : data.status === 'failed'
                ? 'bg-red-100/80 text-red-700'
                : 'bg-slate-100/80 text-slate-600'
            }`}
          >
            {agent.charAt(0).toUpperCase()}
          </div>
        ))}
      </div>
    </motion.div>
  );
};

const CandidateDetail = ({ candidate, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white/90 backdrop-blur-xl border border-cyan-200 rounded-3xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
      >
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-slate-800 mb-2">{candidate.id}</h2>
            <p className="text-slate-600">Verification Details</p>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl p-6 border border-cyan-200">
            <Award className="text-cyan-600 mb-2" size={32} />
            <div className="text-sm text-slate-600 mb-1">Trust Score</div>
            <div className="text-4xl font-bold text-cyan-600">{candidate.trust_score}%</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-200">
            <TrendingUp className="text-purple-600 mb-2" size={32} />
            <div className="text-sm text-slate-600 mb-1">Skill Match</div>
            <div className="text-4xl font-bold text-purple-600">{candidate.skill_match}%</div>
          </div>
        </div>

        {/* Agent Stages */}
        <div className="mb-6">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Agent Pipeline</h3>
          <div className="space-y-3">
            {Object.entries(candidate.stages || {}).map(([agent, data]) => (
              <div
                key={agent}
                className="bg-white/60 backdrop-blur-sm border border-cyan-100 rounded-xl p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-slate-800 capitalize">{agent}</div>
                    {data.matched_skills && (
                      <div className="text-xs text-slate-600 mt-1">
                        Skills: {data.matched_skills.join(', ')}
                      </div>
                    )}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    data.status === 'passed'
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {data.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Questions */}
        {candidate.questions && candidate.questions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-bold text-slate-800 mb-4">Verification Questions</h3>
            <div className="space-y-2">
              {candidate.questions.map((question, index) => (
                <div key={index} className="bg-cyan-50/50 backdrop-blur-sm rounded-xl p-4 border border-cyan-100">
                  <div className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-cyan-500 text-white flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </span>
                    <p className="text-sm text-slate-700">{question}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Redacted Resume Preview */}
        {candidate.redacted_resume && (
          <div>
            <h3 className="text-lg font-bold text-slate-800 mb-4">Redacted Resume</h3>
            <div className="bg-slate-50/50 backdrop-blur-sm rounded-xl p-4 border border-slate-200 max-h-48 overflow-y-auto">
              <pre className="text-xs text-slate-600 whitespace-pre-wrap font-mono">
                {candidate.redacted_resume.substring(0, 500)}...
              </pre>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

const Candidates = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [fetchError, setFetchError] = useState(null);

  useEffect(() => {
    fetchCandidates();
    const interval = setInterval(fetchCandidates, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/candidates`);
      if (response.ok) {
        const data = await response.json();
        setCandidates(data.candidates || []);
        setFetchError(null);
      } else {
        setCandidates([]);
        setFetchError(`Failed to load candidates (HTTP ${response.status})`);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
      setCandidates([]);
      setFetchError('Unable to reach the server. Candidate list unavailable.');
      setLoading(false);
    }
  };

  const filteredCandidates = candidates.filter(c => {
    const matchesSearch = searchTerm === '' || (c.id ?? '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || c.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const stats = {
    total: candidates.length,
    passed: candidates.filter(c => c.status === 'passed').length,
    failed: candidates.filter(c => c.status === 'failed').length,
    avgTrust: candidates.length > 0 ? Math.round(candidates.reduce((sum, c) => sum + (c.trust_score || 0), 0) / candidates.length) : 0,
  };

  const exportCSV = () => {
    const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    const header = ['ID', 'Status', 'Trust Score', 'Skill Match', 'Timestamp'];
    const rows = candidates.map(c => [
      escape(c.id), escape(c.status), escape(c.trust_score), escape(c.skill_match), escape(c.timestamp)
    ]);
    const csv = [header.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'candidates.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Fetch Error Banner */}
      {fetchError && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-5 py-3 bg-red-50 border border-red-200 rounded-2xl text-red-700"
        >
          <WifiOff size={18} className="flex-shrink-0" />
          <span className="text-sm font-medium flex-1">{fetchError}</span>
          <button onClick={() => setFetchError(null)} className="text-red-400 hover:text-red-600 transition-colors text-lg leading-none">&times;</button>
        </motion.div>
      )}
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-cyan-50/70 to-blue-50/70 backdrop-blur-xl border border-cyan-100/50 rounded-3xl p-8 shadow-lg"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-400 flex items-center justify-center shadow-lg animate-float">
              <Users className="text-white" size={32} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-800">Candidates</h1>
              <p className="text-slate-600 mt-1">View all verified candidates</p>
            </div>
          </div>
          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={exportCSV}
              className="flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm border border-cyan-200 rounded-xl font-medium text-slate-700 shadow-sm transition-all"
            >
              <Download size={18} />
              Export
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', value: stats.total, color: 'from-blue-400 to-cyan-400', icon: Users },
          { label: 'Passed', value: stats.passed, color: 'from-emerald-400 to-green-400', icon: CheckCircle },
          { label: 'Failed', value: stats.failed, color: 'from-red-400 to-rose-400', icon: XCircle },
          { label: 'Avg Trust', value: `${stats.avgTrust}%`, color: 'from-purple-400 to-pink-400', icon: Award },
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.05 }}
            className="bg-white/60 backdrop-blur-xl border border-cyan-100/50 rounded-2xl p-6 shadow-sm"
          >
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mb-3 shadow-md`}>
              <stat.icon className="text-white" size={24} />
            </div>
            <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl border border-cyan-100/50 rounded-2xl p-6 shadow-sm"
      >
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search candidates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-cyan-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-all"
            />
          </div>
          <div className="flex gap-2">
            {['all', 'passed', 'failed', 'pending'].map((status) => (
              <motion.button
                key={status}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilterStatus(status)}
                className={`px-4 py-2 rounded-xl font-medium transition-all backdrop-blur-sm ${
                  filterStatus === status
                    ? 'bg-cyan-500 text-white shadow-md'
                    : 'bg-white/80 text-slate-600 hover:bg-white border border-cyan-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Candidates Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-cyan-200 border-t-cyan-500 rounded-full animate-spin"></div>
          </div>
        ) : filteredCandidates.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            No candidates found
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCandidates.map((candidate, index) => (
              <CandidateCard
                key={candidate.id}
                candidate={candidate}
                onClick={() => setSelectedCandidate(candidate)}
              />
            ))}
          </div>
        )}
      </motion.div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedCandidate && (
          <CandidateDetail
            candidate={selectedCandidate}
            onClose={() => setSelectedCandidate(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default Candidates;
