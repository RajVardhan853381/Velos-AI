import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, TrendingUp, Filter, Users, Star, Target, WifiOff } from 'lucide-react';
import { API_BASE } from '../config.js';

const LeaderboardEntry = ({ candidate, rank, index }) => {
  const getRankIcon = (rank) => {
    if (rank === 1) return <Trophy className="text-yellow-500" size={24} />;
    if (rank === 2) return <Medal className="text-slate-400" size={24} />;
    if (rank === 3) return <Medal className="text-amber-600" size={24} />;
    return <span className="text-slate-600 font-bold text-lg">#{rank}</span>;
  };

  const getRankColor = (rank) => {
    if (rank === 1) return 'from-yellow-400 to-amber-400';
    if (rank === 2) return 'from-slate-300 to-slate-400';
    if (rank === 3) return 'from-amber-500 to-orange-500';
    return 'from-emerald-400 to-green-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.02, x: 8 }}
      className={`bg-white/60 backdrop-blur-xl border rounded-2xl p-6 shadow-sm transition-all ${
        rank <= 3 ? 'border-emerald-200 bg-emerald-50/30' : 'border-emerald-100/50'
      }`}
    >
      <div className="flex items-center gap-6">
        {/* Rank */}
        <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${getRankColor(rank)} flex items-center justify-center shadow-md flex-shrink-0`}>
          {getRankIcon(rank)}
        </div>

        {/* Candidate Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-slate-800 truncate mb-1">
            {candidate.id || `Candidate ${candidate.rank}`}
          </h3>
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="flex items-center gap-1">
              <Star size={14} className="text-emerald-500" />
              Trust: {candidate.trust_score}%
            </span>
            <span className="flex items-center gap-1">
              <Target size={14} className="text-blue-500" />
              Match: {candidate.skill_match}%
            </span>
          </div>
        </div>

        {/* Score */}
        <div className="text-right flex-shrink-0">
          <div className="text-3xl font-bold text-emerald-600">
            {candidate.overall_score || candidate.trust_score}
          </div>
          <div className="text-xs text-slate-600 uppercase tracking-wide">Score</div>
        </div>
      </div>

      {/* Skills Bar */}
      {candidate.skills && candidate.skills.length > 0 && (
        <div className="mt-4 pt-4 border-t border-emerald-100">
          <div className="flex flex-wrap gap-2">
            {candidate.skills.slice(0, 5).map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-emerald-100/80 text-emerald-700 text-xs font-medium rounded-full backdrop-blur-sm"
              >
                {skill}
              </span>
            ))}
            {candidate.skills.length > 5 && (
              <span className="px-3 py-1 bg-slate-100/80 text-slate-600 text-xs font-medium rounded-full">
                +{candidate.skills.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};

const Leaderboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [unavailable, setUnavailable] = useState(false);
  const [fetchError, setFetchError] = useState(null);
  const [minScore, setMinScore] = useState(0);
  const [statusFilter, setStatusFilter] = useState('passed');

  useEffect(() => {
    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/leaderboard`);
      if (response.ok) {
        const data = await response.json();
        setCandidates(data.data?.leaderboard || []);
        setUnavailable(false);
        setFetchError(null);
      } else if (response.status === 503) {
        setCandidates([]);
        setUnavailable(true);
        setFetchError(null);
        console.info('Leaderboard requires batch analytics — process candidates via Batch Upload first.');
      } else {
        setCandidates([]);
        setUnavailable(false);
        setFetchError(`Failed to load leaderboard (HTTP ${response.status})`);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setCandidates([]);
      setFetchError('Unable to reach the server. Leaderboard unavailable.');
      setLoading(false);
    }
  };

  const filteredCandidates = candidates
    .filter(c => {
      const score = c.overall_score || c.trust_score || 0;
      return score >= minScore && (statusFilter === 'all' || c.status === statusFilter);
    })
    .sort((a, b) => {
      const scoreA = a.overall_score || a.trust_score || 0;
      const scoreB = b.overall_score || b.trust_score || 0;
      return scoreB - scoreA;
    });

  const stats = {
    total: filteredCandidates.length,
    avgScore: filteredCandidates.length > 0
      ? Math.round(filteredCandidates.reduce((sum, c) => sum + (c.overall_score || c.trust_score || 0), 0) / filteredCandidates.length)
      : 0,
    topScore: filteredCandidates.length > 0 ? (filteredCandidates[0].overall_score || filteredCandidates[0].trust_score) : 0,
    aboveThreshold: filteredCandidates.filter(c => (c.overall_score || c.trust_score || 0) >= 80).length,
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
        className="bg-gradient-to-r from-emerald-50/70 to-green-50/70 backdrop-blur-xl border border-emerald-100/50 rounded-3xl p-8 shadow-lg"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-green-400 flex items-center justify-center shadow-lg animate-float">
            <Trophy className="text-white" size={32} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-800">Leaderboard</h1>
            <p className="text-slate-600 mt-1">Top-ranked verified candidates by trust score</p>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Candidates', value: stats.total, color: 'from-blue-400 to-cyan-400', icon: Users },
          { label: 'Average Score', value: `${stats.avgScore}%`, color: 'from-purple-400 to-pink-400', icon: TrendingUp },
          { label: 'Top Score', value: `${stats.topScore}%`, color: 'from-yellow-400 to-amber-400', icon: Trophy },
          { label: 'Above 80%', value: stats.aboveThreshold, color: 'from-emerald-400 to-green-400', icon: Award },
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.05 }}
            className="bg-white/60 backdrop-blur-xl border border-emerald-100/50 rounded-2xl p-6 shadow-sm"
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
        className="bg-white/60 backdrop-blur-xl border border-emerald-100/50 rounded-2xl p-6 shadow-sm"
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter className="text-emerald-600" size={20} />
          <h3 className="font-bold text-slate-800">Filters</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Min Score Slider */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Minimum Score: <span className="text-emerald-600 font-bold">{minScore}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="w-full h-2 bg-emerald-200 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>0%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
            <div className="flex gap-2">
              {['all', 'passed', 'failed'].map((status) => (
                <motion.button
                  key={status}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setStatusFilter(status)}
                  className={`flex-1 px-4 py-2 rounded-xl font-medium transition-all backdrop-blur-sm ${
                    statusFilter === status
                      ? 'bg-emerald-500 text-white shadow-md'
                      : 'bg-white/80 text-slate-600 hover:bg-white border border-emerald-200'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </motion.button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Leaderboard List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="space-y-4"
      >
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-emerald-200 border-t-emerald-500 rounded-full animate-spin"></div>
          </div>
        ) : filteredCandidates.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
              <Users className="text-slate-400" size={40} />
            </div>
            {unavailable ? (
              <>
                <p className="text-slate-600 font-medium">Batch Analytics Not Available</p>
                <p className="text-sm text-slate-500 mt-1">Process candidates via <strong>Batch Upload</strong> to populate the leaderboard.</p>
              </>
            ) : (
              <>
                <p className="text-slate-600 font-medium">No candidates found</p>
                <p className="text-sm text-slate-500 mt-1">Try adjusting your filters</p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredCandidates.map((candidate, index) => (
              <LeaderboardEntry
                key={candidate.id || index}
                candidate={{ ...candidate, rank: index + 1 }}
                rank={index + 1}
                index={index}
              />
            ))}
          </div>
        )}
      </motion.div>

      {/* Top 3 Podium (if enough candidates) */}
      {filteredCandidates.length >= 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-emerald-50/70 to-green-50/70 backdrop-blur-xl border border-emerald-100/50 rounded-3xl p-8 shadow-lg"
        >
          <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Top 3 Podium</h2>
          <div className="flex items-end justify-center gap-4">
            {/* 2nd Place */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="flex-1 max-w-xs"
            >
              <div className="bg-white/80 backdrop-blur-sm border-2 border-slate-300 rounded-2xl p-6 text-center h-48 flex flex-col justify-between">
                <div>
                  <Medal className="text-slate-400 mx-auto mb-2" size={40} />
                  <p className="font-bold text-slate-800 truncate">{filteredCandidates[1].id}</p>
                  <p className="text-3xl font-bold text-slate-600 mt-2">{filteredCandidates[1].overall_score || filteredCandidates[1].trust_score}%</p>
                </div>
                <div className="text-xs text-slate-600 uppercase tracking-wide font-bold">2nd Place</div>
              </div>
            </motion.div>

            {/* 1st Place (Tallest) */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="flex-1 max-w-xs"
            >
              <div className="bg-gradient-to-br from-yellow-100 to-amber-100 backdrop-blur-sm border-2 border-yellow-400 rounded-2xl p-6 text-center h-56 flex flex-col justify-between shadow-lg">
                <div>
                  <Trophy className="text-yellow-500 mx-auto mb-2 animate-float" size={48} />
                  <p className="font-bold text-slate-800 truncate">{filteredCandidates[0].id}</p>
                  <p className="text-4xl font-bold text-yellow-600 mt-2">{filteredCandidates[0].overall_score || filteredCandidates[0].trust_score}%</p>
                </div>
                <div className="text-xs text-yellow-700 uppercase tracking-wide font-bold">Champion</div>
              </div>
            </motion.div>

            {/* 3rd Place */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.55 }}
              className="flex-1 max-w-xs"
            >
              <div className="bg-white/80 backdrop-blur-sm border-2 border-amber-500 rounded-2xl p-6 text-center h-40 flex flex-col justify-between">
                <div>
                  <Medal className="text-amber-600 mx-auto mb-2" size={36} />
                  <p className="font-bold text-slate-800 truncate">{filteredCandidates[2].id}</p>
                  <p className="text-2xl font-bold text-amber-600 mt-2">{filteredCandidates[2].overall_score || filteredCandidates[2].trust_score}%</p>
                </div>
                <div className="text-xs text-amber-700 uppercase tracking-wide font-bold">3rd Place</div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Leaderboard;
