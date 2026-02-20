# 🚀 Velos AI - Production Deployment Guide

## 📋 Quick Start (Development)

### Option 1: Automated Setup (Recommended)

```bash
# Run the automated setup script
chmod +x setup.sh
./setup.sh

# Edit .env and add your GROQ_API_KEY
nano .env

# Start backend (Terminal 1)
./run-backend.sh

# Start frontend (Terminal 2)
./run-frontend.sh

# Open browser
http://localhost:5173
```

### Option 2: Manual Setup

```bash
# 1. Backend Setup
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Configure environment
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# 3. Frontend Setup
cd velos-frontend
npm install
cd ..

# 4. Start Backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 5. Start Frontend (new terminal)
cd velos-frontend
npm run dev
```

---

## 🐳 Docker Deployment

### Local Docker (Quick Test)

```bash
# 1. Build and run with Docker Compose
docker-compose up --build

# 2. Access the application
Backend:  http://localhost:8000
Frontend: http://localhost:5173

# 3. View logs
docker-compose logs -f

# 4. Stop containers
docker-compose down
```

### Production Docker Deployment

```bash
# 1. Set environment variables
export GROQ_API_KEY=your_actual_api_key_here

# 2. Build production images
docker build -t velos-backend:latest .
docker build -t velos-frontend:latest -f Dockerfile.frontend .

# 3. Run with proper config
docker-compose -f docker-compose.yml up -d

# 4. Check health
curl http://localhost:8000/health
curl http://localhost:5173/
```

---

## ☁️ Cloud Deployment Options

### Option A: Render.com (Recommended for Quick Deploy)

1. **Backend Deployment:**
   ```bash
   # Push to GitHub
   git add .
   git commit -m "Production ready"
   git push origin main
   
   # On Render.com:
   - Create new Web Service
   - Connect GitHub repo
   - Build Command: pip install -r requirements.txt && python -m spacy download en_core_web_sm
   - Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT
   - Add Environment Variable: GROQ_API_KEY
   ```

2. **Frontend Deployment:**
   ```bash
   # On Render.com:
   - Create new Static Site
   - Build Command: cd velos-frontend && npm install && npm run build
   - Publish Directory: velos-frontend/dist
   ```

### Option B: AWS EC2

```bash
# 1. Launch EC2 instance (t3.medium recommended)
# Ubuntu 22.04 LTS, open ports 80, 443, 8000

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx docker.io docker-compose

# 4. Clone repository
git clone https://github.com/yourusername/velos-ai.git
cd velos-ai

# 5. Setup environment
cp .env.example .env
nano .env  # Add GROQ_API_KEY

# 6. Deploy with Docker
docker-compose up -d

# 7. Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/velos
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/velos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option C: Google Cloud Run

```bash
# 1. Install gcloud CLI
# 2. Authenticate
gcloud auth login

# 3. Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/velos-backend

# 4. Deploy
gcloud run deploy velos-backend \
  --image gcr.io/YOUR_PROJECT/velos-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key_here
```

---

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run API tests
pytest tests/test_api_endpoints.py -v

# Run all tests
pytest tests/ -v --tb=short

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## 📊 Monitoring & Logs

### View Application Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Local development logs
tail -f logs/velos_*.log

# Filter by log level
grep "ERROR" logs/velos_*.log
grep "WARNING" logs/velos_*.log
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# API health with metrics
curl http://localhost:8000/api/health

# Get system status
curl http://localhost:8000/api/status
```

### Performance Monitoring

```bash
# Cache statistics
curl http://localhost:8000/api/stats

# Agent performance
curl http://localhost:8000/api/agents

# Database audit trail
curl http://localhost:8000/api/audit
```

---

## 🔧 Maintenance

### Database Backup

```bash
# Backup SQLite database
cp velos_audit.db backups/velos_audit_$(date +%Y%m%d).db

# Backup ChromaDB vector store
tar -czf backups/chroma_db_$(date +%Y%m%d).tar.gz chroma_db/
```

### Log Rotation

```bash
# Add to crontab for automatic cleanup
0 0 * * * find /path/to/velos/logs -name "*.log" -mtime +30 -delete
```

### Update Dependencies

```bash
# Update Python packages
pip list --outdated
pip install --upgrade package-name

# Update frontend packages
cd velos-frontend
npm outdated
npm update
```

---

## 🔒 Security Checklist

- [ ] `.env` file is NOT committed to git
- [ ] `GROQ_API_KEY` is set securely
- [ ] CORS origins are restricted in production
- [ ] Rate limiting is enabled
- [ ] HTTPS/SSL is configured
- [ ] Firewall rules are configured
- [ ] Database files are backed up
- [ ] Logs are monitored for errors
- [ ] Environment variables use secrets manager
- [ ] API keys are rotated periodically

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python3 --version  # Must be 3.9+

# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>  # If needed

# Check environment
cat .env | grep GROQ_API_KEY

# Check logs
tail -f logs/velos_*.log
```

### Frontend won't start

```bash
# Check Node version
node --version  # Must be 18+

# Clear cache
cd velos-frontend
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is in use
lsof -i :5173
```

### ChromaDB issues

```bash
# Clear vector database
rm -rf chroma_db/
# Will auto-recreate on next run

# Check disk space
df -h
```

### Memory issues

```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart backend

# Monitor logs
docker-compose logs -f backend | grep "memory"
```

---

## 📈 Scaling Recommendations

### For < 100 users/day
- **Setup:** Single EC2 t3.small or Render free tier
- **Database:** SQLite (included)
- **Storage:** Local filesystem

### For 100-1000 users/day
- **Setup:** EC2 t3.medium or Render standard
- **Database:** Upgrade to PostgreSQL
- **Storage:** S3 for uploads
- **Caching:** Redis for session management

### For 1000+ users/day
- **Setup:** Load balanced EC2 instances
- **Database:** RDS PostgreSQL with read replicas
- **Storage:** S3 with CloudFront CDN
- **Caching:** Redis cluster
- **Monitoring:** Datadog or New Relic

---

## 📞 Support

For issues or questions:
- Check logs first: `logs/velos_*.log`
- Run health check: `curl localhost:8000/health`
- Review this guide
- Check GitHub Issues

---

## ✅ Production Readiness Checklist

- [x] Environment setup automated
- [x] API contract mismatches fixed
- [x] Centralized logging implemented
- [x] Memory leaks fixed
- [x] Comprehensive API tests added
- [x] Docker setup completed
- [x] Performance caching added
- [x] Health checks configured
- [x] Error monitoring ready
- [x] Deployment guide created

**Status: PRODUCTION READY ✨**

Last Updated: $(date +"%B %d, %Y")
