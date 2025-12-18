import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GitCompare, Users, TrendingUp, Award, AlertCircle, CheckCircle, XCircle, BarChart3 } from 'lucide-react';

const MetricBar = ({ label, value1, value2, name1, name2, color1, color2 }) => {
  const max = Math.max(value1, value2, 1);
  const percent1 = (value1 / max) * 100;
  const percent2 = (value2 / max) * 100;

  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-teal-300 mb-2">
        <span>{label}</span>
        <div className="flex gap-4">
          <span className="text-cyan-400">{name1}: {value1}</span>
          <span className="text-emerald-400">{name2}: {value2}</span>
        </div>
      </div>
      <div className="flex gap-2">
        <div className="flex-1 bg-teal-900/30 rounded-full h-3 overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${percent1}%` }} transition={{ duration: 0.8, ease: "easeOut" }} className={`h-full ${color1} rounded-full`} />
        </div>
        <div className="flex-1 bg-teal-900/30 rounded-full h-3 overflow-hidden">
          <motion.div initial={{ width: 0 }} animate={{ width: `${percent2}%` }} transition={{ duration: 0.8, ease: "easeOut" }} className={`h-full ${color2} rounded-full`} />
        </div>
      </div>
    </div>
  );
};

const CandidateCard = ({ candidate, color, side }) => {
  const getStatusIcon = (status) => {
    if (status === 'verified') return <CheckCircle className="text-green-400" size={20} />;
    if (status === 'flagged') return <AlertCircle className="text-yellow-400" size={20} />;
    return <XCircle className="text-red-400" size={20} />;
  };

  return (
    <motion.div initial={{ opacity: 0, x: side === 'left' ? -30 : 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }} className={`bg-gradient-to-br ${color} backdrop-blur-xl border border-teal-700/50 rounded-2xl p-6 shadow-2xl`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 rounded-full bg-teal-800/50 flex items-center justify-center text-white text-2xl font-bold border-2 border-teal-500">{candidate?.name?.charAt(0) || '?'}</div>
          <div>
            <h3 className="text-2xl font-bold text-white">{candidate?.name || 'N/A'}</h3>
            <p className="text-teal-300">{candidate?.role || 'N/A'}</p>
          </div>
        </div>
        {candidate?.status && getStatusIcon(candidate.status)}
      </div>

      <div className="space-y-3 mt-6">
        <div className="flex justify-between p-3 bg-teal-950/30 rounded-lg">
          <span className="text-teal-300">Trust Score</span>
          <span className="text-white font-bold">{candidate?.trust_score || 0}%</span>
        </div>
        <div className="flex justify-between p-3 bg-teal-950/30 rounded-lg">
          <span className="text-teal-300">Experience</span>
          <span className="text-white font-bold">{candidate?.experience || 0} years</span>
        </div>
        <div className="flex justify-between p-3 bg-teal-950/30 rounded-lg">
          <span className="text-teal-300">Skills Match</span>
          <span className="text-white font-bold">{candidate?.skills_match || 0}%</span>
        </div>
      </div>

      {candidate?.skills && candidate.skills.length > 0 && (
        <div className="mt-6">
          <p className="text-teal-300 text-sm mb-3">Top Skills</p>
          <div className="flex flex-wrap gap-2">
            {candidate.skills.map((skill, idx) => (
              <span key={idx} className="px-3 py-1 bg-teal-800/40 border border-teal-600/30 text-teal-200 rounded-full text-xs">{skill}</span>
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

  const compareNow = async () => {
    if (!candidate1Id.trim() || !candidate2Id.trim()) {
      alert('Please enter both candidate IDs');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate1_id: candidate1Id, candidate2_id: candidate2Id })
      });

      if (response.ok) {
        const data = await response.json();
        setComparison(data);
      } else {
        alert('Failed to compare candidates');
      }
    } catch (error) {
      console.error('Failed to compare:', error);
      alert('Failed to compare candidates');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white p-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
            <GitCompare className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-violet-900">Compare Candidates</h1>
            <p className="text-slate-500">Side-by-side candidate analysis</p>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/95 backdrop-blur-sm border border-violet-100 shadow-xl rounded-2xl p-6 mb-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-violet-600/10 pointer-events-none" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 relative z-10">
          <input type="text" placeholder="Candidate 1 ID (e.g., cand_123)" value={candidate1Id} onChange={(e) => setCandidate1Id(e.target.value)} className="px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all" />
          <input type="text" placeholder="Candidate 2 ID (e.g., cand_456)" value={candidate2Id} onChange={(e) => setCandidate2Id(e.target.value)} className="px-6 py-4 bg-teal-950/50 border border-teal-700/30 rounded-xl text-white placeholder-teal-400 focus:outline-none focus:border-teal-500 transition-all" />
        </div>
        <button onClick={compareNow} disabled={loading} className="w-full px-8 py-4 bg-gradient-to-r from-teal-600 to-cyan-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed">{loading ? 'Comparing...' : 'Compare Now'}</button>
      </motion.div>

      {comparison && (
        <div className="space-y-6">
          {comparison.winner && (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 backdrop-blur-xl border border-yellow-600/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-full flex items-center justify-center">
                  <Award className="text-white" size={32} />
                </div>
                <div>
                  <p className="text-yellow-300 text-sm mb-1">Recommended Candidate</p>
                  <h2 className="text-3xl font-bold text-white">{comparison.winner}</h2>
                  <p className="text-yellow-200 text-sm mt-1">{comparison.reason || 'Higher overall performance'}</p>
                </div>
              </div>
            </motion.div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CandidateCard candidate={comparison.candidate1} color="from-cyan-900/70 to-teal-900/70" side="left" />
            <CandidateCard candidate={comparison.candidate2} color="from-emerald-900/70 to-teal-900/70" side="right" />
          </div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-teal-900/50 backdrop-blur-xl border border-teal-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <BarChart3 className="text-teal-400" size={24} />
              <h2 className="text-2xl font-bold text-white">Performance Comparison</h2>
            </div>

            <div className="space-y-6">
              <MetricBar label="Trust Score" value1={comparison.candidate1?.trust_score || 0} value2={comparison.candidate2?.trust_score || 0} name1={comparison.candidate1?.name || 'C1'} name2={comparison.candidate2?.name || 'C2'} color1="bg-gradient-to-r from-cyan-500 to-blue-500" color2="bg-gradient-to-r from-emerald-500 to-teal-500" />
              <MetricBar label="Skills Match" value1={comparison.candidate1?.skills_match || 0} value2={comparison.candidate2?.skills_match || 0} name1={comparison.candidate1?.name || 'C1'} name2={comparison.candidate2?.name || 'C2'} color1="bg-gradient-to-r from-cyan-600 to-blue-600" color2="bg-gradient-to-r from-emerald-600 to-teal-600" />
              <MetricBar label="Experience (Years)" value1={comparison.candidate1?.experience || 0} value2={comparison.candidate2?.experience || 0} name1={comparison.candidate1?.name || 'C1'} name2={comparison.candidate2?.name || 'C2'} color1="bg-gradient-to-r from-cyan-700 to-blue-700" color2="bg-gradient-to-r from-emerald-700 to-teal-700" />
            </div>
          </motion.div>

          {comparison.skills_comparison && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="bg-teal-900/50 backdrop-blur-xl border border-teal-700/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <TrendingUp className="text-teal-400" size={24} />
                <h2 className="text-2xl font-bold text-white">Skills Analysis</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {comparison.skills_comparison.common && comparison.skills_comparison.common.length > 0 && (
                  <div>
                    <p className="text-green-400 font-semibold mb-3">Common Skills</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.common.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-green-900/30 border border-green-700/30 rounded-lg text-green-200 text-sm">{skill}</div>
                      ))}
                    </div>
                  </div>
                )}

                {comparison.skills_comparison.unique_to_1 && comparison.skills_comparison.unique_to_1.length > 0 && (
                  <div>
                    <p className="text-cyan-400 font-semibold mb-3">Unique to {comparison.candidate1?.name || 'C1'}</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.unique_to_1.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-cyan-900/30 border border-cyan-700/30 rounded-lg text-cyan-200 text-sm">{skill}</div>
                      ))}
                    </div>
                  </div>
                )}

                {comparison.skills_comparison.unique_to_2 && comparison.skills_comparison.unique_to_2.length > 0 && (
                  <div>
                    <p className="text-emerald-400 font-semibold mb-3">Unique to {comparison.candidate2?.name || 'C2'}</p>
                    <div className="space-y-2">
                      {comparison.skills_comparison.unique_to_2.map((skill, idx) => (
                        <div key={idx} className="p-2 bg-emerald-900/30 border border-emerald-700/30 rounded-lg text-emerald-200 text-sm">{skill}</div>
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
          <GitCompare className="w-20 h-20 text-teal-700 mx-auto mb-4 opacity-50" />
          <p className="text-teal-300 text-lg">Enter two candidate IDs to start comparison</p>
        </motion.div>
      )}
    </div>
  );
};

export default CompareCandidates;
