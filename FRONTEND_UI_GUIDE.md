# 🖥️ Velos AI: Frontend Component & Interface Guide

This document is a comprehensive guide to every aspect of the Velos AI frontend application. It explains the purpose of each interface and the specific React components (`Velos-AI-main/velos-frontend/src/components/`) that power them. Think of this as your visual and structural map of the platform.

---

## 🎨 Design Philosophy & Architecture
The Velos frontend is built using a modern React stack, likely incorporating **Vite** for build speed, **Tailwind CSS** for rich styling, and specialized libraries like **Framer Motion** for animations and **Recharts** for data visualization. 

The aesthetic is designed to feel "web3 native" passing as a premium, secure protocol dashboard—heavy on dark modes, glowing accents (Zynd Protocol orange/blue), and terminal-style data readouts.

---

## 🧭 1. Main Dashboard & Navigation (The Command Center)

### `Dashboard.jsx` & `LiveAgentDashboard.jsx`
- **What it is:** The central hub when a recruiter or admin logs in.
- **Illustration:** Imagine a dark, sleek command center. At the top, glowing counters show "Total Candidates Processed," "Fraud Detected," and "Bias Prevented." Below that, a live feed shows agents currently working on resumes in real-time.
- **Detailed Flow:** `Dashboard.jsx` acts as the primary layout wrapper. `LiveAgentDashboard.jsx` provides the real-time telemetry, likely polling the backend to show which agent (Gatekeeper, Validator, Inquisitor) is currently active on which candidate.

### `GodMode.jsx`
- **What it is:** The ultimate oversight interface for compliance officers.
- **Illustration:** A high-level metrics view. It displays aggregate data across the entire protocol. You'll see line charts showing "Resume Fraud Trends," pie charts mapping "Bias Flags by Category" (Gender, Age, etc.), and network statistics showing how many Zynd Decentralized Identities (DIDs) are currently active.
- **Data Source:** Pulls mock data from `mockGodModeData.js` (for demo purposes) or connects to the backend aggregation endpoints.

---

## 🕵️ 2. The Verification Pipeline (The Core Engine)

This is where the magic happens. The user uploads a resume here and watches the multi-agent system process it.

### `VerificationPipeline.jsx`
- **What it is:** The master component that orchestrates the UI for the 3-step agent validation process.
- **Illustration:** A vertical or horizontal timeline/stepper. As the user clicks "Run," the UI visually moves from Step 1 (Gatekeeper) to Step 2 (Validator) to Step 3 (Inquisitor), with loading spinners and terminal-like text outputting what the AI is currently "thinking."

### `ResumeScreener.jsx`
- **What it is:** The input and initial evaluation interface.
- **Illustration:** A split-screen view. On the left, a text area or drag-and-drop zone for a resume and Job Description. On the right, the immediate output of the "Bias Detector" scanning the Job Description for problematic language.

### `Pipeline3D.jsx` & `AgentGraph.jsx`
- **What it is:** The visual "wow" factor of the pipeline.
- **Illustration:** `AgentGraph.jsx` renders a node-based diagram (likely using a library like React Flow or D3) showing the data path: `Candidate -> Agent 1 -> Agent 2 -> Agent 3 -> Decision`. `Pipeline3D.jsx` presumably adds a three-dimensional flair to this visualization, representing the data moving through the decentralized Zynd network.

### `ZeroBiasProof.jsx`
- **What it is:** The UI layer dedicated to Agent 1 (The Blind Gatekeeper).
- **Illustration:** A "before and after" code-diff view. It shows the original resume with red highlights over PII (Name, Location), and then the output document where those red highlights are replaced with `[REDACTED]`. It visually proves the removal of bias.

---

## ⚖️ 3. Evaluation & Interviewing Interfaces

### `AssessmentGenerator.jsx` & `AIInterviewer.jsx`
- **What it is:** The domain of Agent 3 (The Inquisitor).
- **Illustration:** 
  - `AssessmentGenerator.jsx` shows the AI extracting claims from the resume (e.g., "Built a scalable Redis cache") and formulating a specific question (*"Explain how you handled Redis eviction policies during peak load"*).
  - `AIInterviewer.jsx` is a chat interface. It looks like a standard LLM chat window (like ChatGPT). The candidate types their answer here. The UI then displays the AI's grading (Pass/Fail) based on the technical accuracy of the response.

### `AntiCheat.jsx`
- **What it is:** A companion to the interviewer.
- **Illustration:** Likely a sidebar or hidden module during the interview that warns the candidate if they leave the tab or copy-paste suspiciously large blocks of text, reinforcing the authenticity check.

---

## 📊 4. Candidate Management & Analytics

### `Candidates.jsx` & `Leaderboard.jsx`
- **What it is:** Standard applicant tracking tables.
- **Illustration:** A clean, sortable data table (`Candidates.jsx`). It lists anonymous IDs (`did:zynd:...`), match scores, and a final "Hire/Reject" status. `Leaderboard.jsx` sorts this list by the highest semantic match score calculated by Agent 2, showing the recruiter exactly who to contact first.

### `CompareCandidates.jsx`
- **What it is:** A side-by-side evaluation tool.
- **Illustration:** A split view comparing two candidates' "radar charts" or skill bars. Since names are redacted, the user compares `Candidate A` vs. `Candidate B` purely based on objective metrics (e.g., Python: 90% vs 75%).

### `BatchUpload.jsx`
- **What it is:** Tool for enterprise workflows.
- **Illustration:** A large drag-and-drop area allowing HR to drop 50 resumes at once instead of processing them one by one. Shows a progress bar calculating the batch completion time.

---

## 🔗 5. The Web3 & Trust Layer (Zynd Protocol)

These components are what separate Velos from standard AI tools. They visualize the cryptographic proof.

### `CandidateWallet.jsx`
- **What it is:** The candidate's view of their own data.
- **Illustration:** Looks like a crypto wallet or digital ID pouch. It displays the candidate's DID (`did:zynd:candidate...`) and lists the "Verifiable Credentials" they have earned from the agents (e.g., a green badge for passing the Gatekeeper).

### `AuditTrail.jsx` & `TrustPacketVisualization.jsx`
- **What it is:** The absolute proof of fairness provided to the employer.
- **Illustration:** 
  - `AuditTrail.jsx` is a chronological, immutable log of every action taken by the agents.
  - `TrustPacketVisualization.jsx` is likely a beautifully formatted JSON viewer. It shows the raw, cryptographically signed W3C Verifiable Credential data (HMAC-SHA256 signatures, Issuer DIDs) so compliance teams can verify the math behind the hiring decision.

### `RAGEvidenceExplorer.jsx`
- **What it is:** Shows *why* Agent 2 made its semantic match decision.
- **Illustration:** A deep dive into the vector database. It shows a split screen connecting a sentence in the Job Description (e.g., "Needs cloud experience") to a specific embedded sentence in the resume (e.g., "Deployed apps to AWS ECS"), demonstrating exactly why the candidate got a high match score.

---

## ⚙️ 6. System Configuration

### `Settings.jsx`
- **What it is:** The configuration panel.
- **Illustration:** Toggle switches and sliders. Allows admins to set the strictness of the agents (e.g., changing the Agent 2 pass threshold from 60% to 80%), connect to different LLM models via Groq, or update their Zynd Protocol connection parameters.
