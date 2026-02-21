# Velos AI Architecture - SaaS Edition

## 1. System Overview
Velos comprises an overarching **FastAPI Application Factory** connecting asynchronous workers, an abstract LLM Failover service, and a Multi-tenant persistence layer using SQLAlchemy 2.0.

## 2. PII Data Flow
1. Resume ingested explicitly by `services/resume_parser.py` extracting binary blob to textual nodes.
2. PII Redactor (`services/pii_redactor.py`) intercepts payload, executing Groq-based text classification to strip entities.
3. Removed entities are encrypted symmetric AES-256 (`Fernet`) prior to entry into `velos.db` for later decoding when the Recruiting manager evaluates success.

## 3. Storage Architecture
Storage sits behind `services/storage_service.py` to detach hard-mount dependencies.
- **Local Dev**: `./uploads` syncs via disk.
- **Production**: Abstract routing to `Cloudflare R2` or `Supabase Storage`.

## 4. LLM Routing ($0 Limits)
`LLMClient` coordinates rate limits using native python `asyncio.Lock()`.
- **Groq** (30 RPM Limit) -> Evaluated via Token Bucket logic.
- **Gemini** (60 RPM Limit) -> Steps in on HTTP 429s.
- **Ollama** -> End-of-line fallback routing running on localhost `11434`.

## 5. Security model
Tenant boundaries persist explicitly across data fetching mechanisms, executed through Database base query overrides in `repositories/tenant_repo.py`. Webhooks execute behind HMAC SHA-256 checks mimicking standard Stripe configurations.
