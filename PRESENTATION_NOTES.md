# 🚀 Velos AI: Presenter's Guide & Overview

**Mission:** Eliminate bias AND catch resume fraud in hiring through a decentralized, multi-agent AI system. Built for the ZYND AIckathon 2025.

---

## 🛑 The Core Problem
1. **Unconscious Bias:** AI trained on historical data often inherits societal biases regarding gender, age, and education.
2. **Rampant Resume Fraud:** Studies show up to 43% of resumes contain exaggerated or false claims.
3. **Lack of Trust / "Black Box AI":** Candidates and recruiters cannot verify how AI models arrive at hiring decisions.

---

## 💡 The Solution: Velos Architecture
Velos is a pipeline of three specialized AI agents that process applicants sequentially, communicating securely via the **Zynd Protocol**. 

1. 🛡️ **Blind Gatekeeper (Agent 1):** 
   - **Role:** Redacts ALL Personally Identifiable Information (PII) like names, gender, colleges, and locations to ensure zero-bias evaluation.
   - **Action:** Checks baseline eligibility and issues an `EligibilityCredential`.
2. 🎯 **Skill Validator (Agent 2):** 
   - **Role:** Performs deep semantic matching between the anonymized resume and the Job Description.
   - **Action:** Uses vector databases to calculate a skill match score. Issues a `SkillMatchCredential` if the threshold (e.g., 60%) is met.
3. ❓ **Inquisitor (Agent 3):** 
   - **Role:** Generates dynamic, highly technical questions based on claimed experience to catch resume fraud.
   - **Action:** Evaluates candidate answers for authenticity and issues an `AuthenticityCredential`.

---

## 🔗 The Zynd Protocol Integration (The Differentiator)
Velos isn't just an AI app; it's a decentralized web3 hiring protocol. Every action is verifiable and trustworthy because of Zynd:

- **Decentralized Identities (DIDs):** Every agent (e.g., `did:zynd:agent:gatekeeper_abc123`) and every candidate receives a unique crypto-identity.
- **Verifiable Credentials (W3C Standard):** Outputs from each agent are cryptographically signed credentials (`EligibilityCredential`, `SkillMatchCredential`, `AuthenticityCredential`).
- **Agent Discovery:** Agents natively discover capabilities and securely hand off execution to one another without a centralized middleman.

---

## 🛠️ How It Is Built (Tech Stack)
- **Frontend Core:** Streamlit (v1.50+) for quick, reactive dashboards.
- **Backend APIs:** Python 3.9+ with FastAPI powering the core REST interfaces.
- **AI/LLM Engine:** LangChain & GROQ (`llama-3.3-70b-versatile` running at lightning speeds). 
- **Retrieval Augmented Generation (RAG):** ChromaDB vector store natively embedded for semantic matching.
- **Protocol Layer:** `zyndai-agent` SDK (v0.1.5 compatibility layer) handling DID creation and HMAC-SHA256 signature verification.
- **Security Hardening:** Rate limiting (via SlowAPI), input length sanitization, CORS whitelisting, and strict `.env` secrets.
- **Persistence:** SQLite for immutable audit logs (`velos_state.db`).

---

## ⭐ Standout Platform Features
- **Job Description Bias Detector:** Automatically scans recruiter inputs identifying risky language ("rockstar", "native speaker") and suggests inclusive alternatives. 
- **God Mode Dashboard:** A complete oversight dashboard showing KPIs, real-time agent timelines, anomaly detection flags, and total capabilities.
- **Defensible Audit Trails:** Because of W3C credentials, every rejection or approval is backed by a verifiable proof, protecting the company legally and ethically.

---

## ⏱️ Recommended Demo Flow (5-Minute Strategy)
1. **Upload Resume:** Start by dropping a sample resume into the platform.
2. **Review Bias Scanner:** Scroll down to the Job Description section. Specifically expand the "Bias Analysis" to show the tool detecting and suggesting corrections for exclusive language.
3. **Run Pipeline:** Click "Run Verification Pipeline" and visually point out the step-by-step progress of the agents.
   - Highlight Agent 1 stripping names and checking eligibility.
   - Highlight Agent 2 calculating skill thresholds (`Score >= 60%`).
   - Highlight Agent 3 issuing questions based on claimed past projects.
4. **Candidate Interaction:** Type in an answer to the technical question to show how the Inquisitor catches authenticity issues.
5. **The Reveal:** Show the final decision, and importantly, show the **Verifiable Credentials JSON view** validating the Zynd integration.
6. **God Mode Tour:** Finish by panning to the God Mode statistics dashboard, noting the global system overview and agent credibility scores.

---

**Closing Hook:** *"Velos proves that fair hiring isn't about removing human decision-makers; it's about removing black-box bias so humans make verified, trustworthy decisions."*
