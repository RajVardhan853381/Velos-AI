import React, { useState, useEffect, lazy, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, ShieldCheck, Network, Activity, Eye, 
  Database, Trophy, GitCompare, Zap, Users, Menu, X,
  Sparkles, TrendingUp, CheckCircle2, Cpu, Upload,
  Search, MessageSquare, ClipboardList, Shield
} from 'lucide-react';
import { API_BASE } from './config.js';

// Lazy-loaded components — each chunk loads only when the tab is first visited
const Dashboard = lazy(() => import('./components/Dashboard'));
const VerificationPipeline = lazy(() => import('./components/VerificationPipeline'));
const Candidates = lazy(() => import('./components/Candidates'));
const Leaderboard = lazy(() => import('./components/Leaderboard'));
const GodMode = lazy(() => import('./components/GodMode'));
const CompareCandidates = lazy(() => import('./components/CompareCandidates'));
const TrustPacketVisualization = lazy(() => import('./components/TrustPacketVisualization'));
const RAGEvidenceExplorer = lazy(() => import('./components/RAGEvidenceExplorer'));
const LiveAgentDashboard = lazy(() => import('./components/LiveAgentDashboard'));
const ZeroBiasProof = lazy(() => import('./components/ZeroBiasProof'));
const BatchUpload = lazy(() => import('./components/BatchUpload'));
const ResumeScreener = lazy(() => import('./components/ResumeScreener'));
const AIInterviewer = lazy(() => import('./components/AIInterviewer'));
const AssessmentGenerator = lazy(() => import('./components/AssessmentGenerator'));
const AntiCheat = lazy(() => import('./components/AntiCheat'));
const AuditTrail = lazy(() => import('./components/AuditTrail'));

// Static nav & quick-action config — defined outside App to avoid re-creation on render
const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, badge: null },
  { id: 'verify', label: 'Verify', icon: ShieldCheck, badge: null },
  { id: 'screener', label: 'AI Screener', icon: Search, badge: 'New' },
  { id: 'interviewer', label: 'AI Interview', icon: MessageSquare, badge: 'New' },
  { id: 'assessment', label: 'Assessments', icon: ClipboardList, badge: 'New' },
  { id: 'anti-cheat', label: 'Anti-Cheat', icon: Shield, badge: 'New' },
  { id: 'candidates', label: 'Candidates', icon: Users, badge: null },
  { id: 'blockchain', label: 'Blockchain', icon: Network, badge: null },
  { id: 'live-agents', label: 'Live Agents', icon: Activity, badge: '3' },
  { id: 'evidence', label: 'Evidence', icon: Database, badge: null },
  { id: 'bias-proof', label: 'Zero Bias', icon: Eye, badge: null },
  { id: 'compare', label: 'Compare', icon: GitCompare, badge: null },
  { id: 'batch-upload', label: 'Batch Upload', icon: Upload, badge: null },
  { id: 'leaderboard', label: 'Leaderboard', icon: Trophy, badge: null },
  { id: 'audit', label: 'Audit Trail', icon: Activity, badge: null },
  { id: 'godmode', label: 'God Mode', icon: Zap, badge: null }
];

