import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, ShieldAlert, ShieldCheck, Camera, CameraOff,
  Eye, AlertTriangle, CheckCircle2, XCircle,
  Wifi, WifiOff, RefreshCw, User, Users, MonitorX,
  Bell, ChevronRight, Clock
} from 'lucide-react';
import { API_BASE } from '../config.js';

const API = API_BASE;
const WS = API_BASE
  ? API_BASE.replace(/^http/, 'ws')
  : `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}`;

const glass = {
  background: 'rgba(255,255,255,0.35)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.6)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
};

const SEVERITY_STYLES = {
  critical: { bg: 'bg-red-100 border-red-300', text: 'text-red-700', icon: ShieldAlert, dot: 'bg-red-500' },
  high: { bg: 'bg-orange-100 border-orange-300', text: 'text-orange-700', icon: AlertTriangle, dot: 'bg-orange-500' },
  medium: { bg: 'bg-amber-100 border-amber-300', text: 'text-amber-700', icon: Eye, dot: 'bg-amber-500' },
  low: { bg: 'bg-blue-100 border-blue-300', text: 'text-blue-700', icon: Bell, dot: 'bg-blue-500' },
};

const AlertCard = ({ alert, index }) => {
  const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.medium;
  const Icon = style.icon;
  return (
    <motion.div
      initial={{ opacity: 0, x: 20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ delay: index * 0.05 }}
      className={`flex items-start gap-3 p-3 rounded-xl border ${style.bg}`}
    >
      <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 ${style.dot} mt-0.5`}>
        <Icon size={13} className="text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold ${style.text}`}>{alert.message}</p>
        <p className="text-xs text-gray-400 mt-0.5">
          {new Date(alert.timestamp).toLocaleTimeString()}
        </p>
      </div>
      <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded-full ${style.text} bg-white/60`}>
        {alert.severity}
      </span>
    </motion.div>
  );
};

export default function AntiCheat() {
  const [step, setStep] = useState('setup'); // setup | proctoring | summary
  const [candidateName, setCandidateName] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [wsStatus, setWsStatus] = useState('disconnected'); // disconnected | connecting | connected | error
  const [alerts, setAlerts] = useState([]);
  const [frames, setFrames] = useState(0);
  const [tabSwitches, setTabSwitches] = useState(0);
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [facesStatus, setFacesStatus] = useState('unknown'); // unknown | ok | no_face | multiple

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const timerRef = useRef(null);

  // Detect tab visibility or focus changes
  useEffect(() => {
    let timeoutId;
    const triggerAlert = () => {
      if (step !== 'proctoring') return;

      // Debounce to prevent double-counting if both blur and visibilitychange fire
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        setTabSwitches(prev => prev + 1);
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'tab_switch' }));
        }
      }, 500);
    };

    const handleVisibility = () => {
      if (document.hidden || document.visibilityState === 'hidden') triggerAlert();
    };

    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('blur', triggerAlert);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('blur', triggerAlert);
    };
  }, [step]);

  // Elapsed timer
  useEffect(() => {
    if (step === 'proctoring') {
      timerRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [step]);

  const startCamera = async () => {
    // mediaDevices is only available on HTTPS or localhost
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError(
        'Camera access requires a secure context (HTTPS or localhost). ' +
        'Open the app via http://localhost:5173 or serve over HTTPS. ' +
        'Tab-switch detection will still work.'
      );
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraOn(true);
      setCameraError('');
    } catch (err) {
      const msg = err.name === 'NotAllowedError'
        ? 'Camera permission denied. Please allow camera access in your browser settings.'
        : err.name === 'NotFoundError'
          ? 'No camera found. Connect a camera and try again.'
          : `Camera error: ${err.message}`;
      setCameraError(`${msg} Tab-switch detection will still work.`);
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach(t => t.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCameraOn(false);
  };

  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = 320;
    canvas.height = 240;
    ctx.drawImage(videoRef.current, 0, 0, 320, 240);
    const b64 = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
    wsRef.current.send(JSON.stringify({ type: 'frame', data: b64 }));
    setFrames(prev => prev + 1);
  }, []);

  const startProctoring = async () => {
    setLoading(true);
    try {
      // Create session on backend
      const res = await fetch(`${API}/api/proctor/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_name: candidateName || 'Candidate', assessment_id: '' }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to create session');

      const sid = data.session_id;
      setSessionId(sid);
      setAlerts([]);
      setFrames(0);
      setTabSwitches(0);
      setElapsed(0);

      // Connect WebSocket
      setWsStatus('connecting');
      const ws = new WebSocket(`${WS}/ws/proctor/${sid}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsStatus('connected');
        // Start sending frames every 2s if camera is on
        if (cameraOn) {
          intervalRef.current = setInterval(captureFrame, 2000);
        }
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'alert') {
            setAlerts(prev => [msg, ...prev].slice(0, 50));
            if (msg.category === 'multiple_faces') setFacesStatus('multiple');
            else if (msg.category === 'no_face') setFacesStatus('no_face');
          } else if (msg.type === 'status') {
            if (msg.faces === 1) setFacesStatus('ok');
          }
        } catch (parseErr) {
          console.warn('WebSocket message parse error:', parseErr);
        }
      };

      ws.onerror = () => setWsStatus('error');
      ws.onclose = () => setWsStatus('disconnected');

      setStep('proctoring');
    } catch (err) {
      setAlerts([{ type: 'alert', severity: 'high', message: err.message, timestamp: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  const stopProctoring = () => {
    clearInterval(intervalRef.current);
    wsRef.current?.close();
    stopCamera();
    setStep('summary');
  };

  const reset = () => {
    stopCamera();
    clearInterval(intervalRef.current);
    wsRef.current?.close();
    setStep('setup');
    setSessionId(null);
    setAlerts([]);
    setFrames(0);
    setTabSwitches(0);
    setElapsed(0);
    setFacesStatus('unknown');
    setWsStatus('disconnected');
  };

  const formatTime = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  const criticalAlerts = alerts.filter(a => a.severity === 'critical');
  const highAlerts = alerts.filter(a => a.severity === 'high');

  // ── SETUP ──────────────────────────────────────────────────────────
  if (step === 'setup') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 flex items-center justify-center shadow-lg shadow-rose-500/30">
              <Shield className="text-white" size={20} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900">Anti-Cheat Proctoring</h2>
              <p className="text-sm text-gray-500">Real-time CV face detection + tab-switch monitoring</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="rounded-2xl p-6 space-y-4" style={glass}>
          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Candidate Name (optional)</label>
            <input
              value={candidateName}
              onChange={e => setCandidateName(e.target.value)}
              placeholder="e.g. Jordan Smith"
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-rose-300"
            />
          </div>

          {/* Camera preview */}
          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Camera Preview</label>
            <div className="relative rounded-xl overflow-hidden bg-gray-100 aspect-video flex items-center justify-center">
              <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
              <canvas ref={canvasRef} className="hidden" />
              {!cameraOn && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-white">
                  <CameraOff size={36} className="opacity-40" />
                  <p className="text-sm opacity-60">Camera not started</p>
                </div>
              )}
            </div>
            {cameraError && (
              <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                <AlertTriangle size={12} /> {cameraError}
              </p>
            )}
            <button
              onClick={cameraOn ? stopCamera : startCamera}
              className={`mt-2 flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${cameraOn
                  ? 'bg-red-100 text-red-700 border border-red-200 hover:bg-red-200'
                  : 'bg-white/60 text-gray-700 border border-white/80 hover:bg-white/80'
                }`}
            >
              {cameraOn ? <><CameraOff size={15} /> Stop Camera</> : <><Camera size={15} /> Start Camera</>}
            </button>
          </div>

          <motion.button
            onClick={startProctoring}
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-3.5 rounded-xl font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50"
            style={{ background: 'linear-gradient(135deg, #f43f5e, #ec4899)', boxShadow: '0 4px 20px rgba(244,63,94,0.4)' }}
          >
            {loading
              ? <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}><RefreshCw size={18} /></motion.div> Starting...</>
              : <><Shield size={18} /> Begin Proctoring Session <ChevronRight size={18} /></>
            }
          </motion.button>
        </motion.div>

        {/* Info */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { icon: Eye, label: 'Face Detection', desc: 'OpenCV Haar cascade' },
            { icon: Users, label: 'Multi-Face Alert', desc: 'Detects extra persons' },
            { icon: MonitorX, label: 'Tab Switch', desc: 'Browser visibility API' },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="rounded-xl p-4 text-center" style={glass}>
              <Icon className="mx-auto mb-2 text-rose-500" size={18} />
              <p className="text-xs font-bold text-gray-800">{label}</p>
              <p className="text-xs text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── PROCTORING ────────────────────────────────────────────────────
  if (step === 'proctoring') {
    const faceStatusConfig = {
      ok: { icon: ShieldCheck, color: 'text-green-600', bg: 'bg-green-100', label: 'Face Verified' },
      no_face: { icon: CameraOff, color: 'text-amber-600', bg: 'bg-amber-100', label: 'Not in Frame' },
      multiple: { icon: Users, color: 'text-red-600', bg: 'bg-red-100', label: 'Multiple Faces!' },
      unknown: { icon: Eye, color: 'text-gray-500', bg: 'bg-gray-100', label: 'Monitoring...' },
    };
    const fsc = faceStatusConfig[facesStatus];

    return (
      <div className="max-w-5xl mx-auto space-y-4">
        {/* Status Bar */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between rounded-2xl px-5 py-3" style={glass}>
          <div className="flex items-center gap-3">
            <motion.div animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 1.5, repeat: Infinity }}
              className="w-3 h-3 rounded-full bg-red-500 shadow-lg shadow-red-500/60" />
            <span className="font-bold text-gray-800">LIVE PROCTORING</span>
            <span className="text-sm text-gray-500">{candidateName || 'Candidate'}</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-1 text-gray-600"><Clock size={14} /> {formatTime(elapsed)}</span>
            <span className={`flex items-center gap-1 ${wsStatus === 'connected' ? 'text-green-600' : 'text-red-500'}`}>
              {wsStatus === 'connected' ? <Wifi size={14} /> : <WifiOff size={14} />}
              {wsStatus}
            </span>
            <button
              onClick={stopProctoring}
              className="px-4 py-1.5 rounded-xl bg-red-100 text-red-700 text-xs font-bold border border-red-200 hover:bg-red-200"
            >
              End Session
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Camera Feed */}
          <div className="lg:col-span-2 space-y-3">
            <div className="rounded-2xl overflow-hidden bg-gray-100 relative aspect-video" style={glass}>
              <video ref={videoRef} className="w-full h-full object-cover" muted playsInline />
              <canvas ref={canvasRef} className="hidden" />
              {!cameraOn && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white">
                  <CameraOff size={40} className="opacity-30" />
                  <p className="text-sm opacity-50">Camera off — tab monitoring active</p>
                </div>
              )}

              {/* Overlay */}
              <div className="absolute top-3 left-3 flex items-center gap-2">
                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold ${fsc.bg} ${fsc.color} backdrop-blur-sm`}>
                  <fsc.icon size={13} />
                  {fsc.label}
                </div>
              </div>

              {criticalAlerts.length > 0 && (
                <motion.div
                  animate={{ opacity: [0.7, 1, 0.7] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="absolute inset-0 border-4 border-red-500 rounded-2xl pointer-events-none"
                />
              )}
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Total Alerts', value: alerts.length, icon: Bell, color: 'text-amber-600' },
                { label: 'Tab Switches', value: tabSwitches, icon: MonitorX, color: tabSwitches > 0 ? 'text-red-600' : 'text-gray-600' },
                { label: 'Frames Sent', value: frames, icon: Camera, color: 'text-blue-600' },
              ].map(({ label, value, icon: Icon, color }) => (
                <div key={label} className="rounded-xl p-4 text-center" style={glass}>
                  <Icon className={`mx-auto mb-1 ${color}`} size={18} />
                  <p className="text-2xl font-black text-gray-900">{value}</p>
                  <p className="text-xs text-gray-500">{label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Live Alerts Feed */}
          <div className="rounded-2xl p-4 h-full" style={glass}>
            <h4 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
              <ShieldAlert size={15} className="text-rose-500" />
              Live Alerts Feed
              {alerts.length > 0 && (
                <span className="ml-auto text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-bold">{alerts.length}</span>
              )}
            </h4>
            <div className="space-y-2 max-h-[460px] overflow-y-auto scrollbar-hide">
              <AnimatePresence>
                {alerts.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    <ShieldCheck size={32} className="mx-auto mb-2 opacity-40" />
                    <p className="text-sm">No alerts yet</p>
                    <p className="text-xs">All clear</p>
                  </div>
                ) : alerts.map((alert, i) => (
                  <AlertCard key={`${alert.timestamp}-${i}`} alert={alert} index={i} />
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── SUMMARY ───────────────────────────────────────────────────────
  if (step === 'summary') {
    const risk = criticalAlerts.length > 0 ? 'HIGH' : highAlerts.length > 2 || tabSwitches > 2 ? 'MEDIUM' : 'LOW';
    const riskColor = risk === 'HIGH' ? 'text-red-600' : risk === 'MEDIUM' ? 'text-amber-600' : 'text-green-600';
    const riskBg = risk === 'HIGH' ? 'from-red-50 to-rose-50 border-red-200' : risk === 'MEDIUM' ? 'from-amber-50 to-yellow-50 border-amber-200' : 'from-green-50 to-emerald-50 border-green-200';

    return (
      <div className="max-w-2xl mx-auto space-y-5">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className={`rounded-2xl p-6 bg-gradient-to-br border ${riskBg}`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-black text-gray-900">Session Complete</h3>
              <p className="text-sm text-gray-500">{candidateName || 'Candidate'} · {formatTime(elapsed)}</p>
            </div>
            <div className={`text-center px-6 py-4 rounded-xl bg-white/60 border border-white/80`}>
              <p className="text-xs font-bold text-gray-500 mb-1">Risk Level</p>
              <p className={`text-3xl font-black ${riskColor}`}>{risk}</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Total Alerts', value: alerts.length },
              { label: 'Tab Switches', value: tabSwitches },
              { label: 'Critical Flags', value: criticalAlerts.length },
            ].map(({ label, value }) => (
              <div key={label} className="p-3 rounded-xl bg-white/50 text-center">
                <p className="text-xl font-black text-gray-900">{value}</p>
                <p className="text-xs text-gray-500">{label}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {alerts.length > 0 && (
          <div className="rounded-2xl p-5" style={glass}>
            <h4 className="text-sm font-bold text-gray-700 mb-3">Alert Log</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto scrollbar-hide">
              {alerts.map((alert, i) => <AlertCard key={i} alert={alert} index={i} />)}
            </div>
          </div>
        )}

        <div className="flex justify-center">
          <button onClick={reset} className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/60 border border-white/80 text-gray-700 font-semibold hover:bg-white/80 transition-all text-sm">
            <RefreshCw size={15} /> New Session
          </button>
        </div>
      </div>
    );
  }

  return null;
}
