import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Activity, MessageSquare, Send, CheckCircle, Clock, Shield,
  Package, Fingerprint, ArrowRight, Radio, RefreshCw, Zap,
  User, Bot, Link as LinkIcon, Eye, ChevronDown, Database
} from 'lucide-react';
import { API_BASE } from '../config.js';

// Message type icons and colors
const getMessageTypeConfig = (type) => {
  const configs = {
    'TASK_HANDOFF': {
      icon: ArrowRight,
      color: 'from-blue-100/60 to-indigo-100/60',
      borderColor: 'border-blue-200/60',
      iconColor: 'text-blue-600',
      label: 'Task Handoff'
    },
    'CREDENTIAL_ISSUED': {
      icon: Shield,
      color: 'from-green-100/60 to-emerald-100/60',
      borderColor: 'border-green-200/60',
      iconColor: 'text-green-600',
      label: 'Credential Issued'
    },
    'VERIFICATION_REQUEST': {
      icon: Eye,
      color: 'from-yellow-100/60 to-orange-100/60',
      borderColor: 'border-yellow-200/60',
      iconColor: 'text-yellow-600',
      label: 'Verification Request'
    },
    'VERIFICATION_COMPLETE': {
      icon: CheckCircle,
      color: 'from-purple-100/60 to-pink-100/60',
      borderColor: 'border-purple-200/60',
      iconColor: 'text-purple-600',
      label: 'Verification Complete'
    },
    'AUTHENTICITY_CHECK_REQUEST': {
      icon: Fingerprint,
      color: 'from-pink-100/60 to-rose-100/60',
      borderColor: 'border-pink-200/60',
      iconColor: 'text-pink-600',
      label: 'Authenticity Check'
    },
    'AGENT_STATUS': {
      icon: Activity,
      color: 'from-cyan-100/60 to-teal-100/60',
      borderColor: 'border-cyan-200/60',
      iconColor: 'text-cyan-600',
      label: 'Status Update'
    },
    'ERROR': {
      icon: Zap,
      color: 'from-red-500/20 to-pink-500/20',
      borderColor: 'border-red-500/40',
      iconColor: 'text-red-400',
      label: 'Error'
    }
  };

  return configs[type] || {
    icon: MessageSquare,
    color: 'from-gray-500/20 to-slate-500/20',
    borderColor: 'border-gray-500/40',
    iconColor: 'text-gray-400',
    label: type || 'Message'
  };
};

// Agent avatar component
const AgentAvatar = ({ agentName, size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12'
  };

  const iconSizes = {
    sm: 16,
    md: 20,
    lg: 24
  };

  const getAgentColor = (name) => {
    if (name?.includes('Gatekeeper')) return 'from-blue-500 to-indigo-600';
    if (name?.includes('Validator')) return 'from-green-500 to-emerald-600';
    if (name?.includes('Inquisitor')) return 'from-purple-500 to-pink-600';
    if (name?.includes('Orchestrator')) return 'from-orange-500 to-red-600';
    return 'from-gray-500 to-slate-600';
  };

  const getAgentIcon = (name) => {
    if (name?.includes('Gatekeeper')) return Shield;
    if (name?.includes('Validator')) return Package;
    if (name?.includes('Inquisitor')) return Fingerprint;
    if (name?.includes('Orchestrator')) return Database;
    return Bot;
  };

  const Icon = getAgentIcon(agentName);

  return (
    <div className={`${sizeClasses[size]} bg-gradient-to-br ${getAgentColor(agentName)} rounded-lg flex items-center justify-center shadow-lg`}>
      <Icon className="text-white" size={iconSizes[size]} />
    </div>
  );
};

