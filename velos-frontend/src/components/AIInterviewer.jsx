import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare, Send, User, Bot, Sparkles, Target,
  TrendingUp, RefreshCw, ChevronRight, CheckCircle2,
  Brain, AlertTriangle, Mic, MicOff, Video, VideoOff,
  Volume2, VolumeX, Phone, PhoneOff
} from 'lucide-react';
import { API_BASE } from '../config.js';
import * as THREE from 'three';

// ── Constants ─────────────────────────────────────────────────────────────────

const glass = {
  background: 'rgba(255,255,255,0.35)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.6)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
};

const glassDark = {
  background: 'rgba(241,245,255,0.55)',
  backdropFilter: 'blur(24px)',
  border: '1px solid rgba(200,210,255,0.5)',
  boxShadow: '0 8px 40px rgba(80,100,200,0.12)',
};

// ── Small reusable components ─────────────────────────────────────────────────

const ScoreBadge = React.memo(({ label, score }) => {
  const color =
    score >= 8 ? 'bg-green-100 text-green-700 border-green-200' :
    score >= 5 ? 'bg-blue-100 text-blue-700 border-blue-200' :
    'bg-amber-100 text-amber-700 border-amber-200';
  return (
    <div className={`flex flex-col items-center px-3 py-2 rounded-xl border text-xs font-semibold ${color}`}>
      <span className="text-lg font-black">{score}/10</span>
      <span>{label}</span>
    </div>
  );
});

const ProgressBar = React.memo(({ value, max, color }) => (
  <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
    <motion.div
      initial={{ width: 0 }}
      animate={{ width: `${(value / max) * 100}%` }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`h-2 rounded-full ${color}`}
    />
  </div>
));

// ── 3D Avatar components ───────────────────────────────────────────────────────

/**
 * AvatarHead — the main 3D avatar mesh rendered inside a <Canvas>.
 * isSpeaking: boolean — drives jaw animation and emissive pulse.
 */
