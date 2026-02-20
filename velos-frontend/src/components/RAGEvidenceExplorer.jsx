import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, FileText, ChevronRight, ExternalLink,
  CheckCircle, AlertCircle, Database, Layers, BookOpen, Target, Sparkles
} from 'lucide-react';
import { API_BASE } from '../config.js';

// Safe regex escaping — prevents crash on (, *, +, [ in user input
const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// Evidence chunk card with highlighting
const EvidenceChunk = ({ chunk, index, query, highlighted }) => {
  const [expanded, setExpanded] = useState(false);

  // Highlight matching text
  const highlightText = (text, searchTerms) => {
    if (!searchTerms || searchTerms.length === 0) return text;

    let highlightedText = text;
    searchTerms.forEach(term => {
      const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
      highlightedText = highlightedText.replace(
        regex,
        '<mark class="bg-yellow-300/80 text-gray-900 px-1 rounded">$1</mark>'
      );
    });

    return highlightedText;
  };

  const getRelevanceColor = (score) => {
    if (score >= 0.8) return 'from-green-100/60 to-emerald-100/60 border-green-200/60';
    if (score >= 0.6) return 'from-blue-100/60 to-indigo-100/60 border-blue-200/60';
    if (score >= 0.4) return 'from-yellow-100/60 to-orange-100/60 border-yellow-200/60';
    return 'from-red-50 to-pink-50 border-red-200';
  };

  const relevanceScore = chunk.score || 0.75;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`bg-gradient-to-br ${getRelevanceColor(relevanceScore)} backdrop-blur-xl border rounded-xl p-4 shadow-lg hover:shadow-2xl transition-all`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center">
            <FileText className="text-gray-900" size={16} />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="text-gray-900 font-semibold text-sm">Evidence Chunk #{index + 1}</h4>
              {highlighted && (
                <span className="px-2 py-0.5 bg-yellow-100 border border-yellow-400 rounded-full text-yellow-700 text-xs font-semibold">
                  Match
                </span>
              )}
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1">
                <Target className="text-gray-600" size={12} />
                <span className="text-gray-600">Relevance: {(relevanceScore * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-center gap-1">
                <Layers className="text-gray-600" size={12} />
                <span className="text-gray-600">Chunk {chunk.chunk_id || index + 1}</span>
              </div>
            </div>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <motion.div
            animate={{ rotate: expanded ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight size={20} />
          </motion.div>
        </button>
      </div>

      {/* Preview */}
      <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg mb-3">
        <p
          className="text-gray-900 text-sm leading-relaxed line-clamp-3"
          dangerouslySetInnerHTML={{
            __html: highlightText(chunk.text || chunk.content, query?.split(' ') || [])
          }}
        />
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-3 text-xs">
        <div className="flex items-center gap-1">
          <BookOpen className="text-gray-600" size={12} />
          <span className="text-gray-600">{chunk.text?.length || 0} chars</span>
        </div>
        {chunk.metadata?.source && (
          <div className="flex items-center gap-1">
            <Database className="text-gray-600" size={12} />
            <span className="text-gray-600">{chunk.metadata.source}</span>
          </div>
        )}
      </div>

      {/* Expanded view */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 pt-4 border-t border-white/10"
          >
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <p
                className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap"
                dangerouslySetInnerHTML={{
                  __html: highlightText(chunk.text || chunk.content, query?.split(' ') || [])
                }}
              />
            </div>

            {chunk.metadata && (
              <div className="mt-3 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
                <p className="text-indigo-700 text-xs font-semibold mb-2">Metadata</p>
                <div className="space-y-1">
                  {Object.entries(chunk.metadata).map(([key, value]) => (
                    <div key={key} className="flex items-center gap-2 text-xs">
                      <span className="text-indigo-600">{key}:</span>
                      <span className="text-gray-800 font-mono">{JSON.stringify(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// Search stats banner
const SearchStats = ({ stats }) => {
  return (
    <div className="grid grid-cols-4 gap-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-white/40 to-white/30 border border-blue-500/30 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Database className="text-blue-600" size={20} />
          <p className="text-gray-600 text-sm">Total Chunks</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.total_chunks || 0}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-300 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle className="text-green-600" size={20} />
          <p className="text-green-700 text-sm">Matches Found</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.matches_found || 0}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-white/40 to-white/30 border border-purple-500/30 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Target className="text-purple-600" size={20} />
          <p className="text-purple-700 text-sm">Avg Relevance</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.avg_relevance || 0}%</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-300 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="text-amber-600" size={20} />
          <p className="text-amber-700 text-sm">Highlighted</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.highlighted || 0}</p>
      </motion.div>
    </div>
  );
};

// Main component
const RAGEvidenceExplorer = () => {
  const [candidateId, setCandidateId] = useState('');
  const [query, setQuery] = useState('');
  const [evidence, setEvidence] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchEvidence = async () => {
    if (!candidateId.trim()) {
      setError('Please enter a candidate ID');
      return;
    }

    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setEvidence(null);

    try {
      // First get the candidate's verification result
      const response = await fetch(`${API_BASE}/api/candidates/${candidateId}/trust-packet`);

      if (response.ok) {
        const data = await response.json();

        // Extract evidence from pipeline stages (nested under trust_packet)
        const agent2Data = data.trust_packet?.pipeline_stages?.agent_2;
        const evidenceChunks = agent2Data?.evidence || [];

        // Calculate stats
        const stats = {
          total_chunks: evidenceChunks.length,
          matches_found: evidenceChunks.filter(chunk =>
            chunk.text?.toLowerCase().includes(query.toLowerCase())
          ).length,
          avg_relevance: evidenceChunks.length > 0
            ? Math.round(evidenceChunks.reduce((sum, chunk) => sum + (chunk.score || 0.75), 0) / evidenceChunks.length * 100)
            : 0,
          highlighted: evidenceChunks.filter(chunk =>
            chunk.text?.toLowerCase().includes(query.toLowerCase())
          ).length
        };

        setEvidence({
          chunks: evidenceChunks,
          stats: stats,
          candidate_id: candidateId,
          query: query
        });
      } else {
        setError(`Failed to fetch evidence for candidate ${candidateId}`);
      }
    } catch (err) {
      console.error('Failed to search evidence:', err);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
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
          <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-2xl">
            <Search className="text-gray-900" size={32} />
          </div>
          <div>
            <h1 className="text-5xl font-bold text-gray-900">RAG Evidence Explorer</h1>
            <p className="text-gray-600 text-lg">Search and visualize resume evidence chunks</p>
          </div>
        </div>
      </motion.div>

      {/* Search Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/40 backdrop-blur-xl border border-white/60 rounded-2xl p-6 mb-8"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-gray-600 text-sm font-semibold mb-2">
              Candidate ID
            </label>
            <input
              type="text"
              placeholder="Enter Candidate ID (e.g., CAND-A1B2C3D4)"
              value={candidateId}
              onChange={(e) => setCandidateId(e.target.value)}
              className="w-full px-6 py-3 bg-white/80 border border-indigo-200/60 rounded-xl text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
          </div>

          <div>
            <label className="block text-gray-600 text-sm font-semibold mb-2">
              Search Query
            </label>
            <input
              type="text"
              placeholder="Enter search terms (e.g., Python, machine learning, AWS)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchEvidence()}
              className="w-full px-6 py-3 bg-white/80 border border-indigo-200/60 rounded-xl text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            />
          </div>

          <button
            onClick={searchEvidence}
            disabled={loading}
            className="w-full px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-gray-900 font-semibold rounded-xl hover:shadow-2xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Search size={20} />
            {loading ? 'Searching...' : 'Search Evidence'}
          </button>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-50 border border-red-300 rounded-lg flex items-center gap-3"
          >
            <AlertCircle className="text-red-500" size={20} />
            <p className="text-red-700">{error}</p>
          </motion.div>
        )}
      </motion.div>

      {/* Results */}
      {evidence && (
        <div className="space-y-6">
          {/* Stats */}
          <SearchStats stats={evidence.stats} />

          {/* Evidence Chunks */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <FileText className="text-indigo-600" />
                Evidence Chunks ({evidence.chunks.length})
              </h2>
              {evidence.stats.matches_found > 0 && (
                <span className="px-4 py-2 bg-green-50 border border-green-300 rounded-lg text-green-700 font-semibold">
                  {evidence.stats.matches_found} matches highlighted
                </span>
              )}
            </div>

            {evidence.chunks.length > 0 ? (
              <div className="space-y-4">
                {evidence.chunks.map((chunk, index) => (
                  <EvidenceChunk
                    key={index}
                    chunk={chunk}
                    index={index}
                    query={evidence.query}
                    highlighted={chunk.text?.toLowerCase().includes(evidence.query.toLowerCase())}
                  />
                ))}
              </div>
            ) : (
              <div className="p-12 bg-white/40 backdrop-blur-xl border border-white/60 rounded-xl text-center">
                <Database className="mx-auto text-gray-400 mb-4" size={48} />
                <p className="text-gray-600 text-lg">No evidence chunks found</p>
                <p className="text-gray-500 text-sm mt-2">Try a different candidate ID or search query</p>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default RAGEvidenceExplorer;
