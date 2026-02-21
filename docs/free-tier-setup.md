# Velos Free-Tier Startup Stack

Zero dollars, massive scale. Follow these steps to reach $0 production deployments.

## 1. Hosting Options

### Option A: Render (Easiest)
- Create account at Render.com
- Connect GitHub repo.
- Web Service -> `backend` dir -> build command `pip install -r requirements.txt && ...`
- Static site -> `velos-frontend` dir -> build command `npm run build` -> publish `dist`

### Option B: Railway ($5/mo free limit)
- Provision PostgreSQL plugin first.
- Link repo. Auto-detects Dockerfile and Vite.

## 2. Database Options

### Neon PostgreSQL
- Free 0.5 GB. Automatically scales to zero during inactivity.
- Get connection string like `postgresql://user:pass@ep-db.region.aws.neon.tech/velos`
- Replace in `.env`.

### Supabase
- Always on, free 500 MB.
- Provides PostgreSQL connection string + free storage buckets.

## 3. Storage Options
- **Cloudflare R2**: 10GB free. Set up bucket, configure S3 keys in `.env`.
- **Supabase Storage**: 1GB free.

## 4. LLM API (Groq -> Gemini -> Ollama)
- **Groq**: Free, 30 req/min. Sign up, generate API key.
- **Gemini**: Free tier 60/min. Fallback.
- **Ollama**: Local unlimited fallback.

## 5. Deployment Step by Step
1. Commit all code to a private GitHub Repo.
2. Sign up for Neon DB, Copy Connection string -> GitHub Actions Secrets (`DATABASE_URL`).
3. Deploy DB Migrations via Actions.
4. Deploy Frontend via Vercel (Import GitHub Repo, auto-builds Vite).
5. Deploy Backend via Render Web Service.

Enjoy your $0 MRR infrastructure!
