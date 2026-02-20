# Velos: Decentralized Blind Hiring Protocol

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-1.50+-green?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/LangChain-Groq-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Zynd_Protocol-Integrated-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<p align="center">
  <strong>🛡️ Anonymize → 🎯 Match → ❓ Verify → ✅ Decide</strong><br/>
  <em>🔗 Powered by Zynd Protocol | DIDs • Verifiable Credentials • Agent Discovery</em>
</p>

---

## 🎯 Overview

**Velos** is a decentralized multi-agent AI system that eliminates bias AND catches resume fraud in hiring. Built for the **ZYND AIckathon 2025 - Fair Hiring Network** challenge with full **Zynd Protocol integration**.

### The Problem

1. **Bias in AI Hiring**: AI trained on biased data learns to discriminate
2. **Resume Fraud**: 43% of resumes contain false claims (LinkedIn study)
3. **Lack of Trust**: No way to verify AI hiring decisions are fair

### The Solution: Three Agents + Zynd Protocol

| Agent | Role | Zynd Integration |
|-------|------|------------------|
| 🛡️ **Blind Gatekeeper** | PII Removal + Eligibility | Issues `EligibilityCredential` |
| 🎯 **Skill Validator** | Semantic Matching | Issues `SkillMatchCredential` |
| ❓ **Inquisitor** | Authenticity Check | Issues `AuthenticityCredential` |

---

## 🔗 Zynd Protocol Integration

Velos implements the core Zynd Protocol concepts:

### 🆔 Decentralized Identities (DIDs)
```
did:zynd:agent:gatekeeper_abc123
did:zynd:candidate:cand_xyz789
```
- Every agent has a unique DID
- Candidates receive DIDs upon entering the pipeline
- HMAC-SHA256 cryptographic signing

### 📜 Verifiable Credentials
- **W3C Verifiable Credentials format**
- Credentials issued at each pipeline stage
- Cryptographically signed and verifiable
- Full audit trail

### 🌐 Agent Discovery & Trust
- Agent registry with capability declarations
- Trust scores based on verification history
- Authenticated messaging between agents

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- GROQ API key (free at https://console.groq.com)

### Installation

```bash
# 1. Clone/download the project
cd velos

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Set up environment
echo "GROQ_API_KEY=your_key_here" > .env
```

### Run the App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 📊 How It Works

### Pipeline Flow with Zynd Protocol

```
Resume (PDF/Text)
        ↓
   [Candidate DID Created]
        ↓
┌─────────────────────────────────┐
│  🛡️ Agent 1: Blind Gatekeeper  │
│  • DID: did:zynd:agent:gate...  │
│  • Extract experience (LLM)     │
│  • Check eligibility            │
│  • Remove ALL PII               │
│  → Issues: EligibilityCredential│
└─────────────────────────────────┘
        ↓ (Zynd Authenticated Message)
┌─────────────────────────────────┐
│  🎯 Agent 2: Skill Validator    │
│  • DID: did:zynd:agent:valid... │
│  • Verify incoming credential   │
│  • Parse JD requirements        │
│  • Semantic skill matching      │
│  → Issues: SkillMatchCredential │
└─────────────────────────────────┘
        ↓ (If score ≥ 60%)
┌─────────────────────────────────┐
│  ❓ Agent 3: Inquisitor         │
│  • DID: did:zynd:agent:inq...   │
│  • Generate tech questions      │
│  • Candidate answers            │
│  • Evaluate authenticity        │
│  → Issues: AuthenticityCredential│
└─────────────────────────────────┘
        ↓
Final Decision + Verifiable Credentials + Full Audit Trail
```

### Key Features

✅ **Zero-Bias Architecture**: Agents never see names, genders, or colleges  
✅ **Fraud Detection**: Technical questions verify project authenticity  
✅ **Zynd Protocol**: DIDs, Verifiable Credentials, Agent Discovery  
✅ **Bias Detection**: Automatic JD bias analysis and rewriting suggestions  
✅ **Audit Trail**: Every decision is logged and cryptographically signed  
✅ **God Mode Dashboard**: Real-time oversight of all agents  

---

## 📁 Project Structure

```
velos/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── agents/
│   ├── __init__.py
│   ├── agent_1_gatekeeper.py  # PII removal + eligibility
│   ├── agent_2_validator.py   # Skill matching
│   ├── agent_3_inquisitor.py  # Authenticity verification
│   ├── orchestrator.py        # Pipeline coordinator + Zynd integration
│   ├── orchestrator_zynd.py   # Full Zynd orchestrator
│   └── god_mode.py            # Oversight dashboard
├── zynd/                       # 🔗 Zynd Protocol Implementation
│   ├── __init__.py
│   └── protocol.py            # DID, Credentials, Registry, Protocol
├── utils/
│   ├── __init__.py
│   ├── pii_redactor.py        # spaCy + regex PII removal
│   ├── experience_extractor.py # LLM experience extraction
│   └── bias_detector.py       # JD bias detection & rewriting
├── database/
│   ├── __init__.py
│   └── storage.py             # SQLite audit logging
├── mock_data/
│   └── sample_resume.txt      # Demo data
└── tests/
    └── test_pipeline.py       # Integration tests
```

---

## 🔐 Zynd Protocol Details

### Decentralized Identity (DID)

```python
from zynd.protocol import zynd_protocol

# Create identity for an agent
agent_did = zynd_protocol.create_agent_identity(
    agent_name="Blind Gatekeeper",
    agent_type="eligibility_checker",
    capabilities=["pii_redaction", "eligibility_check"]
)
# Returns: did:zynd:agent:gatekeeper_abc123...
```

### Verifiable Credential

```python
# Issue a credential
credential = zynd_protocol.issue_credential(
    issuer_did=agent_did,
    subject_did=candidate_did,
    credential_type="EligibilityCredential",
    claims={
        "eligible": True,
        "experience_years": 3.5,
        "reason": "Meets minimum requirements"
    }
)
```

### Credential Structure (W3C Format)

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "EligibilityCredential"],
  "issuer": "did:zynd:agent:gatekeeper_abc123",
  "issuanceDate": "2025-01-15T10:30:00Z",
  "credentialSubject": {
    "id": "did:zynd:candidate:xyz789",
    "eligible": true,
    "experience_years": 3.5
  },
  "proof": {
    "type": "HmacSha256Signature",
    "created": "2025-01-15T10:30:00Z",
    "verificationMethod": "did:zynd:agent:gatekeeper_abc123#key-1",
    "signature": "..."
  }
}
```

---

## 🔍 Bias Detection

Velos includes automatic bias detection in job descriptions:

### Detected Bias Types

| Type | Examples | Suggested Replacement |
|------|----------|----------------------|
| **Gender** | "rockstar", "ninja" | "high-performer", "expert" |
| **Age** | "digital native", "young team" | "tech-savvy", "dynamic team" |
| **Education** | "Ivy League", "top-tier college" | "strong academic background" |
| **Location** | "native speaker", "local only" | "fluent speaker", "region preferred" |
| **Disability** | "must be able to lift" | "physical requirements may apply" |

### Bias Score

- **0-15**: ✅ Good (minimal bias)
- **15-30**: ⚠️ Fair (some issues)
- **30+**: ❌ High Risk (needs revision)

---

## 🧪 Testing

```bash
# Run all tests
python -m tests.test_pipeline