// Animated Background Component
const AnimatedBackground = () => {
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Gradient Orbs — static when user prefers reduced motion */}
      <motion.div
        animate={prefersReducedMotion ? false : {
          x: [0, 100, 0],
          y: [0, -100, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute top-0 left-0 w-[600px] h-[600px] bg-gradient-to-br from-purple-400/30 via-blue-500/30 to-indigo-600/30 rounded-full blur-3xl"
      />
      
      <motion.div
        animate={prefersReducedMotion ? false : {
          x: [0, -150, 0],
          y: [0, 100, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
        className="absolute top-1/3 right-0 w-[700px] h-[700px] bg-gradient-to-br from-blue-400/20 via-violet-500/25 to-purple-600/30 rounded-full blur-3xl"
      />
      
      <motion.div
        animate={prefersReducedMotion ? false : {
          x: [0, 80, 0],
          y: [0, -80, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 4
        }}
        className="absolute bottom-0 left-1/3 w-[500px] h-[500px] bg-gradient-to-br from-indigo-400/25 via-purple-500/20 to-pink-600/25 rounded-full blur-3xl"
      />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:100px_100px]" />
    </div>
  );
};

// Glassmorphic Navigation Item
const GlassNavItem = ({ icon: Icon, label, active, onClick, badge }) => {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.95 }}
      className="relative group"
    >
      <div className={`
        relative flex items-center gap-3 px-5 py-3 rounded-2xl
        transition-all duration-300
        ${active 
          ? 'text-white shadow-lg shadow-purple-500/30' 
          : 'text-gray-700 hover:text-purple-700'
        }
      `}>
        {/* Glassmorphic Background for Active */}
        {active && (
          <motion.div
            layoutId="activeGlassNav"
            className="absolute inset-0 bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-600 rounded-2xl"
            style={{
              boxShadow: '0 8px 32px rgba(99, 102, 241, 0.35), inset 0 1px 0 rgba(255,255,255,0.3)'
            }}
            initial={false}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
          />
        )}
        
        {/* Glass Hover Effect */}
        {!active && (
          <motion.div
            className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
            style={{
              background: 'rgba(255, 255, 255, 0.4)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.6)',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.1)'
            }}
          />
        )}

        <motion.div
          whileHover={{ rotate: [0, -10, 10, -10, 0] }}
          transition={{ duration: 0.5 }}
          className="relative z-10"
        >
          <Icon size={20} className={active ? 'drop-shadow-lg' : ''} />
        </motion.div>
        
        <span className="relative z-10 text-sm font-semibold whitespace-nowrap">
          {label}
        </span>

        {/* Badge */}
        {badge && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="relative z-10 ml-auto"
          >
            <div className="px-2 py-0.5 bg-white/90 backdrop-blur-sm rounded-full text-xs font-bold text-purple-600 shadow-sm">
              {badge}
            </div>
          </motion.div>
        )}

        {/* Glow Effect on Active */}
        {active && (
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute inset-0 bg-gradient-to-br from-purple-400 to-blue-500 rounded-2xl blur-xl opacity-50 -z-10"
          />
        )}
      </div>
    </motion.button>
  );
};

