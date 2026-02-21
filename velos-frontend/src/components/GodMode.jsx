import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, AlertTriangle, Zap, Shield, Clock, Server, Database, TrendingUp, Users, CheckCircle, XCircle, AlertCircle, WifiOff } from 'lucide-react';
import { injectMockData } from './mockGodModeData';
import { API_BASE } from '../config.js';

const MetricCard = ({ icon: Icon, label, value, status, gradient }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    className="bg-white/95 backdrop-blur-sm border border-violet-100 shadow-xl rounded-2xl p-6 relative overflow-hidden"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-violet-600/10 pointer-events-none" />
    <div className="flex items-center justify-between mb-4">
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg animate-pulse`}>
        <Icon className="text-white" size={24} />
      </div>
      {status === 'good' && <CheckCircle className="text-green-400" size={20} />}
      {status === 'warning' && <AlertCircle className="text-yellow-400" size={20} />}
      {status === 'error' && <XCircle className="text-red-400" size={20} />}
    </div>
    <p className="text-sm text-slate-500 relative z-10 mb-1">{label}</p>
    <h3 className="text-3xl font-bold text-slate-900 relative z-10">{value}</h3>
  </motion.div>
);

const AgentCard = ({ agent, index }) => {
  const statusColors = {
    'active': 'bg-green-500',
    'idle': 'bg-yellow-500',
    'error': 'bg-red-500'
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white/95 backdrop-blur-sm border border-violet-100 shadow-lg rounded-xl p-5 hover:border-violet-300 transition-all relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-violet-600/10 pointer-events-none" />
      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${statusColors[agent.status]} animate-pulse`} />
          <h4 className="text-lg font-semibold text-violet-900">{agent.name}</h4>
        </div>
        <span className="text-xs text-violet-700 bg-violet-100 px-3 py-1 rounded-full">
          {agent.role}
        </span>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4 relative z-10">
        <div>
          <p className="text-xs text-slate-500">Processed</p>
          <p className="text-xl font-bold text-slate-900">{agent.processed}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Success Rate</p>
          <p className="text-xl font-bold text-green-600">{agent.successRate}%</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Avg Time</p>
          <p className="text-xl font-bold text-cyan-600">{agent.avgTime}s</p>
        </div>
      </div>

      <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden relative z-10">
        <div 
          className="h-full bg-gradient-to-r from-violet-500 to-purple-400 rounded-full transition-all duration-500 animate-shimmer"
          style={{ width: `${agent.successRate}%` }}
        />
      </div>
    </motion.div>
  );
};