# Or run individual agent tests
python -m agents.agent_1_gatekeeper
python -m agents.agent_2_validator
python -m agents.agent_3_inquisitor
```

---

## 👁️ God Mode Dashboard

Real-time monitoring of the entire system:

- **KPIs**: Total candidates, pass rates, fraud detected
- **Agent Timeline**: Decisions over time
- **Zynd Network Stats**: DIDs registered, credentials issued
- **Bias Charts**: Flags by category, trend over time
- **Performance Scorecard**: Agent accuracy and speed
- **Red Flags**: System interventions

---

## 🔧 Configuration

### Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Customization

- **Minimum experience**: Set in the UI (default: 2 years)
- **Pass threshold**: Edit `pass_threshold` in agent_2_validator.py (default: 60%)
- **Authenticity threshold**: Edit `authenticity_threshold` in agent_3_inquisitor.py (default: 70%)
- **Bias patterns**: Add to `BiasDetector` class in utils/bias_detector.py

---

## 📈 Demo Flow (5 Minutes)

1. **Upload Resume** (or use sample)
2. **Check Bias Analysis** (expand the section under JD)
3. **Set Job Description** (or use sample)
4. **Click "Run Verification Pipeline"**
5. **Watch agents process**:
   - Agent 1: Eligibility + PII removal → Credential issued
   - Agent 2: Skill matching → Credential issued
   - Agent 3: Questions generated
6. **Answer verification questions**
7. **See final verdict + Verifiable Credentials**
8. **Check Results Dashboard for all credentials**
9. **Explore God Mode dashboard**
10. **Check Zynd Network Stats in sidebar**

---

## 🏆 Why Velos Wins

### Technical Excellence
- ✅ **Full Zynd Protocol Implementation**: DIDs, Verifiable Credentials, Agent Registry
- ✅ **W3C Standard Compliance**: Credentials follow Verifiable Credentials Data Model
- ✅ **Cryptographic Signing**: HMAC-SHA256 signatures on all credentials

### Problem Solving
- ✅ **Dual Problem Solution**: Bias AND fraud detection together
- ✅ **Explainable AI**: Full audit trail for every decision
- ✅ **Legally Defensible**: GDPR-friendly PII handling

### Innovation
- ✅ **Bias Detection Engine**: 50+ bias patterns with suggestions
- ✅ **Multi-Agent Architecture**: Clear authority boundaries
- ✅ **God Mode Oversight**: Human-in-the-loop monitoring

### Alignment with Zynd Values
- ✅ **Decentralized**: No central authority controlling decisions
- ✅ **Transparent**: Every step is auditable
- ✅ **Fair**: Designed to eliminate, not embed, bias

---

## 🛣️ Roadmap

- [ ] Blockchain-based credential storage (IPFS/Ethereum)
- [ ] Full SSI wallet integration
- [ ] Multi-language bias detection
- [ ] ATS system integrations (Greenhouse, Lever)
- [ ] Enterprise licensing
- [ ] Real-time bias monitoring alerts
- [ ] Candidate credential portability
- [ ] Video interview integration

---

## 📄 License

MIT License - see LICENSE file

---

## 👥 Authors

Built for **ZYND AIckathon 2025** - Fair Hiring Network Challenge

---

<p align="center">
  <strong>Velos: Fair hiring isn't about replacing humans—it's about removing bias so humans make better decisions.</strong>
</p>

<p align="center">
  🔗 <em>Powered by Zynd Protocol</em>
</p>
