# Frontend Integration Guide

## 🔌 Connecting React Frontend to FastAPI Backend

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │     React Frontend (Vite Dev Server)               │   │
│  │     http://localhost:5173                          │   │
│  │                                                     │   │
│  │  • Dashboard (Charts + Stats)                      │   │
│  │  • VerificationPipeline (3D Visualization)         │   │
│  │  • Pipeline3D (Three.js Scene)                     │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓ Proxy                          │
│                    /api/* requests                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                FastAPI Backend Server                       │
│                http://localhost:8000                        │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  POST /api/verify                                  │   │
│  │  ├─> Gatekeeper Agent (PII Removal)                │   │
│  │  ├─> Validator Agent (Skill Matching)              │   │
│  │  └─> Inquisitor Agent (Fraud Detection)            │   │
│  │                                                     │   │
│  │  GET  /api/stats        (Dashboard data)           │   │
│  │  GET  /api/agents       (Agent info)               │   │
│  │  GET  /api/audit        (Audit logs)               │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↓                                 │
│  ┌────────────────────────────────────────────────────┐   │
│  │  GROQ API (llama-3.3-70b-versatile)                │   │
│  │  Zynd Protocol (W3C DID/VC)                        │   │
│  │  ChromaDB (Vector Store)                           │   │
│  │  SQLite (velos_state.db, velos_audit.db)           │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Step-by-Step Setup

### 1. Start the Backend (Terminal 1)

```bash
cd /media/raj/Raj/Hackathon/trustflow
python server.py
```

Expected output:
```
🚀 Velos Server Starting...
✅ Orchestrator: Connected
✅ Zynd Protocol v0.1.5-compat (Python 3.10.12)
✅ GROQ API: Connected
📡 API Endpoints: /api/verify, /api/stats, /api/agents...
```

### 2. Start the Frontend (Terminal 2)

```bash
cd /media/raj/Raj/Hackathon/trustflow/velos-frontend
npm run dev
```

Expected output:
```
VITE v5.4.21  ready in 794 ms
➜  Local:   http://localhost:5173/
➜  Network: http://192.168.x.x:5173/
```

### 3. Open in Browser

Navigate to: **http://localhost:5173**

You should see:
- **Dashboard Tab**: Stats cards + Trust trend chart
- **Verify Candidate Tab**: 3D pipeline visualization

## 📡 API Integration Points

### Current Implementation

The `VerificationPipeline.jsx` component now has **TWO modes**:

#### 1. **Demo Mode** (No Backend Required)
- Click "Demo Mode" button
- Uses simulated data with hardcoded results
- Perfect for testing the UI/UX flow

#### 2. **Real API Mode** (Connects to Backend)
- Enter resume text and job description
- Click "Analyze with Real API"
- Makes actual `POST /api/verify` request to `http://localhost:8000`

### API Request Flow

```javascript
// Frontend: VerificationPipeline.jsx (Line ~20-60)
const startRealAnalysis = async () => {
  const response = await fetch('http://localhost:8000/api/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description: jobDescription,
    }),
  });
  
  const data = await response.json();
  // data structure matches your backend response
};
```

### Expected Backend Response

```json
{
  "id": "CAND-8F7A",
  "status": "passed",
  "trust_score": 92,
  "skill_match": 88,
  "timestamp": "14:32:44",
  "stages": {
    "gatekeeper": {
      "status": "passed",
      "pii_removed": true,
      "eligible": true,
      "years_exp": 7
    },
    "validator": {
      "status": "passed",
      "skill_match": 88,
      "matched_skills": ["Python", "React", "AWS"]
    },
    "inquisitor": {
      "status": "passed",
      "trust_score": 92,
      "questions_generated": 3
    }
  },
  "redacted_resume": "[REDACTED NAME]\n[REDACTED EMAIL]...",
  "questions": [
    "Can you explain your experience with Python?",
    "Describe your React project architecture.",
    "How do you handle AWS deployments?"
  ],
  "credential": {
    "id": "cred-xyz",
    "type": "VerifiedCandidate",
    "issuer": "did:zynd:velos"
  }
}
```

## 🎨 3D Visualization State Machine

### Pipeline States

```javascript
'idle'        → Nothing selected, upload screen visible
'gatekeeper'  → Blue icosahedron glowing, data packet at position [-4, 0, 0]
'validator'   → Purple icosahedron glowing, data packet at [0, 0, 0]
'inquisitor'  → Orange icosahedron glowing, data packet at [4, 0, 0]
'done'        → All agents green, results panel appears
```

### State Transitions

```javascript
// Frontend syncs with backend stages
setPipelineState('gatekeeper');  // When API call starts
await new Promise(r => setTimeout(r, 1000));  // Visual delay
setPipelineState('validator');   // After gatekeeper complete
await new Promise(r => setTimeout(r, 1000));
setPipelineState('inquisitor');  // After validator complete
setPipelineState('done');         // When all agents finish
```

## 🔐 CORS Configuration

### Backend: server.py (Line 43-52)

```python
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",  # React frontend (Vite)
    "http://127.0.0.1:5173",
    "https://velos-ai.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend: vite.config.js (Line 5-13)

```javascript
server: {
  port: 5173,
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

**Note**: The proxy is optional. We're currently using direct `fetch()` to `http://localhost:8000/api/*` for clarity.

## 🧪 Testing the Integration

### Test 1: Demo Mode (No Backend)
1. Go to **Verify Candidate** tab
2. Click **"Demo Mode"**
3. Watch the 3D agents animate
4. See 92% trust score appear after 8 seconds

**Expected**: Works even if backend is down

### Test 2: Real API Mode (With Backend)
1. Start backend server first
2. Go to **Verify Candidate** tab
3. Paste resume text:
```
John Doe
Email: john@example.com
Phone: 555-1234

Senior Software Engineer with 7 years experience in Python, React, AWS...
```
4. Paste job description:
```
Looking for Senior Software Engineer with Python, React, cloud experience...
```
5. Click **"Analyze with Real API"**

**Expected**: 
- Loading spinner appears
- 3D pipeline animates through agents
- Real trust score from backend appears
- Agent statuses match backend response

### Test 3: Error Handling
1. Stop the backend server
2. Try "Analyze with Real API"

**Expected**: 
- Red error banner appears: "API Error: Failed to fetch"
- Pipeline resets to idle state
- User can try again

## 📊 Dashboard Integration (Optional)

### Fetching Real Stats

Add this to `Dashboard.jsx` to fetch real data:

```javascript
import { useEffect, useState } from 'react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Stats fetch failed:', err));
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    // Use stats.total_candidates, stats.agent_stats, etc.
  );
};
```

## 🎯 Key Files Modified

### Frontend
- `src/components/VerificationPipeline.jsx` ← **Main integration point**
- `src/components/Pipeline3D.jsx` ← 3D visualization
- `src/components/Dashboard.jsx` ← Stats dashboard
- `vite.config.js` ← Proxy configuration (optional)

### Backend
- `server.py` ← CORS updated to allow `:5173`

## 🚢 Production Deployment

### Frontend Build
```bash
cd velos-frontend
npm run build
# Output: dist/ folder
```

### Serve with Backend
Option 1: FastAPI serves React build
```python
# Add to server.py
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="velos-frontend/dist", html=True), name="static")
```

Option 2: Deploy separately
- Frontend: Netlify/Vercel (dist folder)
- Backend: Render/Railway (server.py)
- Update CORS to include production domain

## 🐛 Common Issues

### Issue: "Network Error" in browser console
**Fix**: Ensure backend is running on port 8000

### Issue: "CORS policy blocked"
**Fix**: Check ALLOWED_ORIGINS includes `:5173`

### Issue: 3D scene is black
**Fix**: Check browser supports WebGL 2.0 (Chrome/Firefox/Edge)

### Issue: "Cannot read properties of undefined"
**Fix**: Backend response structure changed, update frontend to match

## 📝 Next Steps

1. ✅ **Basic Integration Complete**
2. 🔄 **Add file upload** - Use `/api/parse-resume` endpoint
3. 📊 **Connect Dashboard** - Fetch real-time stats
4. 🔍 **Audit Trail Tab** - Display `/api/audit` logs
5. 🎨 **Polish UI** - Add loading skeletons, error boundaries

---

**You now have a fully functional AI-powered hiring platform with 3D visualization!** 🎉
