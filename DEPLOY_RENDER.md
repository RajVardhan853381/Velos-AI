# 🚀 Deploy Velos to Render - Step by Step Guide

## ✅ Prerequisites Complete
- ✅ Code pushed to GitHub: https://github.com/RajVardhan853381/Velos-AI
- ✅ render.yaml configuration file created
- ✅ Server configured to use dynamic PORT

---

## 📋 Deployment Steps

### **Step 1: Sign Up on Render** (2 minutes)

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your GitHub repositories

---

### **Step 2: Create New Web Service** (1 minute)

1. On Render Dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect account"** if not already connected to GitHub
4. Find and select **"Velos-AI"** repository
5. Click **"Connect"**

---

### **Step 3: Configure Service** (2 minutes)

Render will auto-detect most settings from `render.yaml`, but verify:

#### **Basic Settings:**
- **Name:** `velos-ai` (or your preferred name)
- **Region:** `Oregon (US West)` (or closest to you)
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

#### **Build & Deploy:**
- **Build Command:** (auto-filled from render.yaml)
  ```bash
  pip install -r requirements.txt && python -m spacy download en_core_web_sm
  ```

- **Start Command:** (auto-filled from render.yaml)
  ```bash
  uvicorn server:app --host 0.0.0.0 --port $PORT
  ```

#### **Instance Type:**
- Select **"Free"** plan

---

### **Step 4: Add Environment Variables** (1 minute)

⚠️ **CRITICAL STEP** - Your app won't work without this!

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add:
   - **Key:** `GROQ_API_KEY`
   - **Value:** Your actual GROQ API key (from https://console.groq.com)

---

### **Step 5: Deploy!** (5-10 minutes)

1. Click **"Create Web Service"** button at the bottom
2. Render will start building your app - watch the logs:
   - Installing Python dependencies
   - Downloading spaCy model
   - Starting FastAPI server

3. Wait for the status to show **"Live"** (green)

---

## 🎉 Your App is Live!

Once deployed, you'll get a URL like:
```
https://velos-ai.onrender.com
```

Or:
```
https://velos-ai-xxxx.onrender.com
```

### **Test Your Deployment:**

1. Click the URL in Render dashboard
2. You should see the Velos frontend
3. Try uploading a resume to verify it works!

---

## 🔧 Post-Deployment

### **View Logs:**
- Click on your service in Render
- Go to "Logs" tab to see real-time output

### **Environment Variables:**
- Go to "Environment" tab to add/edit variables
- Changes trigger automatic redeployment

### **Custom Domain (Optional):**
- Go to "Settings" → "Custom Domain"
- Add your own domain (e.g., velos.yourdomain.com)

---

## ⚠️ Important Notes

### **Free Tier Limitations:**
- ✅ 750 hours/month (enough for hackathon)
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ First request after sleep takes ~30 seconds to wake up

### **Keep Your App Awake:**
**Option 1: During Demo** - Keep a browser tab open

**Option 2: Auto Ping** - Use UptimeRobot (free)
1. Go to https://uptimerobot.com
2. Sign up free
3. Add new monitor → HTTP(s)
4. URL: Your Render URL
5. Interval: 5 minutes

---

## 🐛 Troubleshooting

### **Build Failed:**
- Check Render logs for error messages
- Common issues:
  - Missing dependency in requirements.txt
  - Python version mismatch
  - spaCy model download failed

### **App Crashes:**
- Check if GROQ_API_KEY is set correctly
- View logs in Render dashboard
- Verify all dependencies installed

### **Can't Access App:**
- Check if deployment status is "Live"
- Wait 30 seconds if app was sleeping
- Check Render logs for errors

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Render Discord: https://render.com/community
- Your repo: https://github.com/RajVardhan853381/Velos-AI

---

## 🎯 Quick Checklist

- [ ] Signed up on Render with GitHub
- [ ] Created new Web Service
- [ ] Connected Velos-AI repository
- [ ] Added GROQ_API_KEY environment variable
- [ ] Clicked "Create Web Service"
- [ ] Waited for deployment to complete
- [ ] Tested the live URL
- [ ] (Optional) Set up UptimeRobot for wake-up

---

**Good luck with your ZYND AIckathon 2025 demo! 🚀**
