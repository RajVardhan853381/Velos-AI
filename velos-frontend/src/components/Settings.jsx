import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Key, Shield, Save, Copy, Check, Eye, EyeOff, Sparkles } from 'lucide-react';

const Settings = () => {
  const [config, setConfig] = useState({
    strictnessLevel: 'moderate',
    apiKeyManagement: {
      groq: '••••••••••••••••',
      zynd: '••••••••••••••••',
    }
  });

  const [showGroqKey, setShowGroqKey] = useState(false);
  const [showZyndKey, setShowZyndKey] = useState(false);
  const [copied, setCopied] = useState('');
  const [saving, setSaving] = useState(false);

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopied(key);
    setTimeout(() => setCopied(''), 2000);
  };

  const handleSave = async () => {
    setSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setSaving(false);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden bg-white rounded-3xl p-8 border border-gray-200/50 shadow-soft"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100/40 to-indigo-100/40 rounded-full blur-3xl -z-10"></div>
        <div className="flex items-center gap-4 relative z-10">
          <motion.div
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.5 }}
            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg"
          >
            <SettingsIcon className="text-white" size={32} />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Settings & Configuration</h1>
            <p className="text-gray-500 mt-1">Customize your verification system</p>
          </div>
        </div>
      </motion.div>

      {/* Strictness Level */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center shadow-soft">
            <Shield className="text-white" size={20} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-800">Verification Strictness</h3>
            <p className="text-sm text-gray-500">Configure AI verification sensitivity</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { level: 'lenient', label: 'Lenient', desc: 'Fast processing, more candidates pass', color: 'from-green-400 to-emerald-500' },
            { level: 'moderate', label: 'Moderate', desc: 'Balanced verification approach', color: 'from-blue-400 to-indigo-500' },
            { level: 'strict', label: 'Strict', desc: 'Rigorous checks, highest accuracy', color: 'from-purple-400 to-pink-500' }
          ].map(({ level, label, desc, color }) => (
            <motion.button
              key={level}
              whileHover={{ scale: 1.03, y: -4 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setConfig({ ...config, strictnessLevel: level })}
              className={`
                relative p-5 rounded-2xl text-left transition-all border-2
                ${config.strictnessLevel === level
                  ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-soft-lg'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-soft'
                }
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color} shadow-soft`}></div>
                {config.strictnessLevel === level && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center"
                  >
                    <Check className="text-white" size={14} />
                  </motion.div>
                )}
              </div>
              <div className="font-semibold text-gray-800 mb-1">{label}</div>
              <div className="text-xs text-gray-500">{desc}</div>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* API Key Management */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-2xl p-6 border border-gray-200/50 shadow-soft"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-soft">
            <Key className="text-white" size={20} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-800">API Key Management</h3>
            <p className="text-sm text-gray-500">Secure your integration keys</p>
          </div>
        </div>

        <div className="space-y-4">
          {/* GROQ API Key */}
          <div className="p-4 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 rounded-2xl border border-blue-100/50">
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Sparkles size={16} className="text-blue-500" />
              GROQ API Key
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showGroqKey ? 'text' : 'password'}
                  value={showGroqKey ? 'gsk_1234567890abcdefghijklmnop' : config.apiKeyManagement.groq}
                  readOnly
                  className="w-full px-4 py-3 bg-white/90 border border-blue-200/50 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
                />
                <button
                  onClick={() => setShowGroqKey(!showGroqKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showGroqKey ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => copyToClipboard('gsk_1234567890abcdefghijklmnop', 'groq')}
                className="px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white rounded-xl transition-all flex items-center gap-2 shadow-soft"
              >
                {copied === 'groq' ? <Check size={18} /> : <Copy size={18} />}
              </motion.button>
            </div>
          </div>

          {/* ZYND API Key */}
          <div className="p-4 bg-gradient-to-br from-purple-50/50 to-pink-50/30 rounded-2xl border border-purple-100/50">
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Sparkles size={16} className="text-purple-500" />
              ZYND Protocol Key
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <input
                  type={showZyndKey ? 'text' : 'password'}
                  value={showZyndKey ? 'zynd_9876543210zyxwvutsrqponmlk' : config.apiKeyManagement.zynd}
                  readOnly
                  className="w-full px-4 py-3 bg-white/90 border border-purple-200/50 rounded-xl font-mono text-sm focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all"
                />
                <button
                  onClick={() => setShowZyndKey(!showZyndKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  {showZyndKey ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => copyToClipboard('zynd_9876543210zyxwvutsrqponmlk', 'zynd')}
                className="px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-xl transition-all flex items-center gap-2 shadow-soft"
              >
                {copied === 'zynd' ? <Check size={18} /> : <Copy size={18} />}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex justify-center pb-8"
      >
        <motion.button
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleSave}
          disabled={saving}
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white rounded-2xl font-semibold shadow-soft-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 transition-all"
        >
          {saving ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Saving Changes...
            </>
          ) : (
            <>
              <Save size={20} />
              Save Configuration
            </>
          )}
        </motion.button>
      </motion.div>
    </div>
  );
};

export default Settings;
