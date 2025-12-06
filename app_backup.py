"""
Velos: Decentralized Blind Hiring Protocol
Main Streamlit Application with Zynd Protocol Integration

Run with: streamlit run app.py
"""

import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import Velos components
from agents.orchestrator import VelosOrchestrator
from agents.god_mode import GodModeDashboard
from database.storage import AuditLog

# Try to import bias detector
try:
    from utils.bias_detector import bias_detector
    BIAS_DETECTOR_AVAILABLE = True
except ImportError:
    BIAS_DETECTOR_AVAILABLE = False

# Try to import PDF reader
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("⚠️ pypdf not installed. PDF upload disabled.")


# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Velos: Blind Hiring",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============ CUSTOM CSS ============
st.markdown("""
<style>
    /* Dark theme enhancements */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%);
    }
    
    /* Header gradient */
    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    /* Status badges */
    .status-pass {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .status-fail {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Agent cards */
    .agent-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Progress indicators */
    .progress-step {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin: 0 5px;
    }
    
    .progress-active {
        background: #667eea;
        color: white;
    }
    
    .progress-complete {
        background: #38ef7d;
        color: white;
    }
    
    .progress-pending {
        background: #4a4a5a;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)


# ============ SESSION STATE ============
def init_session_state():
    """Initialize session state variables"""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = VelosOrchestrator()
    
    if "candidate_data" not in st.session_state:
        st.session_state.candidate_data = None
    
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = 0
    
    if "answers_submitted" not in st.session_state:
        st.session_state.answers_submitted = False

init_session_state()


# ============ HEADER ============
def render_header():
    """Render main header"""
    st.markdown("""
    <div class="header-gradient">
        <h1 style="color: white; margin: 0; font-size: 42px;">⚖️ Velos</h1>
        <p style="color: #e0e0e0; margin: 8px 0 0 0; font-size: 18px;">
            Decentralized Blind Hiring Protocol
        </p>
        <p style="color: #b0b0ff; margin: 10px 0 0 0; font-size: 14px;">
            🛡️ Anonymize → 🎯 Match → ❓ Verify → ✅ Decide
        </p>
        <p style="color: #90f090; margin: 8px 0 0 0; font-size: 12px;">
            🔗 Powered by Zynd Protocol | DIDs • Verifiable Credentials • Agent Discovery
        </p>
    </div>
    """, unsafe_allow_html=True)

render_header()


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🏆 About TrustFlow")
    st.markdown("""
    TrustFlow solves two critical hiring problems:
    
    **1. Bias in AI Hiring**
    → Anonymize data before evaluation
    
    **2. Resume Fraud**
    → Verify authenticity via technical questions
    
    ---
    
    **Three Agents Work Together:**
    
    🛡️ **Agent 1: Blind Gatekeeper**
    - PII removal + eligibility check
    
    🎯 **Agent 2: Skill Validator**  
    - Semantic skill matching
    
    ❓ **Agent 3: Inquisitor**
    - Authenticity verification
    """)
    
    st.divider()
    
    # ============ ZYND PROTOCOL STATUS ============
    st.markdown("### 🔗 Zynd Protocol Network")
    
    try:
        network_stats = st.session_state.orchestrator.get_network_stats()
        if network_stats:
            st.success("🟢 Connected to Zynd Network")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Agents", network_stats.get("registered_agents", 0))
            with col2:
                st.metric("Messages", network_stats.get("total_messages", 0))
            
            st.metric("Credentials Issued", network_stats.get("total_credentials", 0))
            
            with st.expander("🤖 Agent DIDs"):
                trust_scores = st.session_state.orchestrator.get_agent_trust_scores()
                for agent_name, score in trust_scores.items():
                    st.markdown(f"**{agent_name}**: Trust {score}%")
        else:
            st.warning("⚠️ Zynd Protocol Offline")
    except Exception as e:
        st.info("🔄 Zynd Protocol initializing...")
    
    st.divider()
    
    st.markdown("### ⚙️ Settings")
    
    # API Key status
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        st.success("✅ GROQ API Connected")
    else:
        st.error("❌ GROQ API Key Missing")
        st.markdown("Add to `.env`: `GROQ_API_KEY=your_key`")
    
    st.divider()
    
    st.markdown("### 📊 Quick Stats")
    stats = st.session_state.orchestrator.get_pipeline_stats()
    st.metric("Total Processed", stats.get('total_candidates', 0))
    st.metric("Approved", stats.get('total_approved', 0))


# ============ SAMPLE DATA ============
SAMPLE_RESUME = """
PROFESSIONAL SUMMARY
Senior AI/ML Engineer with 3.5 years of experience building production LLM systems.
Expertise in Python, RAG architectures, and cloud deployment.

WORK EXPERIENCE

Senior AI Engineer | TechCorp Inc. (2022-2025)
- Built RAG systems using LangChain and Pinecone for document Q&A
- Developed production LLM pipelines serving 10K+ daily requests
- Reduced inference latency by 40% through caching and optimization
- Led team of 3 engineers on GenAI initiatives
- Tech Stack: Python, FastAPI, AWS, Docker, PostgreSQL

AI Developer | StartupXYZ (2020-2022)
- Created NLP pipelines for document classification and extraction
- Implemented transformer-based models for text analysis
- Built: Real-time sentiment analysis system processing 1M+ tweets/day
- Tech Stack: Python, PyTorch, GCP, Redis

SKILLS
Python, FastAPI, LangChain, RAG, LLMs, Transformers, AWS, GCP, Docker, Kubernetes, 
PostgreSQL, Redis, Git, CI/CD, Agile

PROJECTS
1. Document Q&A System: Built RAG system processing 500-page PDFs with 95% accuracy
2. LLM Fine-tuning Pipeline: Automated fine-tuning workflow reducing training time by 60%
3. Bias Detection Tool: ML model detecting bias in hiring systems (this project!)

CERTIFICATIONS
- AWS Certified Solutions Architect
- Google Cloud Professional ML Engineer
"""

SAMPLE_JD = """
Senior AI Engineer

We're building the future of AI-powered applications and looking for a talented 
AI Engineer to join our team.

Requirements:
- 2+ years of professional AI/ML development experience
- Strong proficiency in Python programming
- Experience with LLMs and RAG systems
- Familiarity with FastAPI, Django, or similar frameworks
- AWS or GCP cloud experience
- Strong SQL and database skills
- Experience with Docker and containerization

Nice to have:
- LangChain or similar LLM frameworks
- Production ML deployment experience
- Kubernetes experience
- Open source contributions

We offer competitive compensation, remote work, and equity.
"""


# ============ MAIN TABS ============
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Verify Candidate",
    "📊 Results Dashboard", 
    "📋 Audit Trail",
    "👁️ God Mode"
])


# ============ TAB 1: VERIFICATION ============
with tab1:
    st.header("Candidate Verification Pipeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Resume Input")
        
        input_method = st.radio(
            "Input Method",
            ["📝 Paste Text", "📁 Upload PDF", "📋 Use Sample"],
            horizontal=True
        )
        
        resume_text = ""
        
        if input_method == "📝 Paste Text":
            resume_text = st.text_area(
                "Paste Resume Text",
                height=300,
                placeholder="Paste the candidate's resume text here..."
            )
        
        elif input_method == "📁 Upload PDF":
            if PDF_SUPPORT:
                uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                if uploaded_file:
                    try:
                        pdf_reader = PdfReader(uploaded_file)
                        resume_text = ""
                        for page in pdf_reader.pages:
                            resume_text += page.extract_text() or ""
                        st.success(f"✅ Extracted {len(resume_text)} characters from PDF")
                    except Exception as e:
                        st.error(f"Error reading PDF: {e}")
            else:
                st.warning("PDF support not available. Install pypdf: `pip install pypdf`")
        
        else:  # Use Sample
            resume_text = SAMPLE_RESUME
            st.info("📋 Using sample resume for demo")
            with st.expander("View Sample Resume"):
                st.text(resume_text)
        
        # Minimum experience
        min_exp = st.number_input(
            "Minimum Experience Required (years)",
            min_value=0,
            max_value=20,
            value=2
        )
    
    with col2:
        st.subheader("💼 Job Description")
        
        use_sample_jd = st.checkbox("Use sample JD", value=True)
        
        if use_sample_jd:
            job_desc = SAMPLE_JD
            with st.expander("View Job Description"):
                st.text(job_desc)
        else:
            job_desc = st.text_area(
                "Enter Job Description",
                height=300,
                placeholder="Paste the job description here..."
            )
        
        # ============ BIAS ANALYSIS ============
        if BIAS_DETECTOR_AVAILABLE and job_desc:
            with st.expander("🔍 Bias Analysis (Zynd Protocol)", expanded=False):
                bias_result = bias_detector.calculate_bias_score(job_desc)
                bias_score = bias_result.get("score", 0)
                
                # Color-coded score (0-100 scale, lower is better)
                if bias_score < 15:
                    st.success(f"✅ Bias Score: {bias_score}/100 ({bias_result.get('rating', 'Good')})")
                elif bias_score < 30:
                    st.warning(f"⚠️ Bias Score: {bias_score}/100 ({bias_result.get('rating', 'Fair')})")
                else:
                    st.error(f"❌ Bias Score: {bias_score}/100 ({bias_result.get('rating', 'High')})")
                
                # Show detected issues
                flags = bias_result.get("flags", [])
                if flags:
                    st.markdown("**Detected Issues:**")
                    for flag in flags[:5]:  # Show top 5
                        bias_type = flag.bias_type.value
                        term = flag.original_text
                        suggestion = flag.suggested_replacement
                        st.markdown(f"- `{term}` → *{suggestion}* ({bias_type})")
                else:
                    st.markdown("✅ No bias patterns detected!")
    
    st.divider()
    
    # ============ RUN PIPELINE BUTTON ============
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Run Verification Pipeline", use_container_width=True, type="primary"):
            if not resume_text:
                st.error("❌ Please provide a resume")
            elif not job_desc:
                st.error("❌ Please provide a job description")
            else:
                # Reset state
                st.session_state.answers_submitted = False
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Run pipeline
                with st.spinner(""):
                    status_text.text("🛡️ Agent 1: Checking eligibility & removing PII...")
                    progress_bar.progress(15)
                    
                    result = st.session_state.orchestrator.run_verification_pipeline(
                        resume_text,
                        job_desc,
                        min_years=min_exp
                    )
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Pipeline complete!")
                    time.sleep(0.5)
                    
                    st.session_state.candidate_data = result
                    st.session_state.current_stage = 1
                
                progress_bar.empty()
                status_text.empty()
                st.rerun()
    
    # ============ DISPLAY RESULTS ============
    if st.session_state.candidate_data:
        data = st.session_state.candidate_data
        
        st.divider()
        st.subheader("📊 Pipeline Results")
        
        # Agent Status Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_color = "🟢" if data.get("agent_1_status") == "PASS" else "🔴"
            st.markdown(f"""
            <div class="agent-card">
                <h4>{status_color} Agent 1: Gatekeeper</h4>
                <p><strong>Status:</strong> {data.get('agent_1_status', 'N/A')}</p>
                <p><strong>Experience:</strong> {data.get('years_exp', 0):.1f} years</p>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Experience Found", f"{data.get('years_exp', 0):.1f} years")
        
        with col2:
            if data.get("agent_2_status"):
                status_color = "🟢" if data.get("agent_2_status") == "PASS" else "🔴"
                st.markdown(f"""
                <div class="agent-card">
                    <h4>{status_color} Agent 2: Validator</h4>
                    <p><strong>Status:</strong> {data.get('agent_2_status', 'N/A')}</p>
                    <p><strong>Match Score:</strong> {data.get('agent_2_score', 0)}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Skill Match", f"{data.get('agent_2_score', 0)}%")
            else:
                st.info("⏳ Waiting for Agent 1")
        
        with col3:
            if data.get("agent_3_authenticity"):
                status_color = "🟢" if data.get("agent_3_status") == "PASS" else "🔴"
                st.markdown(f"""
                <div class="agent-card">
                    <h4>{status_color} Agent 3: Inquisitor</h4>
                    <p><strong>Status:</strong> {data.get('agent_3_status', 'N/A')}</p>
                    <p><strong>Authenticity:</strong> {data.get('agent_3_authenticity', 0):.0f}%</p>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Authenticity", f"{data.get('agent_3_authenticity', 0):.0f}%")
            elif data.get("final_status") == "QUESTIONS_PENDING":
                st.info("❓ Awaiting candidate answers")
            else:
                st.info("⏳ Waiting for Agent 2")
        
        # Show anonymized data expander
        if data.get("agent_1_status") == "PASS":
            with st.expander("🔍 View Anonymized Data (What Agent 2 Sees)", expanded=False):
                agent1_data = data.get("pipeline_stages", {}).get("agent_1", {})
                
                st.markdown("**This is the CLEAN DATA passed to Agent 2:**")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Skills Detected:**")
                    skills = agent1_data.get("clean_data", {}).get("skills", [])
                    st.write(", ".join(skills) if skills else "None found")
                
                with col2:
                    st.markdown("**Projects Found:**")
                    projects = agent1_data.get("clean_data", {}).get("projects", [])
                    for p in projects[:5]:
                        st.write(f"• {p[:80]}...")
                
                st.markdown("---")
                st.markdown("**Redacted Text Preview:**")
                redacted = agent1_data.get("clean_data_full_text", "")[:500]
                st.text(redacted + "..." if len(redacted) == 500 else redacted)
                
                # Redaction stats
                stats = agent1_data.get("redaction_stats", {})
                if stats:
                    st.markdown("**PII Redaction Stats:**")
                    stat_str = " | ".join([f"{k}: {v}" for k, v in stats.items() if v > 0])
                    st.caption(stat_str if stat_str else "No PII found")
        
        # ============ Q&A SECTION ============
        if data.get("final_status") == "QUESTIONS_PENDING" and not st.session_state.answers_submitted:
            st.divider()
            st.subheader("❓ Verification Questions")
            st.markdown("Agent 3 has generated technical questions. Please answer them:")
            
            questions = data.get("verification_questions", [])
            qa_pairs = []
            
            for i, question in enumerate(questions, 1):
                st.markdown(f"**Q{i}: {question}**")
                answer = st.text_area(
                    f"Your answer to Q{i}",
                    key=f"answer_{i}",
                    height=120,
                    placeholder="Type your detailed answer here..."
                )
                qa_pairs.append({"question": question, "answer": answer})
            
            if st.button("✅ Submit Answers for Evaluation", use_container_width=True, type="primary"):
                if all(qa["answer"].strip() for qa in qa_pairs):
                    with st.spinner("❓ Agent 3: Evaluating authenticity..."):
                        final_result = st.session_state.orchestrator.evaluate_candidate_answers(qa_pairs)
                        
                        # Update session data
                        st.session_state.candidate_data.update(final_result)
                        st.session_state.answers_submitted = True
                    
                    st.rerun()
                else:
                    st.error("❌ Please answer all questions before submitting")
        
        # ============ FINAL DECISION ============
        if "final_result" in st.session_state.candidate_data or st.session_state.answers_submitted:
            st.divider()
            
            final_status = data.get("final_status", "")
            
            if "APPROVED" in final_status:
                st.success(f"## ✅ {final_status}")
                st.balloons()
            elif "REJECTED" in final_status or "FAIL" in final_status:
                st.error(f"## ❌ {final_status}")
            
            if data.get("final_reason"):
                st.write(f"**Reason:** {data.get('final_reason')}")
            
            if data.get("red_flags"):
                st.warning(f"**Red Flags:** {', '.join(data.get('red_flags', []))}")


# ============ TAB 2: RESULTS DASHBOARD ============
with tab2:
    st.header("📊 Results Dashboard")
    
    if st.session_state.candidate_data:
        data = st.session_state.candidate_data
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🆔 Candidate ID", data.get("candidate_id", "N/A")[:12] + "...")
        
        with col2:
            st.metric("📅 Experience", f"{data.get('years_exp', 0):.1f} years")
        
        with col3:
            st.metric("🎯 Skill Match", f"{data.get('agent_2_score', 0)}%")
        
        with col4:
            auth = data.get("agent_3_authenticity", 0)
            st.metric("✅ Authenticity", f"{auth:.0f}%" if auth else "Pending")
        
        st.divider()
        
        # ============ ZYND VERIFIABLE CREDENTIALS ============
        st.subheader("🔐 Verifiable Credentials (Zynd Protocol)")
        
        try:
            credentials = st.session_state.orchestrator.get_candidate_credentials(
                data.get("candidate_id")
            )
            
            if credentials:
                for cred in credentials:
                    cred_type = cred.get("type", ["Unknown"])[-1] if isinstance(cred.get("type"), list) else cred.get("type", "Unknown")
                    status_icon = "🟢" if cred.get("proof") else "🟡"
                    
                    with st.expander(f"{status_icon} {cred_type}", expanded=False):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Issuer:** `{cred.get('issuer', 'Unknown')[:30]}...`")
                            st.markdown(f"**Subject:** `{cred.get('credentialSubject', {}).get('id', 'N/A')[:30]}...`")
                            st.markdown(f"**Issued:** {cred.get('issuanceDate', 'N/A')[:10]}")
                        
                        with col2:
                            if cred.get("proof"):
                                st.success("✅ Signed")
                                st.caption(f"Type: {cred['proof'].get('type', 'N/A')}")
                            else:
                                st.warning("⚠️ Unsigned")
                        
                        # Show credential claims
                        subject = cred.get("credentialSubject", {})
                        if subject:
                            st.markdown("**Claims:**")
                            for key, value in subject.items():
                                if key != "id":
                                    st.markdown(f"- {key}: `{value}`")
                        
                        # Raw JSON
                        with st.expander("📄 View Raw JSON"):
                            st.json(cred)
            else:
                st.info("📭 No credentials issued yet. Run the verification pipeline to generate credentials.")
        except Exception as e:
            st.info(f"🔄 Zynd Protocol loading... ({str(e)[:50]})")
        
        st.divider()
        
        # Stage breakdown
        st.subheader("Pipeline Stages")
        
        stages = data.get("pipeline_stages", {})
        for stage_name, stage_data in stages.items():
            if "questions" not in stage_name:
                status = stage_data.get("status", "UNKNOWN")
                reason = stage_data.get("reason", "")
                
                if status == "PASS":
                    st.success(f"✅ **{stage_name.upper()}** - {reason}")
                elif status == "FAIL":
                    st.error(f"❌ **{stage_name.upper()}** - {reason}")
                else:
                    st.info(f"⏳ **{stage_name.upper()}** - {status}")
        
        # Show Candidate DID if available
        if data.get("candidate_did"):
            st.divider()
            st.subheader("🆔 Decentralized Identity")
            st.code(data.get("candidate_did"), language="text")
    else:
        st.info("👆 Run verification pipeline to see results here")


# ============ TAB 3: AUDIT TRAIL ============
with tab3:
    st.header("📋 Audit Trail")
    
    if st.session_state.candidate_data:
        candidate_id = st.session_state.candidate_data.get("candidate_id")
        
        if candidate_id:
            audit_trail = st.session_state.orchestrator.get_full_audit_trail(candidate_id)
            
            if audit_trail:
                for entry in audit_trail:
                    with st.expander(
                        f"📌 {entry.get('agent_name', 'Unknown')} - {entry.get('action', '')} @ {entry.get('timestamp', '')[:19]}"
                    ):
                        st.json(entry.get('details', '{}'))
            else:
                st.info("No audit entries found for this candidate")
        else:
            st.warning("No candidate ID available")
    else:
        st.info("👆 Run verification pipeline to see audit trail here")


# ============ TAB 4: GOD MODE ============
with tab4:
    # Get audit DB from orchestrator
    audit_db = st.session_state.orchestrator.audit_db
    
    # Render God Mode dashboard
    god_mode = GodModeDashboard(audit_db)
    god_mode.render()


# ============ FOOTER ============
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>⚖️ Velos</strong> - Decentralized Blind Hiring Protocol</p>
    <p style="font-size: 14px; color: #9090ff;">
        🔗 Powered by <strong>Zynd Protocol</strong> | 
        🛡️ Decentralized Identities | 
        📜 Verifiable Credentials
    </p>
    <p style="font-size: 12px;">Built for ZYND AIckathon 2025 | Fair Hiring Network Challenge</p>
    <p style="font-size: 11px; color: #888;">
        DID-based Agent Authentication • W3C Verifiable Credentials • Bias-Free Hiring
    </p>
</div>
""", unsafe_allow_html=True)
