# Blockchain Integration Guide - ZYND AIckathon 2025

## 🎉 Implementation Complete!

This guide will help you install dependencies, get testnet ETH, and test the full blockchain integration.

---

## ✅ What We Built

### Backend Infrastructure (1,100+ lines)
1. **Blockchain DID Manager** (`zynd/blockchain_did.py`)
   - Ethereum DIDs on Optimism Sepolia testnet
   - DID creation, signature verification, export/import
   - Real blockchain connection with fallback mode
   
2. **W3C Verifiable Credentials** (`zynd/w3c_credentials.py`)
   - Full W3C 1.1 spec with JSON-LD contexts
   - 3 credential types: Eligibility, SkillMatch, Authenticity
   - QR codes, JWT export, revocation registry
   
3. **ZeroMQ Agent Communication** (`zynd/agent_communication.py`)
   - Async pub/sub messaging with DID authentication
   - Message signing with Ethereum signatures

### Orchestrator Integration
- Updated `agents/orchestrator.py` with blockchain components
- All credentials now use W3C format with cryptographic proofs
- Real-time agent messaging via ZeroMQ

### API Endpoints (8 new endpoints)
- `/api/blockchain/network-info` - Network status
- `/api/credentials/{id}` - Get credential
- `/api/credentials/verify` - Verify external credential
- `/api/credentials/{id}/export` - Export (JSON-LD/JWT/QR)
- `/api/credentials/{id}/revoke` - Revoke credential
- `/api/agents/messages` - Real-time messages
- `/api/trust-packet/{id}/enhanced` - Enhanced trust packet

### React Components (1,500+ lines)
1. **TrustPacketVisualization.jsx** - Blockchain explorer
2. **RAGEvidenceExplorer.jsx** - Evidence search
3. **LiveAgentDashboard.jsx** - Real-time messaging
4. **ZeroBiasProof.jsx** - PII redaction diff viewer

---

## 📦 Installation Steps

### 1. Install Python Dependencies

The blockchain dependencies are already in `requirements.txt`. Install them:

```bash
cd Velos-AI-main
pip install -r requirements.txt
```

Key new dependencies:
- `eth-account>=0.11.0` - Ethereum account management
- `web3>=6.15.0` - Web3 for blockchain interaction
- `pyzmq>=25.1.0` - ZeroMQ for P2P messaging
- `qrcode[pil]>=7.4.0` - QR code generation
- `jsonschema>=4.20.0` - JSON schema validation

### 2. Verify Installation

```bash
python -c "import eth_account, web3, zmq, qrcode; print('✅ All blockchain dependencies installed!')"
```

---

## 🔑 Get Testnet ETH

### Step 1: Run the server to get your wallet address

```bash
python server.py
```

Look for this output:
```
✅ Blockchain DID Manager initialized
   Wallet: 0xYourWalletAddressHere
   Network: Optimism Sepolia
```

Copy your wallet address!

### Step 2: Get free testnet ETH

Visit the Optimism Sepolia faucet:
**https://www.alchemy.com/faucets/optimism-sepolia**

1. Paste your wallet address
2. Click "Send Me ETH"
3. Wait 30 seconds for confirmation

### Step 3: Verify you received ETH

Visit the blockchain explorer:
**https://sepolia-optimism.etherscan.io/address/YOUR_WALLET_ADDRESS**

You should see your balance!

---

## 🧪 Testing Guide

### Test 1: Check Blockchain Connection

```bash
curl http://localhost:8000/api/blockchain/network-info
```

Expected response:
```json
{
  "enabled": true,
  "network_name": "Optimism Sepolia",
  "chain_id": 11155420,
  "wallet_address": "0x...",
  "balance": "0.05 ETH",
  "connected": true,
  "explorer_url": "https://sepolia-optimism.etherscan.io/address/0x...",
  "faucet_url": "https://www.alchemy.com/faucets/optimism-sepolia"
}
```

### Test 2: Run Full Verification Pipeline

```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "John Doe\nEmail: john@example.com\nPhone: 555-1234\n5 years Python experience",
    "job_description": "Senior Python Developer\nRequirements: 3+ years Python",
    "min_years": 3
  }'
```

Look for:
- `blockchain_metadata` in the response
- `credentials_issued` array with W3C credentials
- `agent_messages` array with DID-signed messages

### Test 3: View Trust Packet

Get the candidate ID from Test 2, then:

```bash
curl http://localhost:8000/api/trust-packet/{CANDIDATE_ID}/enhanced
```

Expected:
- `blockchain.enabled: true`
- `blockchain.credentials_count: 3`
- `credentials` array with full W3C format
- `agent_messages` with blockchain signatures

### Test 4: Export Credential as QR Code

```bash
curl "http://localhost:8000/api/credentials/{CREDENTIAL_ID}/export?format=qr"
```

You'll get a base64-encoded QR code image!

### Test 5: View Real-Time Messages

```bash
curl http://localhost:8000/api/agents/messages?limit=10
```

Expected:
- Array of messages with `sender_did`, `recipient_did`
- Each message has `signature` field
- Message types: TASK_HANDOFF, CREDENTIAL_ISSUED, etc.

