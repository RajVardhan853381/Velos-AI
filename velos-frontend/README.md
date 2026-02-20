# Velos Frontend 🎨

**Modern React + 3D Visualization for AI-Powered Blind Hiring Platform**

## 🌟 Features

### 🎨 Design System: "Corporate Pastel" Aesthetic
- **Color Palette**: 
  - Warm Cream backgrounds (`#FDFBF7`)
  - Mint Green success states (`#D1FAE5`)
  - Baby Blue headers (`#E0F2FE`)
  - Deep Navy text for readability (`#0369A1`)
  
- **Glassmorphism**: Translucent cards with frosted glass effect
- **Smooth Animations**: Framer Motion for buttery transitions
- **Responsive Design**: Mobile-first approach with Tailwind CSS

### 🧠 AI Pipeline Visualization

The centerpiece of this frontend is the **3D Agent Pipeline** built with React Three Fiber:

- **3 Geometric Nodes** representing each agent:
  - 🔒 **Gatekeeper** (Blue Icosahedron) - PII Removal
  - ✅ **Validator** (Purple Icosahedron) - Skill Matching
  - 🔍 **Inquisitor** (Orange Icosahedron) - Fraud Detection
  
- **Live Data Packet** with golden trail that physically travels between agents
- **Glassmorphic Materials** using `MeshTransmissionMaterial` for high-tech look
- **State-Based Colors**: Agents glow when active, turn green when completed

### 📊 Dashboard Components

1. **Stat Cards**: Candidates verified, trust scores, bias flags
2. **Trust Trend Chart**: Area chart showing 7-day verification quality
3. **Recent Activity Feed**: Live pipeline results
4. **Results Panel**: Circular progress indicator + verified skills breakdown

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (compatible with Vite 5.x)
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd velos-frontend
npm install
npm run dev
```

The frontend will start on **http://localhost:5173**

### Production Build

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
velos-frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx           # Main stats dashboard with charts
│   │   ├── VerificationPipeline.jsx # Upload + state machine + results
│   │   └── Pipeline3D.jsx          # 3D Three.js visualization
│   ├── App.jsx                     # Main layout with sidebar nav
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Tailwind CSS imports
├── public/                         # Static assets
├── index.html                      # HTML entry point
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration (proxy to :8000)
├── tailwind.config.js              # Custom color palette
└── postcss.config.js               # PostCSS for Tailwind
```

## 🎯 Key Technologies

| Technology | Purpose |
|------------|---------|
| **React 18** | Component architecture |
| **Vite 5.4** | Lightning-fast build tool |
| **Tailwind CSS 3.4** | Utility-first styling |
| **Framer Motion** | Page transitions & animations |
| **Recharts** | Dashboard charts (Area, Bar, etc.) |
| **React Three Fiber** | 3D WebGL canvas |
| **Drei** | Three.js helpers (Float, Trail, Html) |
| **Lucide React** | Icon library (Shield, Users, etc.) |

## 🎨 Design Tokens

### Colors (in `tailwind.config.js`)

```javascript
colors: {
  background: '#FDFBF7',   // Warm Cream
  sidebar: '#F0F4F8',      // Cool Grey-Blue
  primary: {
    light: '#E0F2FE',      // Pastel Blue
    DEFAULT: '#38BDF8',    // Sky Blue
    dark: '#0369A1',       // Navy Blue
  },
  success: {
    light: '#D1FAE5',      // Pastel Mint
    DEFAULT: '#10B981',    // Emerald
  },
  accent: {
    purple: '#EEE6FF',     // Pastel Lavender
    peach: '#FFEDD5',      // Pastel Peach
  }
}
```

### Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 400 (regular), 600 (semibold), 700 (bold), 800-900 (headings)

## 🔌 API Integration

The frontend proxies API requests to the backend via Vite's proxy configuration:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Example API Call (Future Enhancement)

```javascript
// Verify candidate
const response = await fetch('/api/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    resume_text: resumeText,
    job_description: jobDesc
  })
});
const result = await response.json();
```

## 🎬 3D Pipeline Animation Flow

### State Machine
```
idle → gatekeeper (2.5s) → validator (2.5s) → inquisitor (3s) → done
```

### Visual Effects
1. **Agent Node**: Rotates slowly using `useFrame` hook
2. **Data Packet**: Uses `lerp()` for smooth position interpolation
3. **Trail Effect**: Golden particle trail follows the data packet
4. **Status Colors**:
   - 🔵 Active: Agent color with emissive glow
   - 🟢 Completed: Emerald green
   - ⚪ Idle: Light slate gray

## 📱 Responsive Breakpoints

- **Mobile**: `< 768px` (stacked layout, hidden sidebar)
- **Tablet**: `768px - 1024px` (sidebar visible)
- **Desktop**: `> 1024px` (full layout with 3-column grid)

## 🧪 Testing the 3D Scene

Click **"Initiate Verification"** on the Verify Candidate tab to see:

1. ✨ 3D scene appears with idle agents (light gray)
2. 🔵 Gatekeeper activates (blue glow, data packet arrives)
3. 🟣 Validator activates (purple glow, packet moves)
4. 🟠 Inquisitor activates (orange glow)
5. ✅ Results panel appears with 92% trust score

## 🐛 Troubleshooting

### "Three.js MeshTransmissionMaterial not working"
- Ensure `@react-three/drei` version is `>=9.x`
- Check that browser supports WebGL 2.0

### "Vite port already in use"
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### "Fonts not loading"
- Verify Google Fonts link in `index.html`
- Check network tab for CORS issues

## 🚢 Deployment

### Netlify / Vercel
```bash
npm run build
# Deploy the 'dist' folder
```

### Environment Variables
Set `ENVIRONMENT=production` in your deployment platform to enable CORS whitelist.

## 🤝 Contributing

Built for **ZYND AIckathon 2025** by the Velos team.

## 📄 License

MIT License - See LICENSE file for details

---

**Made with ❤️ using React, Three.js, and Tailwind CSS**