const GodMode = () => {
  const [insights, setInsights] = useState(null);
  const [agents, setAgents] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);

  useEffect(() => {
    // Toggle between real API and mock data for testing
    const USE_MOCK_DATA = false; // Set to true to use mock data for testing

    if (USE_MOCK_DATA) {
      console.log('Using mock data for God Mode');
      injectMockData(setInsights, setAgents, setHealth, setLoading);
      // No interval when using mock data — return empty cleanup
      return () => {};
    }

    fetchGodModeData();
    const interval = setInterval(fetchGodModeData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchGodModeData = async () => {
    try {
      const [insightsRes, agentsRes, healthRes] = await Promise.all([
       fetch(`${API_BASE}/api/insights`).catch(() => null),
       fetch(`${API_BASE}/api/agents`).catch(() => null),
       fetch(`${API_BASE}/api/health`).catch(() => null)
      ]);

      if (insightsRes && insightsRes.ok) {
        const data = await insightsRes.json();
        setInsights(data);
      } else {
        setInsights({ bias_alerts: 0, fraud_cases: 0, avg_processing_time: 0, total_candidates: 0 });
      }

      if (agentsRes && agentsRes.ok) {
        const data = await agentsRes.json();
        setAgents(data.agents || []);
      } else {
        setAgents([
          { name: 'Gatekeeper', role: 'Entry Filter', status: 'active', processed: 0, successRate: 0, avgTime: 0 },
          { name: 'Validator', role: 'Verification', status: 'active', processed: 0, successRate: 0, avgTime: 0 },
          { name: 'Inquisitor', role: 'Deep Analysis', status: 'active', processed: 0, successRate: 0, avgTime: 0 }
        ]);
      }

      if (healthRes && healthRes.ok) {
        const data = await healthRes.json();
        setHealth(data);
      } else {
        setHealth({ status: 'unknown', uptime: 0, memory_usage: 0 });
      }

      // If all three endpoints failed (null), surface an error
      if (!insightsRes && !agentsRes && !healthRes) {
        setFetchError('Unable to reach the server. Showing stale / default data.');
      } else {
        setFetchError(null);
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch God Mode data:', error);
      setFetchError('Unable to reach the server. Showing stale / default data.');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center">
        <div className="text-center">
          <Zap className="w-16 h-16 text-violet-400 animate-pulse mx-auto mb-4" />
          <p className="text-violet-600 text-lg">Initializing God Mode...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-0">
      {/* Fetch Error Banner */}
      {fetchError && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-5 py-3 mb-6 bg-red-50 border border-red-200 rounded-2xl text-red-700"
        >
          <WifiOff size={18} className="flex-shrink-0" />
          <span className="text-sm font-medium flex-1">{fetchError}</span>
          <button onClick={() => setFetchError(null)} className="text-red-400 hover:text-red-600 transition-colors text-lg leading-none">&times;</button>
        </motion.div>
      )}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <Zap className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-violet-900">God Mode</h1>
            <p className="text-slate-500">System-wide insights & agent performance</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard icon={AlertTriangle} label="Bias Alerts" value={insights?.bias_alerts || 0} status={insights?.bias_alerts > 5 ? 'warning' : 'good'} gradient="from-red-500 to-orange-500" />
        <MetricCard icon={Shield} label="Fraud Cases" value={insights?.fraud_cases || 0} status={insights?.fraud_cases > 0 ? 'error' : 'good'} gradient="from-yellow-500 to-orange-500" />
        <MetricCard icon={Clock} label="Avg Processing" value={`${insights?.avg_processing_time?.toFixed(1) || 0}s`} status={insights?.avg_processing_time != null && insights.avg_processing_time < 3 ? 'good' : 'warning'} gradient="from-cyan-500 to-blue-500" />
        <MetricCard icon={Users} label="Total Candidates" value={insights?.total_candidates || 0} status="good" gradient="from-green-500 to-teal-500" />
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/95 backdrop-blur-sm border border-violet-100 shadow-xl rounded-2xl p-6 mb-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-violet-600/10 pointer-events-none" />
        <div className="flex items-center gap-3 mb-6 relative z-10">
          <Server className="text-violet-600" size={24} />
          <h2 className="text-2xl font-bold text-violet-900">System Health</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="text-green-500" size={20} />
              <p className="text-slate-500 text-sm">Status</p>
            </div>
            <p className="text-2xl font-bold text-slate-900 capitalize">{health?.status || 'Unknown'}</p>
          </div>
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="text-cyan-500" size={20} />
              <p className="text-slate-500 text-sm">Uptime</p>
            </div>
            <p className="text-2xl font-bold text-slate-900">{health?.uptime ? `${Math.floor(health.uptime / 3600)}h` : '0h'}</p>
          </div>
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="flex items-center gap-3 mb-2">
              <Database className="text-purple-500" size={20} />
              <p className="text-slate-500 text-sm">Memory</p>
            </div>
            <p className="text-2xl font-bold text-slate-900">{health?.memory_usage ? `${health.memory_usage.toFixed(1)} MB` : '0 MB'}</p>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="text-violet-600" size={24} />
          <h2 className="text-2xl font-bold text-violet-900">Agent Performance Matrix</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {agents.map((agent, index) => (<AgentCard key={agent.name} agent={agent} index={index} />))}
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="mt-8 text-center">
        <div className="inline-flex items-center gap-2 bg-white/95 backdrop-blur-sm border border-violet-200 shadow-md rounded-full px-6 py-3">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <p className="text-slate-600 text-sm">Live monitoring • Real-time data</p>
        </div>
      </motion.div>
    </div>
  );
};

export default GodMode;
