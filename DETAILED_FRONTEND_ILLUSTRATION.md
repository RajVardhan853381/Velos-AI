# 🎨 Velos AI: Exhaustive Frontend Architecture & Interface Illustration

This document serves as the absolute, comprehensive guide to **every single interface and component** in the Velos AI frontend application (`velos-frontend/src/components`). 

It provides visual wireframe illustrations, exact functionality descriptions, and explains how the 20 distinct React components map to the user experience.

---

## 🧭 Global Shell & Navigation (`App.jsx`)

The entire application is wrapped in a modern, web3-styled glassmorphic shell.
- **Visuals:** An `AnimatedBackground` component renders floating purple and blue orbs behind an acrylic blur (`backdropFilter: 'blur(24px)'`).
- **Sidebar:** A left-aligned navigation pane using `GlassNavItem` components with Lucide icons (Dashboard, Verify, AI Screener, AI Interviewer, Anti-Cheat, Blockchain Proof, God Mode).

---

## 📊 1. Command Center & Analytics Interfaces

### `Dashboard.jsx` (Route: `/dashboard`)
**Purpose:** The central landing page providing an aggregate view of system performance.
- **Visual Layout:**
  - **Top Row (Metrics):** Uses the `StatCard` component. Four glowing cards displaying: Total Candidates (`Users` icon), Average Match Score (`TrendingUp` icon), Resumes Screened (`Shield` icon), and Fraud Blocked (`AlertTriangle` icon).
  - **Middle Row (Charts):** Uses `Recharts`.
    - Left: An `AreaChart` showing "Processing Volume" over time with a smooth gradient fill.
    - Right: A `BarChart` breaking down "Bias Flags by Category" (Gender, Age, Location).
  - **Bottom Row:** A live feed table of the most recent candidates processed, showing their DID, Status, and Timestamp.

### `GodMode.jsx` (Route: `/godmode`)
**Purpose:** Ultimate oversight for compliance officers. Shows holistic system integrity and Zynd network health.
- **Visual Layout:**
  - **Header:** "God Mode Analytics" with a pulsing red/orange `Zap` icon.
  - **Grid:** A 3x2 grid of dense data visualizations.
  - Includes anomaly detection flags, agent intervention rates, and system latency metrics. Shows raw statistical logs pulled from `mockGodModeData.js` or the `/api/v1/dashboard` endpoint.

### `LiveAgentDashboard.jsx` (Route: `/live-agents`)
**Purpose:** Real-time telemetry of the AI agents currently executing tasks.
- **Visual Layout:**
  - Displays three distinct animated panes, one for each agent (Gatekeeper, Validator, Inquisitor).
  - Each pane has a pulsing "Status: ACTIVE/IDLE" indicator.
  - Below is a scrolling, terminal-style log output (`font-mono text-green-400 bg-black`) showing the exact operations the agents are performing byte-by-byte.

---

## 🛠️ 2. The Verification Pipeline (Core Workflow)

### `VerificationPipeline.jsx` (Route: `/verify`)
**Purpose:** The master component that orchestrates the 3-step agent validation process.
- **Visual Layout:**
  - **Upper Section:** A stepper UI (Step 1: Gatekeeper → Step 2: Validator → Step 3: Inquisitor).
  - **Drag & Drop Zone:** Uses `framer-motion` for a bouncy drop zone where users upload a resume PDF/DOCX.
  - **Action Area:** Job Description text area and numerical thresholds (e.g., Minimum Experience slider).
  - **Execution State:** Upon clicking "Run Analysis," the UI hides the inputs and renders the `Pipeline3D` or `AgentGraph` models.

### `Pipeline3D.jsx` & `AgentGraph.jsx`
- **Purpose:** Visual "wow" elements demonstrating the data moving through the multi-agent system.
- **Pipeline3D:** Uses `@react-three/fiber` to render a 3D isometric view of data packets (cubes) moving between agent nodes (spheres).
- **AgentGraph:** A 2D node-based diagram (`react-flow-renderer` or similar) showing the explicit data contracts passing from Agent 1 to Agent 3.

---

## 🔍 3. Pre-Screening & Anti-Cheat Subsystems

### `ResumeScreener.jsx` (Route: `/screener`)
**Purpose:** Manual override mapping for recruiters to inspect bias removal.
- **Visual Layout:**
  - A split-pane view. 
  - **Left Pane:** The original document input.
  - **Right Pane:** Real-time bias analysis. Flags problematic words in red and opens tooltip popovers with suggested inclusive alternatives.

### `AntiCheat.jsx` (Route: `/anti-cheat`)
**Purpose:** Security interface monitoring the candidate's browser behavior during testing.
- **Visual Layout:**
  - A dense security dashboard with warning indicators (`ShieldAlert` icons).
  - Shows metrics like: "Tab Switches Detected," "Copy/Paste Events," "Typing Cadence Anomalies," and "Browser Focus Lost."
  - Displays a timeline graph where red spikes indicate highly probable cheating moments.

---

## 🎙️ 4. AI Interviewing Interfaces

