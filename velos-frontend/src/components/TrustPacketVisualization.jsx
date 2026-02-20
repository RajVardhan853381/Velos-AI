import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, CheckCircle, XCircle, Download, Lock, ExternalLink,
  Clock, AlertTriangle, Copy, Eye, FileJson, QrCode,
  Link as LinkIcon, Package, Fingerprint, Activity
} from 'lucide-react';
import { API_BASE } from '../config.js';

// Blockchain metadata card
const BlockchainCard = ({ blockchain }) => {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  const copyAddress = async () => {
    try {
      await navigator.clipboard.writeText(blockchain.wallet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopyError(true);
      setTimeout(() => setCopyError(false), 3000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gradient-to-br from-white/40 to-white/30 backdrop-blur-xl border border-indigo-200/60 rounded-2xl p-6 shadow-2xl"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
          <LinkIcon className="text-white" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Blockchain Network</h3>
          <p className="text-gray-600 text-sm">{blockchain.network}</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="p-3 bg-white/40 rounded-lg">
          <p className="text-gray-600 text-xs mb-1">Chain ID</p>
          <p className="text-gray-900 font-mono text-sm">{blockchain.chain_id}</p>
        </div>

        <div className="p-3 bg-white/40 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <p className="text-gray-600 text-xs">Wallet Address</p>
            <button
              onClick={copyAddress}
              className="text-indigo-600 hover:text-gray-600 transition-colors"
              title="Copy address"
            >
              {copied ? <CheckCircle size={14} /> : <Copy size={14} />}
            </button>
          </div>
          <p className="text-gray-900 font-mono text-xs break-all">{blockchain.wallet}</p>
          {copyError && <p className="text-red-500 text-xs mt-1">Failed to copy — please copy manually.</p>}
        </div>

        <div className="flex gap-2">
          <a
            href={blockchain.explorer}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-400 hover:bg-blue-500 text-gray-900 text-sm rounded-lg transition-all"
          >
            <ExternalLink size={14} />
            View on Explorer
          </a>
        </div>

        <div className="pt-3 border-t border-indigo-200/60">
          <div className="flex items-center justify-between">
            <span className="text-gray-600 text-sm">Credentials Issued</span>
            <span className="text-gray-900 font-bold text-lg">{blockchain.credentials_count}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// W3C Credential Card
const CredentialCard = ({ credential, index, onExport }) => {
  const [expanded, setExpanded] = useState(false);

  const getCredentialTypeColor = (type) => {
    const colors = {
      'EligibilityCredential': 'from-green-100/60 to-emerald-100/60 border-green-200/60',
      'SkillMatchCredential': 'from-blue-100/60 to-indigo-100/60 border-blue-200/60',
      'AuthenticityCredential': 'from-purple-100/60 to-pink-100/60 border-purple-200/60'
    };
    return colors[type] || 'from-gray-500/20 to-slate-500/20 border-gray-500/30';
  };

  const getCredentialIcon = (type) => {
    if (type === 'EligibilityCredential') return Shield;
    if (type === 'SkillMatchCredential') return Package;
    if (type === 'AuthenticityCredential') return Fingerprint;
    return FileJson;
  };

  const credentialType = (Array.isArray(credential.type) ? credential.type : []).find(t => t !== 'VerifiableCredential') || 'Credential';
  const Icon = getCredentialIcon(credentialType);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`bg-gradient-to-br ${getCredentialTypeColor(credentialType)} backdrop-blur-xl border rounded-xl p-4 shadow-lg`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
            <Icon className="text-gray-900" size={20} />
          </div>
          <div>
            <h4 className="text-gray-900 font-semibold">{credentialType.replace('Credential', '')}</h4>
            <p className="text-gray-500 text-xs font-mono">{credential.id?.split(':').pop()?.slice(0, 12)}...</p>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Eye size={18} />
        </button>
      </div>

      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="space-y-2 pt-3 border-t border-white/10"
        >
          <div className="p-2 bg-white/40 rounded text-xs">
            <p className="text-gray-600 mb-1">Issuer DID</p>
            <p className="text-gray-900 font-mono break-all">{credential.issuer}</p>
          </div>

          <div className="p-2 bg-white/40 rounded text-xs">
            <p className="text-gray-600 mb-1">Subject DID</p>
            <p className="text-gray-900 font-mono break-all">{credential.credentialSubject?.id}</p>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 bg-white/40 rounded text-xs">
              <p className="text-gray-600 mb-1">Issued</p>
              <p className="text-gray-900">{new Date(credential.issuanceDate).toLocaleDateString()}</p>
            </div>
            <div className="p-2 bg-white/40 rounded text-xs">
              <p className="text-gray-600 mb-1">Expires</p>
              <p className="text-gray-900">{credential.expirationDate ? new Date(credential.expirationDate).toLocaleDateString() : 'N/A'}</p>
            </div>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              onClick={() => onExport(credential.id, 'json-ld')}
              className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-blue-400 hover:bg-blue-500 text-white text-xs rounded transition-all"
            >
              <FileJson size={12} />
              JSON-LD
            </button>
            <button
              onClick={() => onExport(credential.id, 'qr')}
              className="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-all"
            >
              <QrCode size={12} />
              QR Code
            </button>
          </div>

          {credential.proof && (
            <div className="p-2 bg-green-50 border border-green-300 rounded text-xs">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle size={12} className="text-green-600" />
                <p className="text-green-700 font-semibold">Cryptographically Signed</p>
              </div>
              <p className="text-green-600">Type: {credential.proof.type}</p>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
};

// Integrity Block Visualization
const IntegrityBlock = ({ trustLayer, onVerify, verified }) => {
  const [showHash, setShowHash] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-white/40 to-white/30 backdrop-blur-xl border border-purple-200/60 rounded-2xl p-6 shadow-2xl"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
          <Lock className="text-gray-900" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Cryptographic Proof</h3>
          <p className="text-purple-700 text-sm">Tamper-evident integrity seal</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="p-3 bg-white/40 rounded-lg">
          <div className="flex items-center justify-between mb-1">
            <p className="text-purple-300 text-xs">Block ID</p>
            <button
              onClick={() => setShowHash(!showHash)}
              className="text-purple-600 hover:text-purple-300 transition-colors"
            >
              <Eye size={14} />
            </button>
          </div>
          <p className="text-gray-900 font-mono text-xs">
            {showHash ? trustLayer.block_id : `${trustLayer.block_id?.slice(0, 16)}...`}
          </p>
        </div>

        <div className="p-3 bg-white/40 rounded-lg">
          <p className="text-purple-300 text-xs mb-1">Data Hash (SHA-256)</p>
          <p className="text-gray-900 font-mono text-xs break-all">{trustLayer.data_hash?.slice(0, 32)}...</p>
        </div>

        <div className="p-3 bg-white/40 rounded-lg">
          <p className="text-purple-300 text-xs mb-1">Digital Signature</p>
          <p className="text-gray-900 font-mono text-xs">{trustLayer.signature}</p>
        </div>

        <div className="p-3 bg-white/40 rounded-lg">
          <div className="flex items-center gap-2">
            <Clock className="text-purple-600" size={14} />
            <p className="text-purple-300 text-xs">Sealed At</p>
          </div>
          <p className="text-gray-900 text-sm mt-1">
            {trustLayer.sealed_at ? new Date(trustLayer.sealed_at).toLocaleString() : 'N/A'}
          </p>
        </div>

        <button
          onClick={onVerify}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-400 to-emerald-400 hover:from-green-500 hover:to-emerald-500 text-gray-900 font-semibold rounded-lg transition-all shadow-lg"
        >
          <Shield size={18} />
          Verify Integrity
        </button>

        {verified !== null && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`p-4 rounded-lg flex items-center gap-3 ${
              verified
                ? 'bg-green-900/30 border border-green-200/60'
                : 'bg-red-900/30 border border-red-200/60'
            }`}
          >
            {verified ? (
              <>
                <CheckCircle className="text-green-600" size={24} />
                <div>
                  <p className="text-gray-900 font-semibold">Integrity Verified ✓</p>
                  <p className="text-green-300 text-xs">Hash matches blockchain record</p>
                </div>
              </>
            ) : (
              <>
                <XCircle className="text-red-400" size={24} />
                <div>
                  <p className="text-gray-900 font-semibold">Verification Failed</p>
                  <p className="text-red-300 text-xs">Data tampering detected</p>
                </div>
              </>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

// Main component
const TrustPacketVisualization = () => {
  const [candidateId, setCandidateId] = useState('');
  const [trustPacket, setTrustPacket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [verified, setVerified] = useState(null);
  const [error, setError] = useState(null);
  const [exportError, setExportError] = useState(null);

  const fetchTrustPacket = async () => {
    if (!candidateId.trim()) {
      setError('Please enter a candidate ID');
      return;
    }

    setLoading(true);
    setError(null);
    setTrustPacket(null);
    setVerified(null);

    try {
      const response = await fetch(`${API_BASE}/api/trust-packet/${candidateId}/enhanced`);

      if (response.ok) {
        const data = await response.json();
        setTrustPacket(data);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || `Error ${response.status}: Failed to fetch trust packet`);
      }
    } catch (err) {
      console.error('Failed to fetch trust packet:', err);
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const verifyIntegrity = async () => {
    if (!candidateId.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/api/candidates/${candidateId}/verify-integrity`);

      if (response.ok) {
        const data = await response.json();
        setVerified(data.verification_report?.verified || false);
      }
    } catch (err) {
      console.error('Failed to verify integrity:', err);
      setVerified(false);
    }
  };

  const exportCredential = async (credentialId, format) => {
    try {
      const response = await fetch(`${API_BASE}/api/credentials/${credentialId}/export?format=${format}`);

      if (response.ok) {
        const data = await response.json();

        if (format === 'qr') {
          // Display QR code in modal or download
          const link = document.createElement('a');
          link.href = `data:image/png;base64,${data.qr_code}`;
          link.download = `${credentialId.split(':').pop()}_qr.png`;
          link.click();
        } else {
          // Download JSON
          const blob = new Blob([JSON.stringify(data.credential, null, 2)], { type: 'application/json' });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${credentialId.split(':').pop()}.json`;
          link.click();
          window.URL.revokeObjectURL(url);
        }
      }
    } catch (err) {
      setExportError('Failed to export credential. Please try again.');
      setTimeout(() => setExportError(null), 4000);
    }
  };

  return (
    <div className="p-0">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-2">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-2xl">
            <Activity className="text-white" size={32} />
          </div>
          <div>
            <h1 className="text-5xl font-bold text-gray-900">Trust Packet Visualization</h1>
            <p className="text-gray-600 text-lg">Blockchain-verified credential explorer</p>
          </div>
        </div>
      </motion.div>

      {/* Search Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/40 backdrop-blur-xl border border-white/60 rounded-2xl p-6 mb-8"
      >
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Enter Candidate ID (e.g., CAND-A1B2C3D4)"
            value={candidateId}
            onChange={(e) => setCandidateId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchTrustPacket()}
            className="flex-1 px-6 py-4 bg-white/40 border border-indigo-200/60 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
          <button
            onClick={fetchTrustPacket}
            disabled={loading}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-2xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Load Trust Packet'}
          </button>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-center gap-3"
          >
            <AlertTriangle className="text-red-400" size={20} />
            <p className="text-red-200">{error}</p>
          </motion.div>
        )}

        {exportError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3"
          >
            <AlertTriangle className="text-red-500 flex-shrink-0" size={16} />
            <p className="text-red-700 text-sm">{exportError}</p>
          </motion.div>
        )}
      </motion.div>

      {/* Trust Packet Display */}
      {trustPacket && (
        <div className="space-y-6">
          {/* Blockchain Section */}
          {trustPacket.blockchain?.enabled && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <BlockchainCard blockchain={trustPacket.blockchain} />
              
              {trustPacket.trust_layer && (
                <div className="lg:col-span-2">
                  <IntegrityBlock
                    trustLayer={trustPacket.trust_layer}
                    onVerify={verifyIntegrity}
                    verified={verified}
                  />
                </div>
              )}
            </div>
          )}

          {/* Credentials Section */}
          {Array.isArray(trustPacket.credentials) && trustPacket.credentials.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-3">
                <Package className="text-indigo-600" />
                W3C Verifiable Credentials ({trustPacket.credentials.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {trustPacket.credentials.map((credential, index) => (
                  <CredentialCard
                    key={credential.id}
                    credential={credential}
                    index={index}
                    onExport={exportCredential}
                  />
                ))}
              </div>
            </motion.div>
          )}

          {/* No blockchain message */}
          {!trustPacket.blockchain?.enabled && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-6 bg-amber-50 border border-amber-400 rounded-xl"
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-amber-600" size={24} />
                <div>
                  <p className="text-gray-900 font-semibold">Blockchain Integration Not Enabled</p>
                  <p className="text-amber-700 text-sm">This trust packet uses legacy verification</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
};

export default TrustPacketVisualization;
