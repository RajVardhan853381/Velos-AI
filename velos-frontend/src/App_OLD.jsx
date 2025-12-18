import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, ShieldCheck, FileText, Settings, Menu, Bell, Users, Upload, Trophy, GitCompare, Eye, Zap, X, Search, User } from 'lucide-react';
import Dashboard from './components/Dashboard';
import VerificationPipeline from './components/VerificationPipeline';
import AuditTrail from './components/AuditTrail';
import SettingsComponent from './components/Settings';
import Candidates from './components/Candidates';
import BatchUpload from './components/BatchUpload';
import Leaderboard from './components/Leaderboard';
import TrustPacket from './components/TrustPacket';
import GodMode from './components/GodMode';
import CompareCandidates from './components/CompareCandidates';

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <motion.button
    onClick={onClick}
    whileHover={{ scale: 1.02, x: 4 }}
    whileTap={{ scale: 0.98 }}
    className={`
      flex items-center gap-3 w-full px-4 py-3 rounded-2xl 
      transition-all duration-300 relative group
      ${active 
        ? 'bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-600 shadow-soft' 
        : 'text-gray-600 hover:bg-gray-50/80'
      }
    `}
  >
    {active && (
      <motion.div
        layoutId="activeTab"
        className="absolute inset-0 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl"
        initial={false}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      />
    )}
    <Icon size={20} className={`relative z-10 ${active ? 'text-blue-600' : 'text-gray-500'}`} />
    <span className={`relative z-10 font-medium ${active ? 'text-blue-600' : ''}`}>{label}</span>
    {active && (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="absolute right-3 w-1.5 h-1.5 bg-blue-600 rounded-full"
      />
    )}
  </motion.button>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/30 font-sans text-gray-800 overflow-hidden">
      {/* Mobile Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ x: sidebarOpen ? 0 : '-100%' }}
        className={`
          fixed lg:static inset-y-0 left-0 z-50 w-72
          bg-white/80 backdrop-blur-xl border-r border-gray-200/50
          p-6 flex flex-col justify-between
          lg:translate-x-0 transition-all duration-300 ease-out
          shadow-soft-lg
        `}
      >
        <div className="flex-1 overflow-y-auto">
          {/* Logo */}
          <div className="flex items-center justify-between mb-10 px-2">
            <motion.div 
              className="flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
            >
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  V
                </div>
                <div className="absolute -inset-1 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl blur opacity-20 -z-10"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Velos
                </h1>
                <p className="text-xs text-gray-500">AI Verification</p>
              </div>
            </motion.div>
            <button
              className="lg:hidden p-2 hover:bg-gray-100 rounded-xl transition-colors"
              onClick={() => setSidebarOpen(false)}
            >
              <X size={20} className="text-gray-600" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="space-y-1.5">
            <SidebarItem
              icon={LayoutDashboard}
              label="Dashboard"
              active={activeTab === 'dashboard'}
              onClick={() => { setActiveTab('dashboard'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={ShieldCheck}
              label="Verify Candidate"
              active={activeTab === 'verify'}
              onClick={() => { setActiveTab('verify'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Users}
              label="Candidates"
              active={activeTab === 'candidates'}
              onClick={() => { setActiveTab('candidates'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={GitCompare}
              label="Compare"
              active={activeTab === 'compare'}
              onClick={() => { setActiveTab('compare'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Upload}
              label="Batch Upload"
              active={activeTab === 'batch'}
              onClick={() => { setActiveTab('batch'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Trophy}
              label="Leaderboard"
              active={activeTab === 'leaderboard'}
              onClick={() => { setActiveTab('leaderboard'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Eye}
              label="Trust Packet"
              active={activeTab === 'trust'}
              onClick={() => { setActiveTab('trust'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={FileText}
              label="Audit Trail"
              active={activeTab === 'audit'}
              onClick={() => { setActiveTab('audit'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Zap}
              label="God Mode"
              active={activeTab === 'god'}
              onClick={() => { setActiveTab('god'); setSidebarOpen(false); }}
            />
            <SidebarItem
              icon={Settings}
              label="Settings"
              active={activeTab === 'settings'}
              onClick={() => { setActiveTab('settings'); setSidebarOpen(false); }}
            />
          </nav>
        </div>

        {/* User Profile */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="mt-6 p-4 glass-strong rounded-2xl border border-gray-200/50 shadow-soft cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-semibold shadow-lg">
                JD
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-400 border-2 border-white rounded-full"></div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-800">Divya Chaudhary</p>
              <p className="text-xs text-gray-500">Recruiter Admin</p>
            </div>
          </div>
        </motion.div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-30 h-20 glass-strong border-b border-gray-200/50 shadow-soft">
          <div className="h-full flex items-center justify-between px-4 lg:px-8">
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="lg:hidden p-2.5 hover:bg-gray-100 rounded-xl transition-colors"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu size={22} className="text-gray-700" />
              </motion.button>
              <div>
                <h2 className="text-xl font-bold text-gray-800 capitalize">{activeTab.replace('-', ' ')}</h2>
                <p className="text-xs text-gray-500">Welcome back, Divya!</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Search */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="hidden md:flex items-center gap-2 px-4 py-2 bg-gray-100/80 hover:bg-gray-100 rounded-xl transition-all text-gray-600 text-sm"
              >
                <Search size={16} />
                <span>Search...</span>
                <kbd className="px-2 py-0.5 bg-white rounded text-xs border border-gray-200">⌘K</kbd>
              </motion.button>

              {/* Notifications */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="relative p-2.5 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <Bell size={20} className="text-gray-600" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
              </motion.button>

              {/* User Avatar */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2.5 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <User size={20} className="text-gray-600" />
              </motion.button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 lg:p-8">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {activeTab === 'dashboard' && <Dashboard />}
            {activeTab === 'verify' && <VerificationPipeline />}
            {activeTab === 'candidates' && <Candidates />}
            {activeTab === 'compare' && <CompareCandidates />}
            {activeTab === 'batch' && <BatchUpload />}
            {activeTab === 'leaderboard' && <Leaderboard />}
            {activeTab === 'trust' && <TrustPacket />}
            {activeTab === 'audit' && <AuditTrail />}
            {activeTab === 'god' && <GodMode />}
            {activeTab === 'settings' && <SettingsComponent />}
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default App;