### `AssessmentGenerator.jsx` (Route: `/assessment`)
**Purpose:** The interface where Agent 3 decides *what* to ask the candidate.
- **Visual Layout:**
  - Shows a list of extracted claims from the resume (e.g., *Claim: "Reduced AWS costs by 40%"*).
  - Next to each claim, an animated generation icon spins, expanding into a highly specific technical question targeted precisely at verifying that exact claim.

### `AIInterviewer.jsx` (Route: `/interviewer`)
**Purpose:** The candidate-facing chat interface for the technical interview.
- **Visual Layout:**
  - **Top:** A 3D Avatar (using `@react-three/fiber` and custom `AvatarHead` meshes) that animates its jaw when speaking (via browser Speech API).
  - **Middle:** A clean chat transcript box showing both the AI's questions and the user responses.
  - **Bottom:** A text input with a `Send` icon and a microphone button for speech-to-text.
  - **Floating Panel:** A real-time scoring badge (`ScoreBadge` component) that turns green, yellow, or red based on the technical accuracy of the candidate's active response.

---

## 👥 5. Applicant Tracking & Comparisons

### `Candidates.jsx` (Route: `/candidates`)
**Purpose:** The primary applicant tracking table.
- **Visual Layout:** A sortable data grid. Columns include: Candidate DID, Overall Score, Gatekeeper Status, Validator Score, Interview Result. Clicking a row expands into a detailed pane showing their full journey.

### `Leaderboard.jsx` (Route: `/leaderboard`)
**Purpose:** Gamified hiring view to instantly see the top percentile of applicants.
- **Visual Layout:**
  - Podiums for the Top 3 candidates (represented by DIDs) with glowing badges (`#1 Match`).
  - Below, a list of runners-up sorted strictly by their semantic match score and lack of fraud flags.

### `CompareCandidates.jsx` (Route: `/compare`)
**Purpose:** Side-by-side objective evaluation tool.
- **Visual Layout:**
  - Two dropdowns to select candidate DIDs.
  - Renders mirrored "Radar/Spider Charts" overlaying Candidate A's skills vs. Candidate B's skills.
  - Below the charts, aligned text blocks compare their verified credentials side-by-side without any identifying information.

### `BatchUpload.jsx` (Route: `/batch-upload`)
**Purpose:** Enterprise workflow for bulk processing.
- **Visual Layout:** 
  - A massive dropzone. When 50 files are dropped, it transforms into a list.
  - Each list item has an individual progress bar (`motion.div` width transitions).
  - A global summary ring chart tracks overall completion percentage.

---

## 🔗 6. Web3, Trust & Cryptography Layers

### `CandidateWallet.jsx` (Route: `/wallet`)
**Purpose:** The candidate's personal view of their decentralized identity.
- **Visual Layout:** Styled like a translucent ID card. Displays a QR code representing their Zynd DID. Below it, a grid of "Verifiable Credentials" (Eligibility, Match, Authenticity) displayed as digital badges with cryptographic hash strings below them.

### `TrustPacketVisualization.jsx` (Route: `/blockchain`)
**Purpose:** Deep technical proof for auditors showing the cryptographic signatures.
- **Visual Layout:** 
  - A dark, code-editor style interface (`bg-gray-900 font-mono`).
  - Displays the raw W3C JSON payload.
  - Specialized highlighting isolates the `"proof": { "signature": "..." }` block. A green checkmark floats next to the signature, visually indicating that the HMCA-SHA256 signature mathematically matches the issuer DID.

### `ZeroBiasProof.jsx` (Route: `/bias-proof`)
**Purpose:** The definitive visual proof showing exactly how the resume was mutated by Agent 1.
- **Visual Layout:** 
  - A split-screen diff viewer (like GitHub PRs).
  - Left side shows the original text with PII highlighted in red.
  - Right side shows the resulting text with `[REDACTED]` blocks highlighted in bright green, mathematically proving no gender or racial identifiers passed the gate.

### `RAGEvidenceExplorer.jsx` (Route: `/evidence`)
**Purpose:** "Explainable AI" interface to defend *why* a candidate got a high or low score.
- **Visual Layout:** 
  - Left column: The required skill paragraph from the Job Description.
  - Right column: The extracted history from the candidate.
  - Connecting lines (SVG paths) link the JD requirement to the exact chunk retrieved from the ChromaDB vector store, showing the similarity cosine distance (e.g., `Cosine Similarity: 0.89`).

---

## ⚙️ 7. System Administration

### `Settings.jsx` (Route: `/settings`)
**Purpose:** The control panel for the protocol.
- **Visual Layout:** 
  - **Threshold Sliders:** Draggable ranges to set strictness for "Skill Validator Pass Mark" (e.g., 60%) and "Authenticity Pass Mark" (e.g., 70%).
  - **API Keys:** Secure password-masked inputs for Groq API keys and Zynd Protocol connection URLs.
  - **Appearance:** Toggles for Dark/Light mode and Animation Intensity.

---

### Conclusion
This document covers every single React component and route within the Velos frontend architecture. Each interface is carefully constructed to adhere to the core philosophy: **Decentralized, mathematically verifiable, and entirely free of human bias.**