// Glassmorphic Stats Card with 3D Effect
const GlassStatsCard = ({ icon: Icon, title, value, trend, gradient, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, rotateX: -15 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ delay, duration: 0.5 }}
      whileHover={{ 
        scale: 1.05, 
        rotateY: 5,
        rotateX: 5,
        transition: { duration: 0.3 }
      }}
      className="relative group perspective-1000"
    >
      <div 
        className="relative rounded-3xl p-6 transform-gpu transition-all duration-300"
        style={{
          background: 'rgba(255, 255, 255, 0.3)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.5)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.6)',
        }}
      >
        {/* Gradient Overlay */}
        <div 
          className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 rounded-3xl transition-opacity duration-300`}
        />

        {/* Icon with Glow */}
        <motion.div 
          whileHover={{ rotate: 360, scale: 1.1 }}
          transition={{ duration: 0.6 }}
          className="relative w-14 h-14 rounded-2xl bg-gradient-to-br from-white/60 to-white/40 backdrop-blur-sm flex items-center justify-center mb-4"
          style={{
            boxShadow: `0 4px 16px ${gradient.includes('purple') ? 'rgba(168, 85, 247, 0.3)' : 'rgba(59, 130, 246, 0.3)'}`
          }}
        >
          <Icon className={`${gradient.includes('purple') ? 'text-purple-600' : 'text-blue-600'}`} size={28} />
          
          {/* Icon Glow */}
          <motion.div
            animate={{ opacity: [0.4, 0.8, 0.4], scale: [0.8, 1.2, 0.8] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-2xl blur-md -z-10`}
          />
        </motion.div>

        <div className="relative">
          <h3 className="text-sm font-semibold text-gray-600 mb-1">{title}</h3>
          <div className="flex items-end gap-3">
            <motion.p 
              className="text-3xl font-bold bg-gradient-to-br from-gray-900 to-gray-600 bg-clip-text text-transparent"
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.2, type: "spring" }}
            >
              {value}
            </motion.p>
            {trend && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: delay + 0.3 }}
                className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
                  trend > 0 ? 'bg-green-100/80 text-green-700' : 'bg-red-100/80 text-red-700'
                }`}
              >
                <TrendingUp size={14} className={trend < 0 ? 'rotate-180' : ''} />
                {Math.abs(trend)}%
              </motion.div>
            )}
          </div>
        </div>

        {/* Bottom Glow */}
        <div className={`absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-px bg-gradient-to-r ${gradient} opacity-30 group-hover:opacity-60 transition-opacity`} />
      </div>
    </motion.div>
  );
};

// Quick Action Card with 3D Glass Effect
const QuickActionCard = ({ icon: Icon, title, description, onClick, gradient }) => (
  <motion.button
    whileHover={{ scale: 1.05, rotateY: 5, rotateX: 5 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className="relative group text-left transform-gpu perspective-1000"
  >
    <div 
      className="relative rounded-3xl p-6 transition-all duration-300"
      style={{
        background: 'rgba(255, 255, 255, 0.25)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(255, 255, 255, 0.4)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.5)',
      }}
    >
      {/* Gradient Background on Hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-15 rounded-3xl transition-opacity`} />
      
      {/* Icon */}
      <motion.div
        whileHover={{ rotate: [0, -5, 5, -5, 0], scale: 1.1 }}
        transition={{ duration: 0.5 }}
        className="relative w-12 h-12 rounded-xl bg-gradient-to-br from-white/70 to-white/50 flex items-center justify-center mb-4"
        style={{
          boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)'
        }}
      >
        <Icon className="text-indigo-600" size={24} />
      </motion.div>

      <h3 className="relative text-lg font-bold text-gray-900 mb-2">{title}</h3>
      <p className="relative text-sm text-gray-600">{description}</p>

      {/* Hover Arrow */}
      <motion.div
        initial={{ x: -10, opacity: 0 }}
        whileHover={{ x: 0, opacity: 1 }}
        className="absolute top-6 right-6 text-indigo-600"
      >
        <Sparkles size={20} />
      </motion.div>

      {/* Bottom Glow */}
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r ${gradient} rounded-b-3xl`}
      />
    </div>
  </motion.button>
);

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [stats, setStats] = useState({
    candidates: 0,
    verified: 0,
    agents: 0,
    accuracy: 0
  });

  // Fetch real stats then animate counter up to fetched values
  useEffect(() => {
    const animate = (targets) => {
      const duration = 2000;
      const steps = 60;
      const interval = duration / steps;
      let step = 0;
      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        setStats({
          candidates: Math.floor(targets.candidates * progress),
          verified: Math.floor(targets.verified * progress),
          agents: Math.floor(targets.agents * progress),
          accuracy: Math.floor(targets.accuracy * progress),
        });
        if (step >= steps) clearInterval(timer);
      }, interval);
      return timer;
    };

    let timer;
    fetch(`${API_BASE}/api/stats`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        const targets = data
          ? {
              candidates: data.total_candidates ?? 0,
              verified: data.approved_total ?? 0,
              agents: 3,
              accuracy: data.total_candidates > 0
                ? Math.round((data.approved_total / data.total_candidates) * 100)
                : 0,
            }
          : { candidates: 0, verified: 0, agents: 3, accuracy: 0 };
        timer = animate(targets);
      })
      .catch(() => {
        timer = animate({ candidates: 0, verified: 0, agents: 3, accuracy: 0 });
      });

    return () => clearInterval(timer);
  }, []);

  // Listen for navigate events dispatched by child components (e.g. Dashboard "View All")
  useEffect(() => {
    const handler = (e) => setActiveTab(e.detail);
    window.addEventListener('navigate', handler);
    return () => window.removeEventListener('navigate', handler);
  }, []);

  const navItems = NAV_ITEMS;

  const quickActions = [
    {
      icon: Search,
      title: 'AI Resume Screener',
      description: 'Context-aware matching with hidden gem detection',
      gradient: 'from-violet-500 to-purple-600',
      onClick: () => setActiveTab('screener')
    },
    {
      icon: MessageSquare,
      title: 'AI Interviewer',
      description: 'Dynamic conversational screening agent',
      gradient: 'from-blue-500 to-indigo-600',
      onClick: () => setActiveTab('interviewer')
    },
    {
      icon: ClipboardList,
      title: 'Assessment Generator',
      description: 'Instant AI-generated technical tests',
      gradient: 'from-emerald-500 to-teal-600',
      onClick: () => setActiveTab('assessment')
    },
    {
      icon: Shield,
      title: 'Anti-Cheat Proctor',
      description: 'Real-time CV face detection & tab monitoring',
      gradient: 'from-rose-500 to-pink-600',
      onClick: () => setActiveTab('anti-cheat')
    },
    {
      icon: ShieldCheck,
      title: 'Verify Candidate',
      description: 'Run the full AI verification pipeline',
      gradient: 'from-purple-500 to-indigo-600',
      onClick: () => setActiveTab('verify')
    },
    {
      icon: Network,
      title: 'View Trust Packets',
      description: 'Blockchain credentials & DIDs',
      gradient: 'from-blue-500 to-cyan-600',
      onClick: () => setActiveTab('blockchain')
    },
    {
      icon: Activity,
      title: 'Monitor Agents',
      description: 'Real-time agent communication',
      gradient: 'from-violet-500 to-purple-600',
      onClick: () => setActiveTab('live-agents')
    },
    {
      icon: Database,
      title: 'Explore Evidence',
      description: 'RAG-powered evidence search',
      gradient: 'from-indigo-500 to-blue-600',
      onClick: () => setActiveTab('evidence')
    }
  ];

  const renderContent = () => {
    const content = (() => {
      switch (activeTab) {
        case 'dashboard':
          return <Dashboard />;
        case 'verify':
          return <VerificationPipeline />;
        case 'screener':
          return <ResumeScreener />;
        case 'interviewer':
          return <AIInterviewer />;
        case 'assessment':
          return <AssessmentGenerator />;
        case 'anti-cheat':
          return <AntiCheat />;
        case 'candidates':
          return <Candidates />;
        case 'blockchain':
          return <TrustPacketVisualization />;
        case 'live-agents':
          return <LiveAgentDashboard />;
        case 'evidence':
          return <RAGEvidenceExplorer />;
        case 'bias-proof':
          return <ZeroBiasProof />;
        case 'compare':
          return <CompareCandidates />;
        case 'batch-upload':
          return <BatchUpload />;
        case 'leaderboard':
          return <Leaderboard />;
        case 'audit':
          return <AuditTrail />;
        case 'godmode':
          return <GodMode />;
        default:
          return <Dashboard />;
      }
    })();

    const fallback = (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    );

    // Wrap content in glass container for non-dashboard tabs
    if (activeTab !== 'dashboard') {
      return (
        <div 
          className="rounded-3xl p-8"
          style={{
            background: 'rgba(255, 255, 255, 0.35)',
            backdropFilter: 'blur(24px)',
            border: '1px solid rgba(255, 255, 255, 0.6)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
          }}
        >
          <Suspense fallback={fallback}>{content}</Suspense>
        </div>
      );
    }
    
    return <Suspense fallback={fallback}>{content}</Suspense>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 relative">
      <AnimatedBackground />

      {/* Top Navigation Bar - Glassmorphic */}
      <motion.nav 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-0 z-50 mb-8"
      >
        <div 
          className="mx-4 mt-4 rounded-3xl"
          style={{
            background: 'rgba(255, 255, 255, 0.4)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.6)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
          }}
        >
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <motion.div 
                className="flex items-center gap-3"
                whileHover={{ scale: 1.05 }}
              >
                <motion.div 
                  animate={{ 
                    rotate: 360,
                    boxShadow: [
                      '0 0 20px rgba(168, 85, 247, 0.3)',
                      '0 0 40px rgba(99, 102, 241, 0.5)',
                      '0 0 20px rgba(168, 85, 247, 0.3)'
                    ]
                  }}
                  transition={{ 
                    rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                    boxShadow: { duration: 2, repeat: Infinity }
                  }}
                  className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 via-blue-500 to-indigo-600 flex items-center justify-center"
                >
                  <Sparkles className="text-white" size={24} />
                </motion.div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    Velos AI
                  </h1>
                  <p className="text-xs text-gray-600">Blockchain-Powered Hiring</p>
                </div>
              </motion.div>

              {/* Mobile Menu Button */}
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-xl bg-white/60 backdrop-blur-sm"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </motion.button>
            </div>

            {/* Desktop Navigation — two wrapping rows so all items are always visible */}
            <div className="hidden lg:flex flex-wrap gap-1 pt-3 border-t border-white/30">
              {navItems.map((item) => (
                <GlassNavItem
                  key={item.id}
                  icon={item.icon}
                  label={item.label}
                  active={activeTab === item.id}
                  onClick={() => setActiveTab(item.id)}
                  badge={item.badge}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden mx-4 mt-2 rounded-3xl overflow-hidden"
              style={{
                background: 'rgba(255, 255, 255, 0.4)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.6)',
              }}
            >
              <div className="p-4 space-y-2">
                {navItems.map((item) => (
                  <GlassNavItem
                    key={item.id}
                    icon={item.icon}
                    label={item.label}
                    active={activeTab === item.id}
                    onClick={() => {
                      setActiveTab(item.id);
                      setMobileMenuOpen(false);
                    }}
                    badge={item.badge}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>

      {/* Main Content */}
      <div className="px-4 pb-8">
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' ? (
            <motion.div
              key="dashboard-custom"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-7xl mx-auto space-y-8"
            >
              {/* Hero Section */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6 }}
                className="relative rounded-3xl p-12 overflow-hidden"
                style={{
                  background: 'rgba(255, 255, 255, 0.3)',
                  backdropFilter: 'blur(24px)',
                  border: '1px solid rgba(255, 255, 255, 0.5)',
                  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.7)',
                }}
              >
                {/* Background Decoration */}
                <motion.div
                  animate={{ 
                    rotate: 360,
                    scale: [1, 1.2, 1]
                  }}
                  transition={{ 
                    rotate: { duration: 30, repeat: Infinity, ease: "linear" },
                    scale: { duration: 8, repeat: Infinity }
                  }}
                  className="absolute -top-20 -right-20 w-80 h-80 bg-gradient-to-br from-purple-300/30 to-blue-400/30 rounded-full blur-3xl"
                />

                <div className="relative">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <h2 className="text-5xl font-black mb-4 bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
                      Welcome to the Future
                    </h2>
                    <p className="text-xl text-gray-700 mb-6 max-w-2xl">
                      AI-powered blind hiring with blockchain verification. Zero bias. Maximum trust.
                    </p>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="flex gap-4"
                  >
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setActiveTab('verify')}
                      className="px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-500 via-blue-500 to-indigo-600 text-white font-bold shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-shadow"
                      style={{
                        boxShadow: '0 4px 20px rgba(168, 85, 247, 0.4), inset 0 1px 0 rgba(255,255,255,0.3)'
                      }}
                    >
                      Start Verification
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setActiveTab('blockchain')}
                      className="px-8 py-4 rounded-2xl bg-white/50 backdrop-blur-sm text-gray-900 font-bold border border-white/60 hover:bg-white/70 transition-colors"
                    >
                      View Blockchain
                    </motion.button>
                  </motion.div>
                </div>
              </motion.div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <GlassStatsCard
                  icon={Users}
                  title="Total Candidates"
                  value={stats.candidates.toLocaleString()}
                  trend={12}
                  gradient="from-purple-500 to-pink-600"
                  delay={0}
                />
                <GlassStatsCard
                  icon={CheckCircle2}
                  title="Verified"
                  value={stats.verified.toLocaleString()}
                  trend={8}
                  gradient="from-blue-500 to-cyan-600"
                  delay={0.1}
                />
                <GlassStatsCard
                  icon={Cpu}
                  title="Active Agents"
                  value={stats.agents}
                  trend={null}
                  gradient="from-violet-500 to-purple-600"
                  delay={0.2}
                />
                <GlassStatsCard
                  icon={Sparkles}
                  title="Accuracy"
                  value={`${stats.accuracy}%`}
                  trend={3}
                  gradient="from-indigo-500 to-blue-600"
                  delay={0.3}
                />
              </div>

              {/* Quick Actions */}
              <div>
                <motion.h3
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-2xl font-bold text-gray-900 mb-6"
                >
                  Quick Actions
                </motion.h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {quickActions.map((action, index) => (
                    <motion.div
                      key={action.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + index * 0.1 }}
                    >
                      <QuickActionCard {...action} />
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* System Status */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="rounded-3xl p-8"
                style={{
                  background: 'rgba(255, 255, 255, 0.25)',
                  backdropFilter: 'blur(16px)',
                  border: '1px solid rgba(255, 255, 255, 0.4)',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.06)',
                }}
              >
                <h3 className="text-xl font-bold text-gray-900 mb-6">System Status</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[
                    { label: 'Blockchain Network', status: 'Connected', color: 'green', detail: 'Optimism Sepolia' },
                    { label: 'AI Agents', status: 'Active', color: 'blue', detail: '3 agents online' },
                    { label: 'ZeroMQ Hub', status: 'Running', color: 'purple', detail: 'P2P messaging active' },
                    { label: 'GenAI Screener', status: 'Ready', color: 'green', detail: 'Llama 3.3 70B via Groq' },
                    { label: 'AI Interviewer', status: 'Ready', color: 'blue', detail: 'Conversational sessions' },
                    { label: 'Anti-Cheat', status: 'Ready', color: 'purple', detail: 'OpenCV + WebSocket' },
                  ].map((item, index) => (
                    <motion.div
                      key={item.label}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.9 + index * 0.1 }}
                      className="flex items-center gap-4 p-4 rounded-2xl bg-white/40 backdrop-blur-sm border border-white/50"
                    >
                      <motion.div
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className={`w-3 h-3 rounded-full ${
                          item.color === 'green' ? 'bg-green-500' :
                          item.color === 'blue' ? 'bg-blue-500' : 'bg-purple-500'
                        } shadow-lg`}
                        style={{
                          boxShadow: `0 0 12px ${
                            item.color === 'green' ? 'rgba(34, 197, 94, 0.6)' :
                            item.color === 'blue' ? 'rgba(59, 130, 246, 0.6)' : 'rgba(168, 85, 247, 0.6)'
                          }`
                        }}
                      />
                      <div>
                        <p className="font-semibold text-gray-900">{item.label}</p>
                        <p className="text-sm text-gray-600">{item.status} · {item.detail}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="max-w-7xl mx-auto"
            >
              {renderContent()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
