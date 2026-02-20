import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Clock, User, Activity, CheckCircle, XCircle, AlertCircle, Filter, Download, Search } from 'lucide-react';
import { API_BASE } from '../config.js';

const StatusBadge = ({ status }) => {
  const styles = {
    success: 'bg-emerald-100/80 text-emerald-700 border-emerald-200',
    passed: 'bg-emerald-100/80 text-emerald-700 border-emerald-200',
    failed: 'bg-red-100/80 text-red-700 border-red-200',
    pending: 'bg-amber-100/80 text-amber-700 border-amber-200',
    warning: 'bg-orange-100/80 text-orange-700 border-orange-200',
  };

  const icons = {
    success: CheckCircle,
    passed: CheckCircle,
    failed: XCircle,
    pending: AlertCircle,
    warning: AlertCircle,
  };

  const Icon = icons[status] || Activity;

  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm ${styles[status] || 'bg-slate-100/80 text-slate-700 border-slate-200'}`}>
      <Icon size={12} />
      {status}
    </span>
  );
};

const AuditTrail = () => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchAuditLogs();
    const interval = setInterval(fetchAuditLogs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAuditLogs = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/audit`);
      if (response.ok) {
        const data = await response.json();
        setAuditLogs(data.audit_logs || []);
      } else {
        setAuditLogs([]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
      setAuditLogs([]);
      setLoading(false);
    }
  };

  const filteredLogs = auditLogs.filter(log => {
    const matchesFilter = filter === 'all' || log.status === filter;
    const matchesSearch = searchTerm === '' || 
      (log.action?.toLowerCase() ?? '').includes(searchTerm.toLowerCase()) ||
      (log.user?.toLowerCase() ?? '').includes(searchTerm.toLowerCase()) ||
      (log.module?.toLowerCase() ?? '').includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const exportLogs = () => {
    const escapeCSV = (field) => `"${String(field ?? '').replace(/"/g, '""')}"`;
    const csv = [
      ['Time', 'User', 'Action', 'Module', 'Status'].map(escapeCSV).join(','),
      ...filteredLogs.map(log =>
        [log.time, log.user, log.action, log.module, log.status].map(escapeCSV).join(',')
      )
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-trail-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with Glassmorphic Design */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-orange-50/70 to-amber-50/70 backdrop-blur-xl border border-orange-100/50 rounded-3xl p-8 shadow-lg"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 mb-2">Audit Trail</h1>
            <p className="text-slate-600">Immutable blockchain-verified activity logs</p>
          </div>
          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={exportLogs}
              className="flex items-center gap-2 px-4 py-2 bg-white/80 hover:bg-white backdrop-blur-sm border border-orange-200 rounded-xl font-medium text-slate-700 shadow-sm transition-all"
            >
              <Download size={18} />
              Export CSV
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Filters & Search - Glassmorphic */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white/60 backdrop-blur-xl border border-orange-100/50 rounded-2xl p-6 shadow-sm"
      >
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-400 transition-all"
            />
          </div>

          {/* Filter Buttons */}
          <div className="flex gap-2">
            {['all', 'success', 'failed', 'pending', 'warning'].map((status) => (
              <motion.button
                key={status}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-xl font-medium transition-all backdrop-blur-sm ${
                  filter === status
                    ? 'bg-orange-500 text-white shadow-md'
                    : 'bg-white/80 text-slate-600 hover:bg-white border border-slate-200'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </motion.button>
            ))}
          </div>
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-slate-600">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-orange-500" />
            <span>Total Logs: <strong>{auditLogs.length}</strong></span>
          </div>
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-orange-500" />
            <span>Filtered: <strong>{filteredLogs.length}</strong></span>
          </div>
        </div>
      </motion.div>

      {/* Audit Logs Table - Glassmorphic */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-xl border border-orange-100/50 rounded-2xl shadow-lg overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-orange-100/50 to-amber-100/50 backdrop-blur-sm">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  <div className="flex items-center gap-2">
                    <Clock size={14} />
                    Time
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  <div className="flex items-center gap-2">
                    <User size={14} />
                    User/Agent
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Module
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-orange-100/30">
              <AnimatePresence>
                {loading ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center">
                      <div className="flex items-center justify-center gap-2 text-slate-500">
                        <div className="w-5 h-5 border-2 border-slate-300 border-t-orange-500 rounded-full animate-spin"></div>
                        Loading audit logs...
                      </div>
                    </td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                      No audit logs found
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log, index) => (
                    <motion.tr
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: index * 0.03 }}
                      className="hover:bg-orange-50/30 transition-colors backdrop-blur-sm"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-700">
                        {log.time}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                           <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center text-white text-xs font-bold">
                             {(log.user || '?').charAt(0)}
                          </div>
                          <span className="text-sm font-medium text-slate-700">{log.user}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600 max-w-xs truncate">
                        {log.action}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-slate-600">{log.module}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={log.status} />
                      </td>
                    </motion.tr>
                  ))
                )}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Stats Footer - Glassmorphic */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        {[
          { label: 'Total Events', value: auditLogs.length, color: 'from-blue-400 to-cyan-400' },
          { label: 'Success Rate', value: `${auditLogs.length > 0 ? Math.round((auditLogs.filter(l => l.status === 'success' || l.status === 'passed').length / auditLogs.length) * 100) : 0}%`, color: 'from-emerald-400 to-green-400' },
          { label: 'Failed', value: auditLogs.filter(l => l.status === 'failed').length, color: 'from-red-400 to-rose-400' },
          { label: 'Pending', value: auditLogs.filter(l => l.status === 'pending').length, color: 'from-amber-400 to-orange-400' },
        ].map((stat, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            className="bg-white/60 backdrop-blur-xl border border-orange-100/50 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mb-3 shadow-lg`}>
              <Activity className="text-white" size={24} />
            </div>
            <p className="text-sm text-slate-600 mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-slate-800">{stat.value}</p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default AuditTrail;
