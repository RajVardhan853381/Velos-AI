import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Key, Shield, Save, Check, Sparkles } from 'lucide-react';
import { API_BASE } from '../config.js';

const Settings = () => {
  const [strictnessLevel, setStrictnessLevel] = useState('moderate');
  const [groqConfigured, setGroqConfigured] = useState(false);
  const [groqMasked, setGroqMasked] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load current settings from backend on mount
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/settings`);
        if (res.ok) {
          const data = await res.json();
          const s = data.settings || {};
          if (s.strictness_level) setStrictnessLevel(s.strictness_level);
        }
      } catch {
        // Settings endpoint unreachable — continue with defaults
      }

      // Check if GROQ key is configured by pinging health or a dedicated check
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (res.ok) {
          const data = await res.json();
          const hasKey = !!(data.groq_configured ?? data.groq_key_set ?? false);
          setGroqConfigured(hasKey);
          if (hasKey) setGroqMasked('gsk_••••••••••••••••••••••••');
        }
      } catch {
        // Can't determine key status
      }

      setLoading(false);
    };

    fetchSettings();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    setSaveSuccess(false);
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strictness_level: strictnessLevel }),
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
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
              onClick={() => setStrictnessLevel(level)}
              className={`
                relative p-5 rounded-2xl text-left transition-all border-2
                ${strictnessLevel === level
                  ? 'border-blue-400 bg-gradient-to-br from-blue-50 to-indigo-50 shadow-soft-lg'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-soft'
                }
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color} shadow-soft`}></div>
                {strictnessLevel === level && (
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

      {/* API Key Status */}
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
            <h3 className="text-lg font-bold text-gray-800">API Key Status</h3>
            <p className="text-sm text-gray-500">Keys are configured via server environment variables</p>
          </div>
        </div>

        <div className="space-y-4">
          {/* GROQ API Key */}
          <div className="p-4 bg-gradient-to-br from-blue-50/50 to-indigo-50/30 rounded-2xl border border-blue-100/50">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-blue-500" />
              <span className="text-sm font-semibold text-gray-700">GROQ API Key</span>
            </div>
            {loading ? (
              <div className="h-10 bg-gray-100 rounded-xl animate-pulse" />
            ) : groqConfigured ? (
              <div className="flex items-center gap-3">
                <div className="flex-1 px-4 py-3 bg-white/90 border border-blue-200/50 rounded-xl font-mono text-sm text-gray-500 select-none">
                  {groqMasked}
                </div>
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-green-100 text-green-700 text-xs font-semibold rounded-lg border border-green-200">
                  <Check size={12} />
                  Configured via .env
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="flex-1 px-4 py-3 bg-white/90 border border-red-200/50 rounded-xl text-sm text-gray-400 italic">
                  Not configured
                </div>
                <span className="px-3 py-1.5 bg-red-100 text-red-700 text-xs font-semibold rounded-lg border border-red-200">
                  Missing
                </span>
              </div>
            )}
            <p className="mt-2 text-xs text-gray-400">Set <code className="bg-gray-100 px-1 rounded">GROQ_API_KEY</code> in your <code className="bg-gray-100 px-1 rounded">.env</code> file to enable AI features.</p>
          </div>

          {/* ZYND Protocol Key */}
          <div className="p-4 bg-gradient-to-br from-purple-50/50 to-pink-50/30 rounded-2xl border border-purple-100/50">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles size={16} className="text-purple-500" />
              <span className="text-sm font-semibold text-gray-700">ZYND Protocol Key</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1 px-4 py-3 bg-white/90 border border-purple-200/50 rounded-xl text-sm text-gray-400 italic">
                Internal protocol — no user key required
              </div>
              <span className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-100 text-purple-700 text-xs font-semibold rounded-lg border border-purple-200">
                <Check size={12} />
                Built-in
              </span>
            </div>
            <p className="mt-2 text-xs text-gray-400">The ZYND Protocol is embedded in the verification pipeline — no external key needed.</p>
          </div>
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex flex-col items-center gap-3 pb-8"
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
        {saveSuccess && (
          <p className="text-green-600 font-medium text-sm">Settings saved successfully.</p>
        )}
        {saveError && (
          <p className="text-red-600 font-medium text-sm">Error: {saveError}</p>
        )}
      </motion.div>
    </div>
  );
};

export default Settings;
