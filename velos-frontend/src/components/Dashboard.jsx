import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion } from 'framer-motion';
import { Users, Shield, AlertTriangle, TrendingUp, Activity, Award, CheckCircle, XCircle } from 'lucide-react';
import { API_BASE } from '../config.js';

const StatCard = ({ title, value, subtext, icon: Icon, gradient, delay, trend }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ scale: 1.02, y: -4 }}
    transition={{ delay, duration: 0.3 }}
    className="relative overflow-hidden bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft hover:shadow-soft-lg transition-all"
  >
    <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
      <div className={`w-full h-full bg-gradient-to-br ${gradient} rounded-full blur-2xl`}></div>
    </div>
    <div className="relative z-10">
      <div className={`inline-flex w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} items-center justify-center mb-4 shadow-soft`}>
        <Icon className="text-white" size={22} />
      </div>
      <p className="text-sm text-gray-500 mb-1 font-medium">{title}</p>
      <h3 className="text-3xl font-bold text-gray-800 mb-2">{value}</h3>
      {trend && (
        <div className="flex items-center gap-2">
          <span className={`text-xs font-semibold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
          <span className="text-xs text-gray-500">{subtext}</span>
        </div>
      )}
      {!trend && <p className="text-xs text-gray-500">{subtext}</p>}
    </div>
  </motion.div>
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, chartRes, auditRes] = await Promise.all([
        fetch(`${API_BASE}/api/stats`).catch(() => null),
        fetch(`${API_BASE}/api/chart-data/timeline`).catch(() => null),
        fetch(`${API_BASE}/api/audit`).catch(() => null)
      ]);

      if (statsRes && statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      } else {
        setStats({
          total_candidates: 0,
          approved_total: 0,
          fraud_detected: 0,
        });
      }

      if (chartRes && chartRes.ok) {
        const chartJson = await chartRes.json();
        // API returns Chart.js format {labels, datasets} — transform to recharts format [{name, score, candidates}]
        const labels = chartJson.labels || [];
        const processed = (chartJson.datasets || []).find(d => d.label === 'Processed');
        const passed = (chartJson.datasets || []).find(d => d.label === 'Passed');
        if (labels.length > 0) {
          setChartData(labels.map((name, i) => ({
            name,
            candidates: processed ? (processed.data[i] || 0) : 0,
            score: passed && processed && processed.data[i] > 0
              ? Math.round((passed.data[i] / processed.data[i]) * 100)
              : 0,
          })));
        } else {
          setChartData([
            { name: 'Mon', score: 65, candidates: 45 },
            { name: 'Tue', score: 78, candidates: 52 },
            { name: 'Wed', score: 85, candidates: 61 },
            { name: 'Thu', score: 82, candidates: 58 },
            { name: 'Fri', score: 90, candidates: 68 },
            { name: 'Sat', score: 95, candidates: 72 },
            { name: 'Sun', score: 88, candidates: 65 },
          ]);
        }
      } else {
        setChartData([
          { name: 'Mon', score: 65, candidates: 45 },
          { name: 'Tue', score: 78, candidates: 52 },
          { name: 'Wed', score: 85, candidates: 61 },
          { name: 'Thu', score: 82, candidates: 58 },
          { name: 'Fri', score: 90, candidates: 68 },
          { name: 'Sat', score: 95, candidates: 72 },
          { name: 'Sun', score: 88, candidates: 65 },
        ]);
      }

      if (auditRes && auditRes.ok) {
        const auditJson = await auditRes.json();
        // Map audit logs to the activity format the component renders
        const logs = auditJson.audit_logs || [];
        setRecentActivity(logs.slice(0, 5).map((log, i) => ({
          id: i,
          name: log.user,
          action: log.action,
          score: log.status === 'passed' ? 88 : log.status === 'failed' ? 42 : 65,
          status: log.status === 'passed' ? 'passed' : log.status === 'failed' ? 'failed' : 'passed',
          time: log.time
        })));
      }

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setStats({
          total_candidates: 0,
          approved_total: 0,
          fraud_detected: 0,
        });
      setLoading(false);
    }
  };

  const displayStats = stats || {
    total_candidates: 0,
    approved_total: 0,
    fraud_detected: 0,
  };

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Verifications"
          value={(displayStats.total_candidates || 0).toLocaleString()}
          subtext="This month"
          icon={Users}
          gradient="from-blue-500 to-indigo-600"
          delay={0}
          trend={12.5}
        />
        <StatCard
          title="Approved Candidates"
          value={(displayStats.approved_total || 0).toLocaleString()}
          subtext="Across all candidates"
          icon={Shield}
          gradient="from-emerald-500 to-teal-600"
          delay={0.1}
          trend={5.2}
        />
        <StatCard
          title="Fraud Detected"
          value={displayStats.fraud_detected || 0}
          subtext="Requires review"
          icon={AlertTriangle}
          gradient="from-amber-500 to-orange-600"
          delay={0.2}
          trend={-8.3}
        />
        <StatCard
          title="Success Rate"
          value={`${displayStats.total_candidates > 0 ? Math.round((displayStats.approved_total / displayStats.total_candidates) * 100) : 0}%`}
          subtext="Last 30 days"
          icon={Award}
          gradient="from-purple-500 to-pink-600"
          delay={0.3}
          trend={3.1}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trust Score Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-gray-800">Trust Score Trend</h3>
              <p className="text-sm text-gray-500">Weekly performance overview</p>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp size={20} className="text-green-500" />
              <span className="text-sm font-semibold text-green-600">+12.5%</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="name" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #E5E7EB',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#3B82F6"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorScore)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Candidate Volume */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-gray-800">Candidate Volume</h3>
              <p className="text-sm text-gray-500">Daily verification count</p>
            </div>
            <Activity size={20} className="text-indigo-500" />
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="name" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #E5E7EB',
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar dataKey="candidates" fill="#6366F1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-gray-800">Recent Activity</h3>
            <p className="text-sm text-gray-500">Latest verification results</p>
          </div>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('navigate', { detail: 'candidates' }))}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            View All
          </button>
        </div>
        <div className="space-y-3">
          {recentActivity.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Activity size={32} className="mx-auto mb-2 opacity-40" />
              <p className="text-sm">No recent activity yet</p>
              <p className="text-xs">Verify a candidate to see activity here</p>
            </div>
          ) : recentActivity.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + index * 0.1 }}
              className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50/50 to-transparent rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-soft transition-all"
            >
              <div className="flex items-center gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  activity.status === 'passed' ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {activity.status === 'passed' ? (
                    <CheckCircle size={20} className="text-green-600" />
                  ) : (
                    <XCircle size={20} className="text-red-600" />
                  )}
                </div>
                <div>
                  <p className="font-semibold text-gray-800">{activity.name}</p>
                  <p className="text-sm text-gray-500">{activity.action}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className={`text-lg font-bold ${
                    activity.score >= 80 ? 'text-green-600' : 
                    activity.score >= 60 ? 'text-amber-600' : 'text-red-600'
                  }`}>
                    {activity.score}%
                  </p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
