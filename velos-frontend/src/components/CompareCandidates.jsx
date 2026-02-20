import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GitCompare, Users, TrendingUp, Award, AlertCircle, CheckCircle, XCircle, BarChart3 } from 'lucide-react';
import { API_BASE } from '../config.js';

const glass = {
  background: 'rgba(255,255,255,0.35)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.6)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
};

const MetricBar = ({ label, value1, value2, name1, name2, color1, color2 }) => {
  const max = Math.max(value1, value2, 1);
  const percent1 = (value1 / max) * 100;
  const percent2 = (value2 / max) * 100;

  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-slate-600 mb-2">
        <span>{label}</span>
        <div className="flex gap-4">
          <span className="text-blue-600">{name1}: {value1}</span>
          <span className="text-emerald-600">{name2}: {value2}</span>
        </div>
      </div>
      <div className="flex gap-2">
        <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${percent1}%` }} transition={{ duration: 0.8, ease: "easeOut" }} className={`h-full ${color1} rounded-full`} />
        </div>
        <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${percent2}%` }} transition={{ duration: 0.8, ease: "easeOut" }} className={`h-full ${color2} rounded-full`} />
        </div>
      </div>
    </div>
  );
};

const CandidateCard = ({ candidate, side }) => {
  const getStatusIcon = (status) => {
    if (status === 'verified' || status === 'passed') return <CheckCircle className="text-green-500" size={20} />;
    if (status === 'flagged') return <AlertCircle className="text-amber-500" size={20} />;
    return <XCircle className="text-red-500" size={20} />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: side === 'left' ? -30 : 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl p-6 shadow-lg"
      style={glass}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white text-2xl font-bold shadow-md">
            {candidate?.name?.charAt(0) || '?'}
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-800">{candidate?.name || 'N/A'}</h3>
            <p className="text-slate-500 text-sm">{candidate?.role || 'N/A'}</p>
          </div>
        </div>
        {candidate?.status && getStatusIcon(candidate.status)}
      </div>

      <div className="space-y-3 mt-4">
        <div className="flex justify-between p-3 bg-white/50 rounded-xl border border-white/70">
          <span className="text-slate-600 text-sm">Trust Score</span>
          <span className="text-slate-800 font-bold">{candidate?.trust_score || 0}%</span>
        </div>
        <div className="flex justify-between p-3 bg-white/50 rounded-xl border border-white/70">
          <span className="text-slate-600 text-sm">Experience</span>
          <span className="text-slate-800 font-bold">{candidate?.experience || 0} years</span>
        </div>
        <div className="flex justify-between p-3 bg-white/50 rounded-xl border border-white/70">
          <span className="text-slate-600 text-sm">Skills Match</span>
          <span className="text-slate-800 font-bold">{candidate?.skill_match || candidate?.skills_match || 0}%</span>
        </div>
      </div>

      {candidate?.skills && candidate.skills.length > 0 && (
        <div className="mt-5">
          <p className="text-slate-500 text-xs font-semibold uppercase tracking-wide mb-2">Top Skills</p>
          <div className="flex flex-wrap gap-2">
            {candidate.skills.map((skill, idx) => (
              <span key={idx} className="px-3 py-1 bg-blue-50 border border-blue-100 text-blue-700 rounded-full text-xs font-medium">{skill}</span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

const CompareCandidates = () => {
  const [candidate1Id, setCandidate1Id] = useState('');
  const [candidate2Id, setCandidate2Id] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const compareNow = async () => {
    const id1 = candidate1Id.trim();
    const id2 = candidate2Id.trim();

    if (!id1 || !id2) {
      setError('Please enter both candidate IDs');
      return;
    }

    if (id1 === id2) {
      setError('Cannot compare a candidate with themselves. Please enter different IDs.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate1_id: id1, candidate2_id: id2 })
      });

      if (response.ok) {
        const data = await response.json();
        setComparison(data);
      } else if (response.status === 404) {
        setError('One or both candidate IDs not found');
      } else {
        setError('Failed to compare candidates. Please try again.');
      }
    } catch (err) {
      console.error('Failed to compare:', err);
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') compareNow();
  };

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
            <GitCompare className="text-white" size={22} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Compare Candidates</h1>
            <p className="text-slate-500 text-sm">Side-by-side candidate analysis</p>
          </div>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl p-6 shadow-sm"
        style={glass}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="cmp-id1" className="block text-xs font-semibold text-slate-600 mb-1.5">Candidate 1 ID</label>
            <input
              id="cmp-id1"
              type="text"
              placeholder="e.g., CAND-A1B2"
              value={candidate1Id}
              onChange={(e) => setCandidate1Id(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-5 py-3.5 bg-white/60 border border-white/80 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 transition-all text-sm"
            />
          </div>
          <div>
            <label htmlFor="cmp-id2" className="block text-xs font-semibold text-slate-600 mb-1.5">Candidate 2 ID</label>
            <input
              id="cmp-id2"
              type="text"
              placeholder="e.g., CAND-E5F6"
              value={candidate2Id}
              onChange={(e) => setCandidate2Id(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full px-5 py-3.5 bg-white/60 border border-white/80 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 transition-all text-sm"
            />
          </div>
        </div>
        {error && (
          <div className="mb-3 flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            <AlertCircle size={16} />
            {error}
          </div>
        )}
        <motion.button
          onClick={compareNow}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="w-full px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Comparing...' : 'Compare Now'}
        </motion.button>
      </motion.div>

      {comparison && (
        <div className="space-y-6">
          {comparison.winner && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="rounded-2xl p-6 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 shadow-md"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full flex items-center justify-center shadow-md">
                  <Award className="text-white" size={28} />
                </div>
                <div>
                  <p className="text-amber-600 text-xs font-bold uppercase tracking-wide mb-0.5">Recommended Candidate</p>
                  <h2 className="text-2xl font-bold text-slate-800">{comparison.winner}</h2>
                  <p className="text-slate-500 text-sm mt-0.5">{comparison.reason || 'Higher overall performance'}</p>
                </div>
              </div>
            </motion.div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CandidateCard candidate={comparison.candidate1} side="left" />
            <CandidateCard candidate={comparison.candidate2} side="right" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="rounded-2xl p-6 shadow-sm"
            style={glass}
          >
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 className="text-slate-600" size={22} />
              <h2 className="text-xl font-bold text-slate-800">Performance Comparison</h2>
            </div>
            <div className="space-y-4">
              <MetricBar
                label="Trust Score"
                value1={comparison.candidate1?.trust_score || 0}
                value2={comparison.candidate2?.trust_score || 0}
                name1={comparison.candidate1?.name || 'C1'}
                name2={comparison.candidate2?.name || 'C2'}
                color1="bg-gradient-to-r from-blue-400 to-indigo-500"
                color2="bg-gradient-to-r from-emerald-400 to-teal-500"
              />
              <MetricBar
                label="Skills Match"
                value1={comparison.candidate1?.skill_match || comparison.candidate1?.skills_match || 0}
                value2={comparison.candidate2?.skill_match || comparison.candidate2?.skills_match || 0}
                name1={comparison.candidate1?.name || 'C1'}
                name2={comparison.candidate2?.name || 'C2'}
                color1="bg-gradient-to-r from-blue-500 to-indigo-600"
                color2="bg-gradient-to-r from-emerald-500 to-teal-600"
              />
              <MetricBar
                label="Experience (Years)"
                value1={comparison.candidate1?.experience || 0}
                value2={comparison.candidate2?.experience || 0}
                name1={comparison.candidate1?.name || 'C1'}
                name2={comparison.candidate2?.name || 'C2'}
                color1="bg-gradient-to-r from-violet-400 to-purple-500"
                color2="bg-gradient-to-r from-pink-400 to-rose-500"
              />
            </div>
          </motion.div>

          {comparison.skills_comparison && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="rounded-2xl p-6 shadow-sm"
              style={glass}
            >
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="text-slate-600" size={22} />
                <h2 className="text-xl font-bold text-slate-800">Skills Analysis</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {comparison.skills_comparison.common && comparison.skills_comparison.common.length > 0 && (
                  <div>
                    <p className="text-emerald-600 font-semibold text-sm mb-3">Common Skills</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.common.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-emerald-50 border border-emerald-100 rounded-lg text-emerald-700 text-sm">{skill}</div>
                      ))}
                    </div>
                  </div>
                )}
                {comparison.skills_comparison.unique_to_1 && comparison.skills_comparison.unique_to_1.length > 0 && (
                  <div>
                    <p className="text-blue-600 font-semibold text-sm mb-3">Unique to {comparison.candidate1?.name || 'C1'}</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.unique_to_1.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-blue-50 border border-blue-100 rounded-lg text-blue-700 text-sm">{skill}</div>
                      ))}
                    </div>
                  </div>
                )}
                {comparison.skills_comparison.unique_to_2 && comparison.skills_comparison.unique_to_2.length > 0 && (
                  <div>
                    <p className="text-violet-600 font-semibold text-sm mb-3">Unique to {comparison.candidate2?.name || 'C2'}</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.unique_to_2.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-violet-50 border border-violet-100 rounded-lg text-violet-700 text-sm">{skill}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {!comparison && !loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
          <GitCompare className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-400 text-base">Enter two candidate IDs to start comparison</p>
        </motion.div>
      )}
    </div>
  );
};

export default CompareCandidates;
