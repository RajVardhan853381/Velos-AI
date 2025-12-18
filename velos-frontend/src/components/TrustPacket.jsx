import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, Shield, CheckCircle, XCircle, Download, Lock, Unlock, FileText, Database, Clock, AlertTriangle } from 'lucide-react';

const BlockItem = ({ label, value, icon: Icon }) => (
  <div className="flex items-center justify-between p-4 bg-indigo-900/30 rounded-lg border border-indigo-700/30">
    <div className="flex items-center gap-3">
      <Icon className="text-indigo-400" size={18} />
      <span className="text-indigo-300 text-sm">{label}</span>
    </div>
    <span className="text-white font-mono text-sm">{value}</span>
  </div>
);

const DiffRow = ({ field, original, redacted }) => (
  <div className="grid grid-cols-3 gap-4 p-3 bg-purple-900/30 rounded-lg hover:bg-purple-800/40 transition-all">
    <div className="text-indigo-300 font-medium">{field}</div>
    <div className="text-green-400 font-mono text-sm">{original}</div>
    <div className="text-red-400 font-mono text-sm">{redacted}</div>
  </div>
);

const TrustPacket = () => {
  const [candidateId, setCandidateId] = useState('');
  const [trustPacket, setTrustPacket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState(null);

  const fetchTrustPacket = async () => {
    if (!candidateId.trim()) {
      alert('Please enter a candidate ID');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/trust-packet/${candidateId}`);
      if (response.ok) {
        const data = await response.json();
        setTrustPacket(data);
      } else {
        alert('Trust packet not found');
        setTrustPacket(null);
      }
    } catch (error) {
      console.error('Failed to fetch trust packet:', error);
      alert('Failed to fetch trust packet');
    } finally {
      setLoading(false);
    }
  };

  const verifyIntegrity = async () => {
    if (!candidateId.trim()) return;

    setVerifying(true);
    try {
      const response = await fetch(`http://localhost:8000/api/verify-integrity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId })
      });

      if (response.ok) {
        const data = await response.json();
        setVerified(data.verified);
      }
    } catch (error) {
      console.error('Failed to verify integrity:', error);
    } finally {
      setVerifying(false);
    }
  };

  const downloadDossier = async () => {
    if (!candidateId.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/api/candidate-dossier/${candidateId}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${candidateId}_dossier.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to download dossier:', error);
    }
  };

  return (
    <div className="min-h-screen bg-white p-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <Eye className="text-white" size={28} />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-violet-900">Trust Packet Viewer</h1>
            <p className="text-slate-500">Blockchain-verified candidate integrity records</p>
          </div>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/95 backdrop-blur-sm border border-violet-100 shadow-xl rounded-2xl p-6 mb-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-violet-600/10 pointer-events-none" />
        <div className="flex gap-4 relative z-10">
          <input type="text" placeholder="Enter Candidate ID (e.g., cand_123)" value={candidateId} onChange={(e) => setCandidateId(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && fetchTrustPacket()} className="flex-1 px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500 transition-all" />
          <button onClick={fetchTrustPacket} disabled={loading} className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed">{loading ? 'Loading...' : 'Fetch Packet'}</button>
        </div>
      </motion.div>

      {trustPacket && (
        <div className="space-y-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-indigo-900/50 backdrop-blur-xl border border-indigo-700/50 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Database className="text-indigo-400" size={24} />
                <h2 className="text-2xl font-bold text-white">Blockchain Transaction</h2>
              </div>
              <div className="flex gap-3">
                <button onClick={verifyIntegrity} disabled={verifying} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all">{verifying ? <>Verifying...</> : <><Shield size={18} />Verify Integrity</>}</button>
                <button onClick={downloadDossier} className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all"><Download size={18} />Download Dossier</button>
              </div>
            </div>

            <div className="space-y-3">
              <BlockItem icon={FileText} label="Transaction Hash" value={trustPacket.transaction_hash || 'N/A'} />
              <BlockItem icon={Database} label="Block Number" value={trustPacket.block_number || 'N/A'} />
              <BlockItem icon={Clock} label="Timestamp" value={trustPacket.timestamp ? new Date(trustPacket.timestamp).toLocaleString() : 'N/A'} />
              <BlockItem icon={Shield} label="Merkle Root" value={trustPacket.merkle_root || 'N/A'} />
            </div>

            {verified !== null && (
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className={`mt-6 p-4 rounded-xl flex items-center gap-3 ${verified ? 'bg-green-900/30 border border-green-700/50' : 'bg-red-900/30 border border-red-700/50'}`}>{verified ? <><CheckCircle className="text-green-400" size={24} /><div><p className="text-white font-semibold">Integrity Verified</p><p className="text-green-300 text-sm">All data matches blockchain records</p></div></> : <><XCircle className="text-red-400" size={24} /><div><p className="text-white font-semibold">Verification Failed</p><p className="text-red-300 text-sm">Data tampering detected</p></div></>}</motion.div>
            )}
          </motion.div>

          {trustPacket.pii_diff && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-purple-900/50 backdrop-blur-xl border border-purple-700/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <Lock className="text-purple-400" size={24} />
                <h2 className="text-2xl font-bold text-white">PII Redaction Proof</h2>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4 px-3">
                <div className="text-indigo-300 font-bold text-sm">Field</div>
                <div className="text-green-400 font-bold text-sm flex items-center gap-2"><Unlock size={16} /> Original</div>
                <div className="text-red-400 font-bold text-sm flex items-center gap-2"><Lock size={16} /> Redacted</div>
              </div>

              <div className="space-y-2">
                {Object.entries(trustPacket.pii_diff).map(([field, values]) => (<DiffRow key={field} field={field} original={values.original || 'N/A'} redacted={values.redacted || 'N/A'} />))}
              </div>

              <div className="mt-6 p-4 bg-purple-800/30 rounded-lg border border-purple-700/30">
                <div className="flex items-center gap-3 mb-2">
                  <AlertTriangle className="text-yellow-400" size={20} />
                  <p className="text-white font-semibold">Redaction Summary</p>
                </div>
                <p className="text-purple-300 text-sm">{Object.keys(trustPacket.pii_diff).length} field(s) redacted for privacy compliance</p>
              </div>
            </motion.div>
          )}

          {trustPacket.metadata && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-indigo-900/50 backdrop-blur-xl border border-indigo-700/50 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <FileText className="text-indigo-400" size={24} />
                <h2 className="text-2xl font-bold text-white">Metadata</h2>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {Object.entries(trustPacket.metadata).map(([key, value]) => (
                  <div key={key} className="p-4 bg-indigo-950/50 rounded-lg">
                    <p className="text-indigo-400 text-sm mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                    <p className="text-white font-semibold">{String(value)}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      )}

      {!trustPacket && !loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-20">
          <Eye className="w-20 h-20 text-indigo-700 mx-auto mb-4 opacity-50" />
          <p className="text-indigo-300 text-lg">Enter a candidate ID to view trust packet</p>
        </motion.div>
      )}
    </div>
  );
};

export default TrustPacket;
