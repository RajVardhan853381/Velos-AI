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
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    setSearchOpen(!searchOpen);
    setNotificationsOpen(false);
    setUserMenuOpen(false);
    setSearchQuery('');
  };

  const handleNotifications = () => {
    setNotificationsOpen(!notificationsOpen);
    setSearchOpen(false);
    setUserMenuOpen(false);
  };

  const handleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
    setSearchOpen(false);
    setNotificationsOpen(false);
  };

  const notifications = [
    { id: 1, title: 'System Ready', message: 'Velos AI verification system initialized', time: 'Just now', unread: false },
  ];

  const searchResults = searchQuery.length > 0 ? [
    { type: 'Page', name: 'Dashboard', icon: LayoutDashboard, tab: 'dashboard' },
    { type: 'Page', name: 'Verify Candidate', icon: ShieldCheck, tab: 'verify' },
    { type: 'Page', name: 'Candidates', icon: Users, tab: 'candidates' },
    { type: 'Page', name: 'Compare', icon: GitCompare, tab: 'compare' },
    { type: 'Page', name: 'God Mode', icon: Zap, tab: 'god' },
    { type: 'Page', name: 'Settings', icon: Settings, tab: 'settings' },
  ].filter(item => item.name.toLowerCase().includes(searchQuery.toLowerCase())) : [];

  return (
    <div className="flex h-screen bg-white font-sans text-gray-800 overflow-hidden">
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
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50 w-72
          bg-white border-r border-gray-200
          p-6 flex flex-col justify-between
          transition-all duration-300 ease-out
          shadow-lg
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
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
          onClick={handleUserMenu}
          className="mt-6 p-4 glass-strong rounded-2xl border border-gray-200/50 shadow-soft cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-semibold shadow-lg">
                RA
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-400 border-2 border-white rounded-full"></div>
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-800">Recruiter Admin</p>
              <p className="text-xs text-gray-500">Admin User</p>
            </div>
          </div>
        </motion.div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-white">
        {/* Header */}
        <header className="sticky top-0 z-30 h-20 bg-white border-b border-gray-200 shadow-sm">
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
                <p className="text-xs text-gray-500">Welcome back!</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Search */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSearch}
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
                onClick={handleNotifications}
                className="relative p-2.5 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <Bell size={20} className="text-gray-600" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
              </motion.button>

              {/* User Avatar */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleUserMenu}
                className="p-2.5 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <User size={20} className="text-gray-600" />
              </motion.button>
            </div>
          </div>
        </header>

        {/* Search Modal */}
        <AnimatePresence>
          {searchOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-start justify-center pt-20 px-4"
              onClick={() => setSearchOpen(false)}
            >
              <motion.div
                initial={{ scale: 0.95, y: -20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.95, y: -20 }}
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden"
              >
                <div className="flex items-center gap-3 p-4 border-b border-gray-200">
                  <Search size={20} className="text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search candidates, pages, or settings..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                    className="flex-1 outline-none text-gray-800 placeholder-gray-400"
                  />
                  <button
                    onClick={() => setSearchOpen(false)}
                    className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X size={18} className="text-gray-400" />
                  </button>
                </div>
                <div className="max-h-96 overflow-y-auto p-2">
                  {searchQuery.length === 0 ? (
                    <div className="p-8 text-center text-gray-400">
                      <Search size={48} className="mx-auto mb-3 opacity-20" />
                      <p>Start typing to search...</p>
                    </div>
                  ) : searchResults.length === 0 ? (
                    <div className="p-8 text-center text-gray-400">
                      <p>No results found for "{searchQuery}"</p>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      {searchResults.map((result, idx) => (
                        <motion.button
                          key={idx}
                          whileHover={{ scale: 1.01 }}
                          onClick={() => {
                            if (result.type === 'Page' && result.tab) {
                              setActiveTab(result.tab);
                            }
                            setSearchOpen(false);
                          }}
                          className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors text-left"
                        >
                          {result.icon ? (
                            <result.icon size={18} className="text-gray-400" />
                          ) : (
                            <User size={18} className="text-gray-400" />
                          )}
                          <div className="flex-1">
                            <p className="font-medium text-gray-800">{result.name}</p>
                            <p className="text-xs text-gray-500">{result.type}</p>
                          </div>
                          {result.score && (
                            <span className="text-sm font-semibold text-green-600">{result.score}</span>
                          )}
                        </motion.button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Notifications Panel */}
        <AnimatePresence>
          {notificationsOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-40"
                onClick={() => setNotificationsOpen(false)}
              />
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="fixed top-20 right-4 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden"
              >
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800">Notifications</h3>
                  <button
                    onClick={() => setNotificationsOpen(false)}
                    className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X size={18} className="text-gray-400" />
                  </button>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.map((notif) => (
                    <motion.div
                      key={notif.id}
                      whileHover={{ backgroundColor: 'rgba(249, 250, 251, 1)' }}
                      className={`p-4 border-b border-gray-100 cursor-pointer ${
                        notif.unread ? 'bg-blue-50/30' : ''
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          notif.unread ? 'bg-blue-500' : 'bg-gray-300'
                        }`} />
                        <div className="flex-1">
                          <p className="font-medium text-gray-800 text-sm">{notif.title}</p>
                          <p className="text-xs text-gray-500 mt-1">{notif.message}</p>
                          <p className="text-xs text-gray-400 mt-2">{notif.time}</p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="p-3 border-t border-gray-200">
                  <button className="w-full text-center text-sm text-blue-600 hover:text-blue-700 font-medium">
                    View All Notifications
                  </button>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* User Menu Dropdown */}
        <AnimatePresence>
          {userMenuOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-40"
                onClick={() => setUserMenuOpen(false)}
              />
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="fixed top-20 right-4 w-72 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 overflow-hidden"
              >
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-semibold">
                      RA
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">Recruiter Admin</p>
                      <p className="text-xs text-gray-500">admin@velos.ai</p>
                    </div>
                  </div>
                </div>
                <div className="p-2">
                  <button className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors text-left">
                    <User size={18} className="text-gray-600" />
                    <span className="text-gray-800">My Profile</span>
                  </button>
                  <button
                    onClick={() => {
                      setActiveTab('settings');
                      setUserMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors text-left"
                  >
                    <Settings size={18} className="text-gray-600" />
                    <span className="text-gray-800">Settings</span>
                  </button>
                  <button className="w-full flex items-center gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors text-left">
                    <Bell size={18} className="text-gray-600" />
                    <span className="text-gray-800">Notifications</span>
                  </button>
                  <div className="my-2 border-t border-gray-200" />
                  <button className="w-full flex items-center gap-3 p-3 hover:bg-red-50 rounded-xl transition-colors text-left text-red-600">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                      <polyline points="16 17 21 12 16 7"/>
                      <line x1="21" y1="12" x2="9" y2="12"/>
                    </svg>
                    <span>Log Out</span>
                  </button>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

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