// Message card component
const MessageCard = ({ message, index, expanded, onToggle }) => {
  const config = getMessageTypeConfig(message.message_type);
  const Icon = config.icon;

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);

    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    return date.toLocaleTimeString();
  };

  const fromAgent = message.sender_did?.split(':').pop()?.slice(0, 8) || 'Unknown';
  const toAgent = message.recipient_did?.split(':').pop()?.slice(0, 8) || 'Unknown';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ delay: index * 0.03 }}
      className={`bg-gradient-to-br ${config.color} backdrop-blur-xl border ${config.borderColor} rounded-xl p-4 shadow-lg hover:shadow-2xl transition-all`}
    >
      <div className="flex items-start gap-3">
        {/* Message type icon */}
        <div className={`w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0`}>
          <Icon className={config.iconColor} size={20} />
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className={`${config.iconColor} font-semibold text-sm`}>
                {config.label}
              </span>
              <span className="text-xs text-gray-900/50">•</span>
              <span className="text-xs text-gray-900/70">{formatTimestamp(message.timestamp)}</span>
            </div>
            <button
              onClick={() => onToggle(message.message_id)}
              className="text-gray-900/50 hover:text-gray-900 transition-colors"
            >
              <motion.div
                animate={{ rotate: expanded ? 180 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronDown size={16} />
              </motion.div>
            </button>
          </div>

          {/* Agent flow */}
          <div className="flex items-center gap-2 mb-3">
            <AgentAvatar agentName={message.from || fromAgent} size="sm" />
            <span className="text-gray-900/70 text-xs font-mono">{message.from || `...${fromAgent}`}</span>
            <ArrowRight className="text-gray-900/40" size={14} />
            <AgentAvatar agentName={message.to || toAgent} size="sm" />
            <span className="text-gray-900/70 text-xs font-mono">{message.to || `...${toAgent}`}</span>
          </div>

          {/* Message ID */}
          <div className="flex items-center gap-2 mb-2">
            <LinkIcon className="text-gray-900/40" size={12} />
            <span className="text-xs text-gray-900/50 font-mono">
              {message.message_id?.slice(0, 16)}...
            </span>
          </div>

          {/* Expanded content */}
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-white/10"
              >
                {/* Content */}
                {message.content && (
                  <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg mb-3">
                    <p className="text-gray-500 text-xs mb-1">Content</p>
                    <pre className="text-gray-800 text-xs font-mono overflow-x-auto">
                      {typeof message.content === 'object' 
                        ? JSON.stringify(message.content, null, 2)
                        : message.content}
                    </pre>
                  </div>
                )}

                {/* Full DIDs */}
                <div className="space-y-2">
                  <div className="p-2 bg-gray-50 border border-gray-200 rounded text-xs">
                    <p className="text-gray-500 mb-1">Sender DID</p>
                    <p className="text-gray-700 font-mono break-all">{message.sender_did}</p>
                  </div>
                  <div className="p-2 bg-gray-50 border border-gray-200 rounded text-xs">
                    <p className="text-gray-500 mb-1">Recipient DID</p>
                    <p className="text-gray-700 font-mono break-all">{message.recipient_did}</p>
                  </div>
                  
                  {/* Signature */}
                  {message.signature && (
                    <div className="p-2 bg-green-50 border border-green-300 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        <CheckCircle className="text-green-600" size={12} />
                        <p className="text-green-700 font-semibold">DID Signature</p>
                      </div>
                      <p className="text-green-600 font-mono break-all">{message.signature}</p>
                    </div>
                  )}

                  {/* Conversation context */}
                  {message.conversation_id && (
                    <div className="p-2 bg-gray-50 border border-gray-200 rounded text-xs">
                      <p className="text-gray-500 mb-1">Conversation ID</p>
                      <p className="text-gray-700 font-mono">{message.conversation_id}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};

// Live stats component
const LiveStats = ({ stats }) => {
  return (
    <div className="grid grid-cols-4 gap-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-br from-white/40 to-white/30 border border-blue-500/30 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="text-blue-600" size={20} />
          <p className="text-gray-600 text-sm">Total Messages</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.total || 0}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-300 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle className="text-green-600" size={20} />
          <p className="text-green-700 text-sm">Verified</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.verified || 0}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-white/40 to-white/30 border border-purple-500/30 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Activity className="text-purple-600" size={20} />
          <p className="text-gray-600 text-sm">Active Agents</p>
        </div>
        <p className="text-gray-900 text-2xl font-bold">{stats.active_agents || 0}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
        className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-300 rounded-xl p-4"
      >
        <div className="flex items-center gap-2 mb-2">
          <Clock className="text-amber-600" size={20} />
          <p className="text-amber-700 text-sm">Last Update</p>
        </div>
        <p className="text-gray-900 text-sm">{stats.last_update || 'Never'}</p>
      </motion.div>
    </div>
  );
};

// Main component
const LiveAgentDashboard = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [expandedMessages, setExpandedMessages] = useState(new Set());
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchMessages = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/agents/messages?limit=50`);

      if (response.ok) {
        const data = await response.json();
        
        if (data.enabled) {
          setMessages(data.messages || []);
        } else {
          setError('Agent communication not enabled. Blockchain integration may not be active.');
        }
      } else {
        setError('Failed to fetch agent messages');
      }
    } catch (err) {
      console.error('Failed to fetch messages:', err);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchMessages();

    // Setup auto-refresh if enabled
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchMessages, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoRefresh]);

  const toggleExpanded = (messageId) => {
    const newExpanded = new Set(expandedMessages);
    if (newExpanded.has(messageId)) {
      newExpanded.delete(messageId);
    } else {
      newExpanded.add(messageId);
    }
    setExpandedMessages(newExpanded);
  };

  // Calculate stats
  const stats = {
    total: messages.length,
    verified: messages.filter(m => m.signature).length,
    active_agents: new Set([
      ...messages.map(m => m.sender_did),
      ...messages.map(m => m.recipient_did)
    ].filter(Boolean)).size,
    last_update: messages.length > 0 
      ? new Date(messages[0].timestamp).toLocaleTimeString()
      : 'Never'
  };

  return (
    <div className="p-0">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-2xl">
              <Radio className="text-gray-900 animate-pulse" size={32} />
            </div>
            <div>
              <h1 className="text-5xl font-bold text-gray-900">Live Agent Dashboard</h1>
              <p className="text-gray-600 text-lg">Real-time blockchain-authenticated messaging</p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                autoRefresh
                  ? 'bg-green-600 text-gray-900'
                  : 'bg-white/10 text-gray-900/70 hover:bg-white/20'
              }`}
            >
              <Activity size={18} className={autoRefresh ? 'animate-pulse' : ''} />
              {autoRefresh ? 'Live' : 'Paused'}
            </button>

            <button
              onClick={fetchMessages}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-400 hover:bg-blue-500 text-gray-900 rounded-lg font-semibold transition-all disabled:opacity-50"
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
          </div>
        </div>
      </motion.div>

      {/* Stats */}
      <LiveStats stats={stats} />

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-amber-50 border border-amber-400 rounded-lg flex items-center gap-3"
        >
          <Zap className="text-amber-600" size={20} />
          <p className="text-amber-800">{error}</p>
        </motion.div>
      )}

      {/* Messages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
            <MessageSquare className="text-indigo-600" />
            Message Stream ({messages.length})
          </h2>
          {autoRefresh && (
            <span className="flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-300 rounded-lg text-green-700 text-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              Auto-refreshing every 5s
            </span>
          )}
        </div>

        {messages.length > 0 ? (
          <div className="space-y-3">
            <AnimatePresence mode="popLayout">
              {messages.map((message, index) => (
                <MessageCard
                  key={message.message_id}
                  message={message}
                  index={index}
                  expanded={expandedMessages.has(message.message_id)}
                  onToggle={toggleExpanded}
                />
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="p-12 bg-white/40 backdrop-blur-xl border border-white/60 rounded-xl text-center">
            <Radio className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600 text-lg">No messages yet</p>
            <p className="text-gray-500 text-sm mt-2">
              Run a verification pipeline to see agent-to-agent communication
            </p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default LiveAgentDashboard;
