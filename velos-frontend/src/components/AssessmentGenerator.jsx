import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ClipboardList, Sparkles, RefreshCw, ChevronRight,
  CheckCircle2, XCircle, AlertTriangle,
  Clock, Brain, Target, ChevronDown
} from 'lucide-react';
import { API_BASE } from '../config.js';

const glass = {
  background: 'rgba(255,255,255,0.35)',
  backdropFilter: 'blur(20px)',
  border: '1px solid rgba(255,255,255,0.6)',
  boxShadow: '0 8px 32px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.7)',
};

const difficultyColor = {
  easy: 'bg-green-100 text-green-700',
  medium: 'bg-amber-100 text-amber-700',
  hard: 'bg-red-100 text-red-700',
};

export default function AssessmentGenerator() {
  const [step, setStep] = useState('setup'); // setup | taking | results
  const [form, setForm] = useState({ role: '', level: 'Mid', techStack: '', numQuestions: 5 });
  const [assessment, setAssessment] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState('');
  const [expandedQ, setExpandedQ] = useState(null);

  const generate = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/assessment/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role: form.role,
          level: form.level,
          tech_stack: form.techStack,
          num_questions: form.numQuestions,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Generation failed');
      setAssessment(data);
      setSessionId(data.session_id);
      setAnswers({});
      setStep('taking');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitAssessment = async () => {
    setError('');
    setEvaluating(true);
    try {
      const res = await fetch(`${API_BASE}/api/assessment/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, answers }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Evaluation failed');
      setResults(data);
      setStep('results');
    } catch (err) {
      setError(err.message);
    } finally {
      setEvaluating(false);
    }
  };

  const reset = () => {
    setStep('setup');
    setAssessment(null);
    setSessionId(null);
    setAnswers({});
    setResults(null);
    setError('');
    setExpandedQ(null);
  };

  const answered = Object.keys(answers).filter(k => answers[k]?.trim()).length;
  const total = assessment?.questions?.length || 0;

  // ── SETUP ──────────────────────────────────────────────────────────
  if (step === 'setup') {
    return (
      <div className="max-w-xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <ClipboardList className="text-white" size={20} />
            </div>
            <div>
              <h2 className="text-2xl font-black text-gray-900">Assessment Generator</h2>
              <p className="text-sm text-gray-500">Instant AI-generated technical tests with LLM evaluation</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="rounded-2xl p-6 space-y-4" style={glass}>
          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Job Role *</label>
            <input
              value={form.role}
              onChange={e => setForm(p => ({ ...p, role: e.target.value }))}
              placeholder="e.g. Frontend Developer"
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-gray-600 mb-1.5 block">Level *</label>
              <select
                value={form.level}
                onChange={e => setForm(p => ({ ...p, level: e.target.value }))}
                className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-emerald-300"
              >
                {['Junior', 'Mid', 'Senior', 'Lead', 'Principal'].map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-bold text-gray-600 mb-1.5 block">Questions</label>
              <select
                value={form.numQuestions}
                onChange={e => setForm(p => ({ ...p, numQuestions: parseInt(e.target.value) }))}
                className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-emerald-300"
              >
                {[3, 4, 5, 7, 10].map(n => (
                  <option key={n} value={n}>{n} questions</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-bold text-gray-600 mb-1.5 block">Tech Stack *</label>
            <input
              value={form.techStack}
              onChange={e => setForm(p => ({ ...p, techStack: e.target.value }))}
              placeholder="e.g. React, TypeScript, Node.js, GraphQL"
              className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            />
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              <AlertTriangle size={15} /> {error}
            </div>
          )}

          <motion.button
            onClick={generate}
            disabled={!form.role.trim() || !form.techStack.trim() || loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-3.5 rounded-xl font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ background: 'linear-gradient(135deg, #10b981, #0d9488)', boxShadow: '0 4px 20px rgba(16,185,129,0.4)' }}
          >
            {loading ? (
              <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}><RefreshCw size={18} /></motion.div> Generating...</>
            ) : (
              <><Sparkles size={18} /> Generate Assessment <ChevronRight size={18} /></>
            )}
          </motion.button>
        </motion.div>

        <div className="grid grid-cols-3 gap-3">
          {[
            { icon: Brain, label: 'AI-Generated', desc: 'LLM crafts each question' },
            { icon: ClipboardList, label: 'MCQ + Short Answer', desc: 'Mixed question types' },
            { icon: Target, label: 'LLM Evaluated', desc: 'Checks logic, not keywords' },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="rounded-xl p-4 text-center" style={glass}>
              <Icon className="mx-auto mb-2 text-teal-500" size={18} />
              <p className="text-xs font-bold text-gray-800">{label}</p>
              <p className="text-xs text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── TAKING ASSESSMENT ──────────────────────────────────────────────
  if (step === 'taking' && assessment) {
    return (
      <div className="max-w-3xl mx-auto space-y-5">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl p-5" style={glass}>
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-black text-gray-900">{assessment.title}</h2>
              <p className="text-sm text-gray-500 mt-0.5">{assessment.role} · {assessment.level} · {assessment.estimated_minutes} min</p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock size={15} />
              <span>{answered}/{total} answered</span>
            </div>
          </div>
          {/* Progress */}
          <div className="mt-3 w-full bg-gray-100 rounded-full h-2 overflow-hidden">
            <motion.div
              animate={{ width: `${(answered / total) * 100}%` }}
              className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500"
              transition={{ duration: 0.4 }}
            />
          </div>
        </motion.div>

        {/* Questions */}
        <div className="space-y-4">
          {assessment.questions.map((q, i) => (
            <motion.div
              key={q.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="rounded-2xl p-5" style={glass}
            >
              <div className="flex items-start gap-3 mb-3">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center flex-shrink-0 text-white text-xs font-black mt-0.5">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${difficultyColor[q.difficulty] || 'bg-gray-100 text-gray-600'}`}>
                      {q.difficulty}
                    </span>
                    <span className="text-xs text-gray-400">{q.topic}</span>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 border border-blue-100">
                      {q.type === 'multiple_choice' ? 'Multiple Choice' : 'Short Answer'}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-gray-800 leading-relaxed">{q.question}</p>
                </div>
              </div>

              {q.type === 'multiple_choice' && q.options ? (
                <div className="grid grid-cols-1 gap-2 ml-10">
                  {Object.entries(q.options).map(([key, val]) => (
                    <button
                      key={key}
                      onClick={() => setAnswers(p => ({ ...p, [q.id]: key }))}
                      className={`text-left px-4 py-2.5 rounded-xl text-sm transition-all border ${
                        answers[q.id] === key
                          ? 'bg-emerald-500 text-white border-emerald-500 font-semibold'
                          : 'bg-white/60 text-gray-700 border-white/80 hover:border-emerald-300 hover:bg-emerald-50/50'
                      }`}
                    >
                      <span className="font-bold mr-2">{key}.</span> {val}
                    </button>
                  ))}
                </div>
              ) : (
                <div className="ml-10">
                  <textarea
                    value={answers[q.id] || ''}
                    onChange={e => setAnswers(p => ({ ...p, [q.id]: e.target.value }))}
                    rows={4}
                    placeholder="Write your answer here..."
                    className="w-full rounded-xl px-3 py-2.5 text-sm bg-white/60 border border-white/80 focus:outline-none focus:ring-2 focus:ring-emerald-300 resize-none"
                  />
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            <AlertTriangle size={15} /> {error}
          </div>
        )}

        <div className="flex gap-3">
          <button onClick={reset} className="px-5 py-3 rounded-xl bg-white/60 border border-white/80 text-gray-600 font-semibold text-sm hover:bg-white/80 transition-all">
            Cancel
          </button>
          <motion.button
            onClick={submitAssessment}
            disabled={answered === 0 || evaluating}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1 py-3 rounded-xl font-bold text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ background: 'linear-gradient(135deg, #10b981, #0d9488)', boxShadow: '0 4px 20px rgba(16,185,129,0.35)' }}
          >
            {evaluating ? (
              <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}><RefreshCw size={18} /></motion.div> AI Evaluating...</>
            ) : (
              <><CheckCircle2 size={18} /> Submit Assessment ({answered}/{total} answered)</>
            )}
          </motion.button>
        </div>
      </div>
    );
  }

  // ── RESULTS ────────────────────────────────────────────────────────
  if (step === 'results' && results) {
    const gradeColor =
      results.grade === 'A' ? 'text-green-600' :
      results.grade === 'B' ? 'text-blue-600' :
      results.grade === 'C' ? 'text-amber-600' : 'text-red-600';
    const gradeBg =
      results.grade === 'A' ? 'from-green-50 to-emerald-50 border-green-200' :
      results.grade === 'B' ? 'from-blue-50 to-indigo-50 border-blue-200' :
      results.grade === 'C' ? 'from-amber-50 to-yellow-50 border-amber-200' :
      'from-red-50 to-rose-50 border-red-200';

    return (
      <div className="max-w-3xl mx-auto space-y-5">
        {/* Score Hero */}
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
          className={`rounded-2xl p-6 bg-gradient-to-br border ${gradeBg}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 mb-1">Assessment Results</p>
              <h3 className="text-2xl font-black text-gray-900 mb-2">{results.role} · {results.level}</h3>
              <div className={`text-5xl font-black ${gradeColor} mb-1`}>{results.percentage}%</div>
              <p className="text-sm text-gray-600">{results.total_score}/{results.max_score} points · Grade {results.grade}</p>
            </div>
            <motion.div
              initial={{ scale: 0 }} animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.3 }}
              className={`w-24 h-24 rounded-full flex items-center justify-center text-4xl font-black ${gradeColor} border-4 ${
                results.grade === 'A' ? 'border-green-300 bg-green-100' :
                results.grade === 'B' ? 'border-blue-300 bg-blue-100' :
                results.grade === 'C' ? 'border-amber-300 bg-amber-100' : 'border-red-300 bg-red-100'
              }`}
            >
              {results.grade}
            </motion.div>
          </div>
        </motion.div>

        {/* Per-question breakdown */}
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-gray-700">Question Breakdown</h4>
          {(results.results || []).map((r, i) => {
            const q = assessment?.questions?.find(q => q.id === r.question_id);
            const isOpen = expandedQ === r.question_id;
            return (
              <motion.div key={r.question_id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }} className="rounded-2xl overflow-hidden" style={glass}>
                <button
                  onClick={() => setExpandedQ(isOpen ? null : r.question_id)}
                  className="w-full flex items-center gap-3 p-4 text-left"
                >
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    r.type === 'multiple_choice'
                      ? r.is_correct ? 'bg-green-100' : 'bg-red-100'
                      : r.score >= 7 ? 'bg-green-100' : r.score >= 4 ? 'bg-amber-100' : 'bg-red-100'
                  }`}>
                    {r.type === 'multiple_choice'
                      ? r.is_correct ? <CheckCircle2 size={16} className="text-green-600" /> : <XCircle size={16} className="text-red-500" />
                      : <span className={`text-xs font-black ${r.score >= 7 ? 'text-green-600' : r.score >= 4 ? 'text-amber-600' : 'text-red-600'}`}>{r.score}</span>
                    }
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-gray-800 overflow-hidden text-ellipsis whitespace-nowrap">{q?.question || `Question ${i + 1}`}</p>
                    <p className="text-xs text-gray-500">{r.type === 'multiple_choice' ? (r.is_correct ? 'Correct' : 'Incorrect') : `${r.score}/10 points`}</p>
                  </div>
                  <ChevronDown size={16} className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                </button>

                <AnimatePresence>
                  {isOpen && (
                    <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
                      className="overflow-hidden border-t border-white/60">
                      <div className="p-4 space-y-2 bg-white/30">
                        <div>
                          <p className="text-xs font-bold text-gray-500 mb-1">Your Answer</p>
                          <p className="text-sm text-gray-700 bg-white/50 rounded-lg px-3 py-2">{r.candidate_answer || '(no answer)'}</p>
                        </div>
                        {r.correct_answer && (
                          <div>
                            <p className="text-xs font-bold text-gray-500 mb-1">Correct Answer</p>
                            <p className="text-sm text-gray-700">{r.correct_answer}</p>
                          </div>
                        )}
                        <div>
                          <p className="text-xs font-bold text-gray-500 mb-1">AI Feedback</p>
                          <p className="text-sm text-gray-700">{r.feedback}</p>
                        </div>
                        {r.concepts_missed?.length > 0 && (
                          <div>
                            <p className="text-xs font-bold text-red-500 mb-1">Missed Concepts</p>
                            <div className="flex flex-wrap gap-1">
                              {r.concepts_missed.map(c => (
                                <span key={c} className="text-xs px-2 py-0.5 rounded-full bg-red-50 text-red-600 border border-red-100">{c}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>

        <div className="flex justify-center">
          <button onClick={reset} className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/60 border border-white/80 text-gray-700 font-semibold hover:bg-white/80 transition-all text-sm">
            <RefreshCw size={15} /> Generate New Assessment
          </button>
        </div>
      </div>
    );
  }

  return null;
}