function AvatarHead({ isSpeaking }) {
  const headRef = useRef();
  const jawRef = useRef();
  const leftEyeRef = useRef();
  const rightEyeRef = useRef();
  const glowRingRef = useRef();
  const clock = useRef(0);
  const blinkTimer = useRef(0);
  const jawPhase = useRef(0);

  // Stable material ref — never re-created on prop change (avoids GPU leak)
  const headMatRef = useRef(new THREE.MeshPhysicalMaterial({
    color: new THREE.Color('#dbeafe'),
    emissive: new THREE.Color('#3b82f6'),
    emissiveIntensity: 0.12,
    metalness: 0.1,
    roughness: 0.2,
    transmission: 0.05,
    transparent: true,
    opacity: 0.97,
  }));

  // Dispose material on unmount
  useEffect(() => {
    const mat = headMatRef.current;
    return () => mat?.dispose();
  }, []);

  useFrame((_, delta) => {
    clock.current += delta;
    blinkTimer.current += delta;
    if (isSpeaking) jawPhase.current += delta;

    // Smooth emissive pulse via lerp — no new object created
    if (headMatRef.current) {
      headMatRef.current.emissiveIntensity = THREE.MathUtils.lerp(
        headMatRef.current.emissiveIntensity,
        isSpeaking ? 0.35 : 0.12,
        0.08
      );
    }

    // Idle breathing on head
    if (headRef.current) {
      const breathe = Math.sin(clock.current * 1.2) * 0.008;
      headRef.current.scale.setScalar(1 + breathe);

      // Subtle idle head sway
      headRef.current.rotation.y = Math.sin(clock.current * 0.4) * 0.06;
      headRef.current.rotation.z = Math.sin(clock.current * 0.3) * 0.025;
    }

    // Jaw — bob when speaking
    if (jawRef.current) {
      const jawOpen = isSpeaking
        ? Math.abs(Math.sin(jawPhase.current * 6)) * 0.09
        : 0;
      jawRef.current.position.y = -0.32 - jawOpen * 0.5;
      jawRef.current.scale.y = 1 - jawOpen * 0.6;
    }

    // Eye blink every ~3–4 seconds
    if (leftEyeRef.current && rightEyeRef.current) {
      const blinkOpen = blinkTimer.current % 3.5 < 0.12 ? 0.15 : 1;
      leftEyeRef.current.scale.y = THREE.MathUtils.lerp(leftEyeRef.current.scale.y, blinkOpen, 0.25);
      rightEyeRef.current.scale.y = THREE.MathUtils.lerp(rightEyeRef.current.scale.y, blinkOpen, 0.25);
    }

    // Glow ring pulse
    if (glowRingRef.current) {
      const pulse = isSpeaking
        ? 1 + Math.abs(Math.sin(clock.current * 5)) * 0.15
        : 1 + Math.sin(clock.current * 1.5) * 0.03;
      glowRingRef.current.scale.setScalar(pulse);
      glowRingRef.current.material.opacity = isSpeaking
        ? 0.5 + Math.abs(Math.sin(clock.current * 5)) * 0.35
        : 0.18;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Outer glow ring */}
      <mesh ref={glowRingRef} position={[0, 0, -0.2]}>
        <torusGeometry args={[0.75, 0.04, 16, 60]} />
        <meshBasicMaterial color="#6366f1" transparent opacity={0.2} />
      </mesh>

      {/* Neck */}
      <mesh position={[0, -0.65, 0]}>
        <cylinderGeometry args={[0.18, 0.22, 0.35, 24]} />
        <meshPhysicalMaterial color="#bfdbfe" metalness={0.05} roughness={0.4} />
      </mesh>

      {/* Shoulders / body bust */}
      <mesh position={[0, -1.0, 0]}>
        <cylinderGeometry args={[0.7, 0.55, 0.55, 32]} />
        <meshPhysicalMaterial color="#e0e7ff" metalness={0.08} roughness={0.35} />
      </mesh>

      {/* Head */}
      <group ref={headRef}>
        <mesh>
          <sphereGeometry args={[0.48, 64, 64]} />
          <primitive object={headMatRef.current} attach="material" />
        </mesh>

        {/* Forehead ridge */}
        <mesh position={[0, 0.28, 0.35]}>
          <sphereGeometry args={[0.12, 32, 32]} />
          <meshPhysicalMaterial color="#bfdbfe" metalness={0.1} roughness={0.3} transparent opacity={0.7} />
        </mesh>

        {/* Left eye */}
        <group position={[-0.16, 0.12, 0.42]}>
          <mesh ref={leftEyeRef}>
            <sphereGeometry args={[0.07, 32, 32]} />
            <meshBasicMaterial color="#1d4ed8" />
          </mesh>
          {/* Pupil glow */}
          <mesh position={[0, 0, 0.04]}>
            <sphereGeometry args={[0.035, 16, 16]} />
            <meshBasicMaterial color="#ffffff" />
          </mesh>
          {/* Emissive iris */}
          <pointLight color="#60a5fa" intensity={isSpeaking ? 0.5 : 0.15} distance={0.4} />
        </group>

        {/* Right eye */}
        <group position={[0.16, 0.12, 0.42]}>
          <mesh ref={rightEyeRef}>
            <sphereGeometry args={[0.07, 32, 32]} />
            <meshBasicMaterial color="#1d4ed8" />
          </mesh>
          <mesh position={[0, 0, 0.04]}>
            <sphereGeometry args={[0.035, 16, 16]} />
            <meshBasicMaterial color="#ffffff" />
          </mesh>
          <pointLight color="#60a5fa" intensity={isSpeaking ? 0.5 : 0.15} distance={0.4} />
        </group>

        {/* Nose */}
        <mesh position={[0, -0.04, 0.46]}>
          <sphereGeometry args={[0.04, 16, 16]} />
          <meshPhysicalMaterial color="#bfdbfe" roughness={0.5} />
        </mesh>

        {/* Jaw / lower face */}
        <mesh ref={jawRef} position={[0, -0.32, 0]}>
          <sphereGeometry args={[0.38, 64, 32, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2]} />
          <primitive object={headMatRef.current} attach="material" />
        </mesh>

        {/* Mouth line */}
        <mesh position={[0, -0.18, 0.44]} rotation={[0, 0, 0]}>
          <torusGeometry args={[0.1, 0.012, 8, 20, Math.PI]} />
          <meshBasicMaterial color="#93c5fd" />
        </mesh>
      </group>

      {/* Ambient rim light from top */}
      <pointLight position={[0, 2.5, 1]} color="#e0e7ff" intensity={1.2} />
      <pointLight position={[-1.5, 0.5, 1]} color="#bfdbfe" intensity={0.6} />
      <pointLight position={[1.5, 0.5, 1]} color="#ddd6fe" intensity={0.6} />
    </group>
  );
}

/**
 * AvatarScene — the full Canvas with camera, lighting, avatar.
 */
const AvatarScene = React.memo(({ isSpeaking }) => {
  return (
    <Canvas
      camera={{ position: [0, 0.1, 2.2], fov: 42 }}
      gl={{ antialias: true, alpha: true }}
      style={{ width: '100%', height: '100%' }}
    >
      <ambientLight intensity={0.7} color="#e0e7ff" />
      <directionalLight position={[2, 3, 2]} intensity={0.9} color="#ffffff" />
      <AvatarHead isSpeaking={isSpeaking} />
    </Canvas>
  );
});

// ── Speech utilities ───────────────────────────────────────────────────────────

const SPEECH_SYNTHESIS_AVAILABLE = typeof window !== 'undefined' && 'speechSynthesis' in window;
const SPEECH_RECOGNITION_AVAILABLE =
  typeof window !== 'undefined' &&
  ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

function getPreferredVoice() {
  if (!SPEECH_SYNTHESIS_AVAILABLE) return null;
  const voices = window.speechSynthesis.getVoices();
  return (
    voices.find(v => v.name.includes('Google') && v.lang === 'en-US') ||
    voices.find(v => v.lang === 'en-US' && !v.localService) ||
    voices.find(v => v.lang.startsWith('en')) ||
    null
  );
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function AIInterviewer() {
  const [step, setStep] = useState('setup'); // setup | interview | completed
  const [form, setForm] = useState({
    candidateName: '',
    jobRole: '',
    jobDescription: '',
    resumeSummary: '',
  });
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [lastEval, setLastEval] = useState(null);
  const [finalResult, setFinalResult] = useState(null);
  const [error, setError] = useState('');

  // Video call state
  const [isSpeaking, setIsSpeaking] = useState(false);      // AI avatar talking
  const [isMicOn, setIsMicOn] = useState(false);             // candidate mic active
  const [isCamOn, setIsCamOn] = useState(true);              // candidate camera
  const [isMuted, setIsMuted] = useState(false);             // TTS muted
  const [camDenied, setCamDenied] = useState(false);         // camera permission denied
  const [currentQuestion, setCurrentQuestion] = useState('');// current displayed question
  const [recognizing, setRecognizing] = useState(false);     // STT in progress
  const [interimText, setInterimText] = useState('');        // STT interim

  const chatEndRef = useRef(null);
  const textAreaRef = useRef(null);
  const videoRef = useRef(null);           // candidate webcam
  const camStreamRef = useRef(null);       // MediaStream for cleanup
  const recognitionRef = useRef(null);     // SpeechRecognition instance
  const utteranceRef = useRef(null);       // current SpeechSynthesisUtterance
  const isMutedRef = useRef(false);        // mirrors isMuted for stale-closure-free callbacks

  // ── Webcam ────────────────────────────────────────────────────────────────

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      camStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCamDenied(false);
    } catch {
      setCamDenied(true);
      setIsCamOn(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (camStreamRef.current) {
      camStreamRef.current.getTracks().forEach(t => t.stop());
      camStreamRef.current = null;
    }
    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);

  const toggleCamera = useCallback(() => {
    if (isCamOn) {
      stopCamera();
      setIsCamOn(false);
    } else {
      setIsCamOn(true);
      startCamera();
    }
  }, [isCamOn, startCamera, stopCamera]);

  // Start camera when entering interview
  useEffect(() => {
    if (step === 'interview' && isCamOn) {
      startCamera();
    }
    return () => {
      if (step !== 'interview') stopCamera();
    };
  }, [step]); // eslint-disable-line react-hooks/exhaustive-deps

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopCamera();
      if (SPEECH_SYNTHESIS_AVAILABLE) window.speechSynthesis.cancel();
      if (recognitionRef.current) recognitionRef.current.abort();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Keep muted ref in sync (avoids stale closures in speak callback)
  useEffect(() => { isMutedRef.current = isMuted; }, [isMuted]);

  // Chrome TTS keep-alive — prevents the ~15 s silence bug
  useEffect(() => {
    if (!SPEECH_SYNTHESIS_AVAILABLE) return;
    const id = setInterval(() => {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }
    }, 10000);
    return () => clearInterval(id);
  }, []);

  // ── TTS ───────────────────────────────────────────────────────────────────

  const speak = useCallback((text, onEnd) => {
    if (!SPEECH_SYNTHESIS_AVAILABLE || isMutedRef.current) {
      setIsSpeaking(false);
      onEnd?.();
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.92;
    utterance.pitch = 1.05;
    utterance.volume = 1;

    // Wait for voices to load (may be async on first load)
    const trySpeak = () => {
      if (isMutedRef.current) { onEnd?.(); return; } // re-check at actual speak time
      utterance.voice = getPreferredVoice();
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => {
        setIsSpeaking(false);
        onEnd?.();
      };
      utterance.onerror = () => {
        setIsSpeaking(false);
        onEnd?.();
      };
      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    };

    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = trySpeak;
    } else {
      trySpeak();
    }
  }, []); // no dependencies — reads mute state through isMutedRef

  const stopSpeaking = useCallback(() => {
    if (SPEECH_SYNTHESIS_AVAILABLE) window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, []);

  const toggleMute = useCallback(() => {
    if (!isMuted) stopSpeaking();
    setIsMuted(m => !m);
  }, [isMuted, stopSpeaking]);

  // ── STT ───────────────────────────────────────────────────────────────────

  const startRecognition = useCallback(() => {
    if (!SPEECH_RECOGNITION_AVAILABLE) return;
    stopSpeaking(); // stop AI speaking when candidate starts

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new SpeechRecognition();
    rec.lang = 'en-US';
    rec.continuous = true;
    rec.interimResults = true;

    rec.onresult = (e) => {
      let finalTranscript = '';
      let interimTranscript = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) finalTranscript += t;
        else interimTranscript += t;
      }
      if (finalTranscript) {
        setCurrentAnswer(prev => (prev ? prev + ' ' + finalTranscript : finalTranscript).trim());
        setInterimText('');
      } else {
        setInterimText(interimTranscript);
      }
    };

    rec.onend = () => {
      setRecognizing(false);
      setInterimText('');
    };

    rec.onerror = () => {
      setRecognizing(false);
      setInterimText('');
    };

    recognitionRef.current = rec;
    rec.start();
    setRecognizing(true);
    setIsMicOn(true);
  }, [stopSpeaking]);

  const stopRecognition = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setRecognizing(false);
    setIsMicOn(false);
    setInterimText('');
  }, []);

  const toggleMic = useCallback(() => {
    if (recognizing) stopRecognition();
    else startRecognition();
  }, [recognizing, startRecognition, stopRecognition]);

  // ── API calls ─────────────────────────────────────────────────────────────

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startInterview = useCallback(async () => {
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/interview/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_name: form.candidateName || 'Candidate',
          job_role: form.jobRole,
          job_description: form.jobDescription,
          resume_summary: form.resumeSummary,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to start interview');

      setSessionId(data.session_id);
      setMessages([{ role: 'interviewer', content: data.question, qNum: 1 }]);
      setCurrentQuestion(data.question);
      setQuestionNumber(1);
      setStep('interview');

      // Speak the first question after a short delay
      setTimeout(() => speak(data.question), 600);
    } catch (err) {
      const msg =
        err.message.includes('503') || err.message.toLowerCase().includes('groq')
          ? 'AI service unavailable — ensure the backend is running with a valid GROQ_API_KEY.'
          : err.message.includes('Failed to fetch') || err.message.includes('NetworkError')
          ? 'Cannot reach the backend. Start it with: uvicorn server:app --reload --port 8000'
          : err.message;
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [form, speak]);

  const submitAnswer = useCallback(async () => {
    if (!currentAnswer.trim() || loading) return;
    stopSpeaking();
    stopRecognition();
    setError('');

    const answer = currentAnswer.trim();
    setCurrentAnswer('');
    setInterimText('');
    setMessages(prev => [...prev, { role: 'candidate', content: answer }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/interview/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, answer }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to submit answer');

      setLastEval(data.evaluation);

      if (data.status === 'completed') {
        setFinalResult(data);
        const finalMsg = data.message || 'Thank you for completing the interview!';
        setMessages(prev => [...prev, {
          role: 'interviewer',
          content: finalMsg,
          isFinal: true,
        }]);
        setCurrentQuestion(finalMsg);
        speak(finalMsg, () => {
          setTimeout(() => setStep('completed'), 1200);
        });
      } else {
        setMessages(prev => [...prev, {
          role: 'interviewer',
          content: data.question,
          qNum: data.question_number,
        }]);
        setCurrentQuestion(data.question);
        setQuestionNumber(data.question_number);
        setProgress(data.progress || 0);
        speak(data.question);
      }
    } catch (err) {
      const msg =
        err.message.includes('503') || err.message.toLowerCase().includes('groq')
          ? 'AI service unavailable — ensure the backend is running with a valid GROQ_API_KEY.'
          : err.message.includes('Failed to fetch') || err.message.includes('NetworkError')
          ? 'Cannot reach the backend. Start it with: uvicorn server:app --reload --port 8000'
          : err.message;
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [currentAnswer, loading, sessionId, speak, stopSpeaking, stopRecognition]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      submitAnswer();
    }
  }, [submitAnswer]);

  const reset = useCallback(() => {
    stopSpeaking();
    stopRecognition();
    stopCamera();
    setStep('setup');
    setSessionId(null);
    setMessages([]);
    setCurrentAnswer('');
    setProgress(0);
    setQuestionNumber(1);
    setLastEval(null);
    setFinalResult(null);
    setError('');
    setIsSpeaking(false);
    setIsMicOn(false);
    setIsCamOn(true);
    setCurrentQuestion('');
    setInterimText('');
  }, [stopSpeaking, stopRecognition, stopCamera]);

  const canStart = useMemo(
    () => form.jobRole.trim().length >= 3 && form.jobDescription.trim().length >= 20,
    [form.jobRole, form.jobDescription]
  );

  // ── SETUP SCREEN ──────────────────────────────────────────────────────────

  if (step === 'setup') {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <MessageSquare className="text-white" size={20} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900">AI Video Interviewer</h2>
              <p className="text-sm text-gray-500">3D AI avatar · Voice questions · Live scoring</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="rounded-2xl p-6 space-y-4" style={glass}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-gray-600 mb-1.5 block">Candidate Name (optional)</label>
              <input
                value={form.candidateName}
                onChange={e => setForm(p => ({ ...p, candidateName: e.target.value }))}
                placeholder="e.g. Alex Johnson"
                className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-600 mb-1.5 block">Job Role *</label>
              <input
                value={form.jobRole}
                onChange={e => setForm(p => ({ ...p, jobRole: e.target.value }))}
                placeholder="e.g. Senior Backend Engineer"
                className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Job Description *</label>
            <textarea
              value={form.jobDescription}
              onChange={e => setForm(p => ({ ...p, jobDescription: e.target.value }))}
              rows={5}
              placeholder="Paste the job description..."
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Resume Summary (optional)</label>
            <textarea
              value={form.resumeSummary}
              onChange={e => setForm(p => ({ ...p, resumeSummary: e.target.value }))}
              rows={3}
              placeholder="Paste a brief summary of the candidate's background..."
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              <AlertTriangle size={15} /> {error}
            </div>
          )}

          <motion.button
            onClick={startInterview}
            disabled={!canStart || loading}
            whileHover={canStart ? { scale: 1.02 } : {}}
            whileTap={canStart ? { scale: 0.98 } : {}}
            className="w-full py-3.5 rounded-xl font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ background: 'linear-gradient(135deg, #3b82f6, #4f46e5)', boxShadow: '0 4px 20px rgba(59,130,246,0.4)' }}
          >
            {loading ? (
              <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}><RefreshCw size={18} /></motion.div> Starting...</>
            ) : (
              <><Video size={18} /> Begin Video Interview <ChevronRight size={18} /></>
            )}
          </motion.button>
        </motion.div>

        {/* Info cards */}
        <div className="grid grid-cols-4 gap-3">
          {[
            { icon: Brain, label: '6 Questions', desc: 'AI-generated' },
            { icon: TrendingUp, label: 'Live Scoring', desc: 'Clarity · Depth' },
            { icon: Target, label: '3D Avatar', desc: 'Talks to you' },
            { icon: Mic, label: 'Voice Input', desc: 'Speak your answers' },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="rounded-xl p-4 text-center" style={glass}>
              <Icon className="mx-auto mb-2 text-indigo-500" size={20} />
              <p className="text-xs font-bold text-gray-800">{label}</p>
              <p className="text-xs text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── INTERVIEW SCREEN (Video Call) ──────────────────────────────────────────

  if (step === 'interview') {
    return (
      <div className="max-w-5xl mx-auto space-y-4">

        {/* Top bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <Video className="text-white" size={17} />
            </div>
            <div>
              <h2 className="text-lg font-black text-gray-900">{form.jobRole} Interview</h2>
              <p className="text-xs text-gray-500">{form.candidateName || 'Candidate'} · Question {questionNumber} of 6</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {lastEval && (
              <div className="flex gap-2">
                <ScoreBadge label="Clarity" score={lastEval.clarity_score} />
                <ScoreBadge label="Depth" score={lastEval.depth_score} />
              </div>
            )}
            <motion.button
              onClick={reset}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold text-red-600 bg-red-50 border border-red-200 hover:bg-red-100 transition-colors"
            >
              <PhoneOff size={14} /> End
            </motion.button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="rounded-xl px-4 py-3" style={glass}>
          <div className="flex items-center justify-between text-xs text-gray-500 mb-1.5">
            <span>Interview Progress</span>
            <span>{progress}%</span>
          </div>
          <ProgressBar value={progress} max={100} color="bg-gradient-to-r from-blue-500 to-indigo-600" />
        </div>

        {/* Main video call area */}
        <div className="grid grid-cols-3 gap-4">

          {/* ── LEFT: Avatar panel (2/3 width) ── */}
          <div className="col-span-2">
            <div
              className="relative rounded-2xl overflow-hidden"
              style={{
                ...glassDark,
                height: '420px',
                background: 'linear-gradient(145deg, rgba(224,231,255,0.7) 0%, rgba(196,213,255,0.5) 100%)',
              }}
            >
              {/* 3D Avatar canvas */}
              <div className="absolute inset-0">
                <AvatarScene isSpeaking={isSpeaking} />
              </div>

              {/* Candidate webcam PiP — bottom right */}
              <div className="absolute bottom-4 right-4 z-10">
                {isCamOn && !camDenied ? (
                  <div
                    className="relative rounded-xl overflow-hidden shadow-lg"
                    style={{ width: 130, height: 96, border: '2px solid rgba(255,255,255,0.7)' }}
                  >
                    <video
                      ref={videoRef}
                      autoPlay
                      muted
                      playsInline
                      className="w-full h-full object-cover scale-x-[-1]"
                    />
                    <div className="absolute bottom-1 left-1.5 text-white text-xs font-semibold drop-shadow">
                      {form.candidateName || 'You'}
                    </div>
                  </div>
                ) : (
                  <div
                    className="flex flex-col items-center justify-center rounded-xl gap-1"
                    style={{
                      width: 130, height: 96,
                      background: 'rgba(148,163,184,0.3)',
                      border: '2px solid rgba(255,255,255,0.5)',
                    }}
                  >
                    <VideoOff size={24} className="text-slate-500" />
                    <span className="text-xs text-slate-500">Camera off</span>
                  </div>
                )}
              </div>

              {/* Speaking status badge */}
              <div className="absolute top-4 left-4 z-10">
                <AnimatePresence mode="wait">
                  {isSpeaking ? (
                    <motion.div
                      key="speaking"
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold text-blue-700"
                      style={{ background: 'rgba(219,234,254,0.9)', border: '1px solid rgba(147,197,253,0.6)' }}
                    >
                      {/* Sound wave dots */}
                      <span className="flex gap-0.5 items-end h-3">
                        {[0, 0.1, 0.2, 0.15, 0.05].map((d, i) => (
                          <motion.span
                            key={i}
                            className="w-0.5 bg-blue-500 rounded-full"
                            animate={{ height: ['4px', '12px', '4px'] }}
                            transition={{ duration: 0.5, delay: d, repeat: Infinity }}
                            style={{ display: 'inline-block' }}
                          />
                        ))}
                      </span>
                      ZYND AI is speaking...
                    </motion.div>
                  ) : loading ? (
                    <motion.div
                      key="thinking"
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold text-indigo-700"
                      style={{ background: 'rgba(238,242,255,0.9)', border: '1px solid rgba(199,210,254,0.6)' }}
                    >
                      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity }}>
                        <RefreshCw size={12} />
                      </motion.div>
                      Thinking...
                    </motion.div>
                  ) : (
                    <motion.div
                      key="yourturn"
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className="px-3 py-1.5 rounded-full text-xs font-bold text-green-700"
                      style={{ background: 'rgba(220,252,231,0.9)', border: '1px solid rgba(134,239,172,0.6)' }}
                    >
                      Your turn to answer
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* AI name badge */}
              <div className="absolute bottom-4 left-4 z-10">
                <div
                  className="px-3 py-1.5 rounded-full text-xs font-bold text-indigo-800"
                  style={{ background: 'rgba(224,231,255,0.85)', border: '1px solid rgba(165,180,252,0.5)' }}
                >
                  ZYND AI Interviewer
                </div>
              </div>
            </div>
          </div>

          {/* ── RIGHT: Chat transcript (1/3 width) ── */}
          <div className="col-span-1 flex flex-col gap-3">
            {/* Current question highlight */}
            <AnimatePresence mode="wait">
              {currentQuestion && (
                <motion.div
                  key={currentQuestion}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="rounded-xl p-4"
                  style={{ ...glassDark, background: 'rgba(239,246,255,0.75)' }}
                >
                  <p className="text-xs font-bold text-blue-600 mb-1.5">
                    {loading && !isSpeaking ? 'Processing...' : isSpeaking ? 'Current Question' : 'Question'}
                  </p>
                  <p className="text-sm text-gray-800 leading-relaxed">{currentQuestion}</p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Chat scroll log */}
            <div
              role="log"
              aria-live="polite"
              className="flex-1 rounded-xl p-3 space-y-2.5 overflow-y-auto scrollbar-hide"
              style={{ ...glass, maxHeight: '240px' }}
            >
              <AnimatePresence>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-2 ${msg.role === 'candidate' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role === 'interviewer' && (
                      <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Bot size={11} className="text-white" />
                      </div>
                    )}
                    <div className={`max-w-[85%] rounded-xl px-3 py-2 text-xs leading-relaxed ${
                      msg.role === 'interviewer'
                        ? 'bg-white/70 text-gray-700 border border-white/80'
                        : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
                    } ${msg.isFinal ? 'border-2 border-green-400' : ''}`}>
                      {msg.content}
                    </div>
                    {msg.role === 'candidate' && (
                      <div className="w-6 h-6 rounded-lg bg-gray-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <User size={11} className="text-gray-600" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              {loading && !isSpeaking && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                    <Bot size={11} className="text-white" />
                  </div>
                  <div className="bg-white/70 border border-white/80 rounded-xl px-3 py-2 flex items-center gap-1.5">
                    {[0, 0.2, 0.4].map((d, i) => (
                      <motion.div key={i} animate={{ y: [0, -5, 0] }} transition={{ duration: 0.5, delay: d, repeat: Infinity }}
                        className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                    ))}
                  </div>
                </motion.div>
              )}
              <div ref={chatEndRef} />
            </div>
          </div>
        </div>

        {/* ── Input + Controls bar ── */}
        <div className="rounded-2xl p-4 space-y-3" style={glass}>
          {/* Answer input */}
          <div className="relative">
            <textarea
              ref={textAreaRef}
              value={currentAnswer}
              onChange={e => setCurrentAnswer(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder={
                recognizing
                  ? 'Listening... speak your answer'
                  : 'Type your answer here, or click the mic to speak... (Ctrl+Enter to send)'
              }
              disabled={loading}
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none disabled:opacity-50 pr-10"
            />
            {recognizing && (
              <motion.div
                animate={{ opacity: [1, 0.4, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
                className="absolute right-3 top-3"
              >
                <Mic size={16} className="text-red-500" />
              </motion.div>
            )}
            {/* Interim STT text shown as a non-editable hint below the textarea */}
            {interimText && (
              <p className="text-xs text-blue-500 italic px-1 mt-1">
                🎤 {interimText}
              </p>
            )}
          </div>

          {/* Controls row */}
          <div className="flex items-center justify-between gap-3">
            {/* Left: media controls */}
            <div className="flex items-center gap-2">
              {/* Mic button */}
              {SPEECH_RECOGNITION_AVAILABLE ? (
                <motion.button
                  onClick={toggleMic}
                  disabled={loading}
                  whileHover={{ scale: 1.07 }}
                  whileTap={{ scale: 0.93 }}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold border transition-all disabled:opacity-50 ${
                    recognizing
                      ? 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100'
                      : 'bg-white/60 text-gray-600 border-white/80 hover:bg-white/80'
                  }`}
                  title={recognizing ? 'Stop listening' : 'Speak your answer'}
                >
                  {recognizing ? <MicOff size={14} /> : <Mic size={14} />}
                  {recognizing ? 'Stop' : 'Speak'}
                </motion.button>
              ) : (
                <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold border border-gray-200 text-gray-400 cursor-not-allowed select-none">
                  <MicOff size={14} /> Voice N/A
                </div>
              )}

              {/* Camera toggle */}
              <motion.button
                onClick={toggleCamera}
                whileHover={{ scale: 1.07 }}
                whileTap={{ scale: 0.93 }}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold border transition-all ${
                  isCamOn
                    ? 'bg-white/60 text-gray-600 border-white/80 hover:bg-white/80'
                    : 'bg-gray-100 text-gray-400 border-gray-200'
                }`}
                title={isCamOn ? 'Turn off camera' : 'Turn on camera'}
              >
                {isCamOn ? <Video size={14} /> : <VideoOff size={14} />}
                {isCamOn ? 'Cam On' : 'Cam Off'}
              </motion.button>

              {/* TTS mute */}
              {SPEECH_SYNTHESIS_AVAILABLE && (
                <motion.button
                  onClick={toggleMute}
                  whileHover={{ scale: 1.07 }}
                  whileTap={{ scale: 0.93 }}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold border transition-all ${
                    isMuted
                      ? 'bg-gray-100 text-gray-400 border-gray-200'
                      : 'bg-white/60 text-gray-600 border-white/80 hover:bg-white/80'
                  }`}
                  title={isMuted ? 'Unmute AI voice' : 'Mute AI voice'}
                >
                  {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
                  {isMuted ? 'Unmute' : 'Mute AI'}
                </motion.button>
              )}
            </div>

            {/* Right: hint + send */}
            <div className="flex items-center gap-3">
              <p className="text-xs text-gray-400 hidden sm:block">Ctrl+Enter to send</p>
              <motion.button
                onClick={submitAnswer}
                disabled={!currentAnswer.trim() || loading}
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-white text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ background: 'linear-gradient(135deg, #3b82f6, #4f46e5)', boxShadow: '0 4px 14px rgba(59,130,246,0.35)' }}
              >
                <Send size={15} /> Send Answer
              </motion.button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs">
              <AlertTriangle size={13} /> {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ── COMPLETED SCREEN ──────────────────────────────────────────────────────

  if (step === 'completed' && finalResult) {
    const score = finalResult.final_score || 0;
    const grade = score >= 85 ? 'Excellent' : score >= 70 ? 'Strong' : score >= 55 ? 'Average' : 'Below Average';
    const gradeColor = score >= 85 ? 'text-green-600' : score >= 70 ? 'text-blue-600' : score >= 55 ? 'text-amber-600' : 'text-red-600';

    return (
      <div className="max-w-2xl mx-auto space-y-5">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className="rounded-2xl p-8 text-center" style={glass}>
          <motion.div
            initial={{ scale: 0 }} animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
            className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-500/30"
          >
            <CheckCircle2 className="text-white" size={40} />
          </motion.div>
          <h3 className="text-2xl font-black text-gray-900 mb-1">Interview Complete!</h3>
          <p className="text-gray-500 mb-6">All {finalResult.total_questions} questions answered</p>

          <div className="inline-flex flex-col items-center gap-1 px-8 py-5 rounded-2xl bg-white/60 border border-white/80 mb-6">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Reasoning Quality Score</span>
            <motion.span
              className={`text-6xl font-black ${gradeColor}`}
              initial={{ scale: 0 }} animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.4 }}
            >
              {score}
            </motion.span>
            <span className="text-sm font-semibold text-gray-500">/ 100 — {grade}</span>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-6">
            <div className="p-4 rounded-xl bg-white/50 border border-white/60">
              <p className="text-xs text-gray-500 mb-1">Questions Asked</p>
              <p className="text-xl font-black text-gray-900">{finalResult.total_questions}</p>
            </div>
            <div className="p-4 rounded-xl bg-white/50 border border-white/60">
              <p className="text-xs text-gray-500 mb-1">Role Assessed</p>
              <p className="text-sm font-bold text-gray-900 truncate">{form.jobRole}</p>
            </div>
          </div>

          <button
            onClick={reset}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/60 border border-white/80 text-gray-700 font-semibold hover:bg-white/80 transition-all text-sm mx-auto"
          >
            <RefreshCw size={15} /> Start New Interview
          </button>
        </motion.div>
      </div>
    );
  }

  return null;
}