---

## 🎨 Testing React Components

### 1. Start the Frontend

```bash
cd velos-frontend
npm install
npm run dev
```

Visit: http://localhost:5173

### 2. Test Each Component

#### Trust Packet Visualization
- Navigate to the component (you may need to add routes)
- Enter a candidate ID
- Click "Load Trust Packet"
- Verify:
  - Blockchain metadata card shows
  - Credentials display with expand/collapse
  - Can export as QR code
  - Integrity verification works

#### RAG Evidence Explorer
- Enter candidate ID
- Enter search query (e.g., "Python")
- Verify:
  - Evidence chunks load
  - Text highlighting works
  - Stats show matches

#### Live Agent Dashboard
- Click "Refresh" to load messages
- Enable "Live" mode for auto-refresh
- Verify:
  - Messages show agent flow
  - Can expand to see full DIDs
  - Signatures display

#### Zero-Bias Proof
- Enter candidate ID
- Click "Load Diff"
- Verify:
  - Redaction stats show
  - Side-by-side view works
  - Unified diff highlights deletions/additions
  - Can download report

---

## 🚀 Demo Script

### The Perfect Demo Flow

1. **Start with Network Info**
   - Show blockchain explorer with your wallet
   - Point out Optimism Sepolia testnet
   - Mention W3C compliance

2. **Run Verification Pipeline**
   - Upload sample resume
   - Watch it go through 3 agents
   - Point out credential issuance messages

3. **Show Trust Packet Visualization**
   - Display blockchain metadata
   - Expand credentials to show W3C format
   - Export a credential as QR code
   - Verify integrity

4. **Demonstrate RAG Evidence**
   - Search for skills (e.g., "Python", "AWS")
   - Show evidence highlighting
   - Explain how this proves claims

5. **Live Agent Dashboard**
   - Show real-time message flow
   - Expand a message to show DID signature
   - Explain blockchain authentication

6. **Zero-Bias Proof**
   - Show side-by-side original vs redacted
   - Point out PII categories removed
   - Show redaction statistics
   - Switch to unified diff view

---

## 🎯 Hackathon Talking Points

### Technical Depth
- ✅ Real Ethereum DIDs on Optimism Sepolia (not simulated!)
- ✅ Full W3C Verifiable Credentials 1.1 spec
- ✅ EthereumEip712Signature2021 cryptographic proofs
- ✅ ZeroMQ P2P messaging with DID authentication
- ✅ 1,100+ lines of production-ready blockchain code

### Decentralization
- ✅ Every credential has a blockchain-verifiable DID
- ✅ Candidates can take credentials anywhere
- ✅ External verification via API
- ✅ Revocation registry for credential management

### W3C Standards
- ✅ JSON-LD contexts
- ✅ Credential status (RevocationList2021Status)
- ✅ Multiple export formats (JSON-LD, JWT, QR)
- ✅ Full schema validation

### Visual Demo
- ✅ 4 stunning React components
- ✅ Real-time updates with animations
- ✅ Blockchain explorer integration
- ✅ QR code generation

### Fair Hiring
- ✅ Visual proof of PII removal (Zero-Bias Proof)
- ✅ RAG-based evidence (no hallucinations)
- ✅ Cryptographic integrity (tamper-proof)
- ✅ Transparent agent communication

---

## 🐛 Troubleshooting

### "Blockchain components not available"
- Make sure you ran `pip install -r requirements.txt`
- Check: `python -c "import eth_account"`

### "Connection to blockchain failed"
- The system will fall back to local mode
- This is OK for demo! Credentials still work
- To fix: Check your internet connection

### "No messages in Live Dashboard"
- Run a verification pipeline first
- Messages only appear after agent communication
- Try the `/api/verify` endpoint

### React components not showing
- Make sure you added routes in App.jsx
- Check browser console for errors
- Verify backend is running on port 8000

---

## 📊 Success Metrics

Your integration is working if:

- ✅ Blockchain network info shows connected
- ✅ Verification creates 3 W3C credentials
- ✅ Each credential has `proof.signature`
- ✅ Agent messages have DID signatures
- ✅ Trust packet shows blockchain metadata
- ✅ Can export credential as QR code
- ✅ All 4 React components load and display data

---

## 🎊 You're Ready!

You now have:
- Real blockchain DIDs on a live testnet
- W3C-compliant verifiable credentials
- Production-ready cryptographic proofs
- Beautiful visual demos
- Full agent-to-agent messaging

**Go win that hackathon! 🏆**

---

## 📝 Next Steps (Optional)

1. **Add routes** for the 4 new components in `velos-frontend/src/App.jsx`
2. **Style integration** - Make sure components match your design system
3. **Error handling** - Add better error messages
4. **Loading states** - Add skeleton loaders
5. **Testnet ETH** - Make sure you have some for demos

---

## 🆘 Need Help?

Check these files if you need to debug:
- `zynd/blockchain_did.py` - DID management
- `zynd/w3c_credentials.py` - Credential issuance
- `zynd/agent_communication.py` - Messaging
- `agents/orchestrator.py` - Integration
- `server.py` - API endpoints

All error messages print to console with helpful context!
