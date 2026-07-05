# Deployment Guide

FinBuddy can be deployed to multiple cloud platforms. This guide covers the recommended approaches.

## Quick Start (Docker Compose)

```bash
# 1. Clone and enter repository
git clone https://github.com/yourusername/finbuddy.git
cd finbuddy

# 2. Create environment file
cp .env.example .env
# Edit .env and set GEMINI_API_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY

# 3. Start all services
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health
```

Services started:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI Backend on port 8000
- MCP Server on port 8001
- Next.js Frontend on port 3000
- Celery Worker + Beat (background tasks)

## Google Cloud Run (Recommended for Serverless)

```bash
# Build and push backend image
gcloud builds submit --config cloudbuild.yaml ./backend

# Deploy to Cloud Run
gcloud run deploy finbuddy-backend \
  --image gcr.io/PROJECT_ID/finbuddy-backend \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=xxx,JWT_SECRET_KEY=yyy
```

## Railway / Render (Easiest for Hackathons)

1. Connect your GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically on every push to `main`

Required env vars:
```
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
GEMINI_API_KEY=your-google-ai-studio-key
JWT_SECRET_KEY=strong-random-string
ENCRYPTION_KEY=32-byte-base64-string
AGENT_FRAMEWORK=adk
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `GEMINI_MODEL` | No | Default `gemini-2.5-flash` |
| `GEMINI_MODEL_PRO` | No | Default `gemini-2.5-pro` |
| `DATABASE_URL` | Yes | PostgreSQL async URL |
| `REDIS_URL` | Yes | Redis connection string |
| `JWT_SECRET_KEY` | Yes | 32+ char random string |
| `ENCRYPTION_KEY` | Yes | 32-byte base64 Fernet key |
| `AGENT_FRAMEWORK` | No | `adk` (default) or `langchain` |
| `PII_REDACTION_ENABLED` | No | `true` (default) |
| `RATE_LIMIT_ENABLED` | No | `true` (default) |
| `AUDIT_LOGGING_ENABLED` | No | `true` (default) |

## Security Checklist Before Deploying

- [ ] Changed `JWT_SECRET_KEY` from default
- [ ] Generated strong `ENCRYPTION_KEY` (use `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
- [ ] Set `GEMINI_API_KEY` (never commit to Git)
- [ ] Enabled `PII_REDACTION_ENABLED=true`
- [ ] Enabled `RATE_LIMIT_ENABLED=true`
- [ ] Enabled `AUDIT_LOGGING_ENABLED=true`
- [ ] Set `APP_ENV=production` and `DEBUG=false`
- [ ] Configured CORS origins to only allowed domains
- [ ] Enabled HTTPS/TLS termination at load balancer
- [ ] Set up database backups
- [ ] Configured log aggregation (CloudWatch, Datadog, etc.)
