"""
LifeEcho FastAPI Backend - Quick Start Guide

This document provides the fastest way to get the LifeEcho API running locally.
"""

# QUICKSTART: Get LifeEcho API Running in 5 Minutes

## ⚡ STEP 1: Install Dependencies

```bash
# Activate virtual environment (already created)
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install packages
pip install -r requirements.txt
```

## ⚡ STEP 2: Configure Environment

```bash
# Copy and edit environment variables
cp .env.example .env
```

Edit `.env` and at minimum set:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lifeecho
REDIS_URL=redis://localhost:6379/0
```

**Ensure these services are running:**
- PostgreSQL (default: localhost:5432)
- Redis (default: localhost:6379)
- Meilisearch (optional, default: localhost:7700)

## ⚡ STEP 3: Run FastAPI Server

**OPTION A: Using Uvicorn (Simple)**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**OPTION B: Using Python Script**
```bash
python -m app.main
```

Server starts at: `http://localhost:8000`

## ⚡ STEP 4: Access API Documentation

Open in browser:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## ⚡ STEP 5: Test API (Optional)

### 1. Create User
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPass123"}'
```

Response:
```json
{
  "id": 1,
  "anonymous_number": "#4821",
  "created_at": "2024-01-15T10:30:00",
  "is_active": true
}
```

### 2. Post a Story
```bash
curl -X POST "http://localhost:8000/api/v1/stories?anon_num=%234821&password=MyPass123" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today I learned that persistence is key to success",
    "category": "Life Lessons"
  }'
```

### 3. Get Story Feed
```bash
curl http://localhost:8000/api/v1/stories
```

### 4. Search Stories
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "persistence"}'
```

## 🔄 BACKGROUND TASKS (Optional for Development)

For **MVP/Development**, background tasks are NOT required:
- Stories auto-publish immediately (no moderation delay)
- Events are published to Redis (built-in simple queue)
- No Celery worker needed to get started

**Performance Tips:**
- Stories should post in **< 200ms** (network + DB latency)
- Railway PostgreSQL adds 100-150ms latency (normal for cloud)
- Use local PostgreSQL for faster development

**IF you need Celery for production:**

To enable Celery (requires Python < 3.14 for full compatibility):

```bash
# Terminal 1: Celery worker (background job processor)
celery -A app.tasks worker --loglevel=info

# Terminal 2: Celery beat (optional, for scheduled tasks)
# Note: Celery Beat requires Python <3.14, use simple Redis queue instead for Python 3.14+
```

**Environment Setup:**
- Ensure Redis is running and `REDIS_URL` is set in `.env`
- Celery uses the same Redis instance as the app
- For cloud: Railway provides free Redis tier

## 📊 PROJECT STRUCTURE

```
app/
├── main.py              ← API entry point (HTTP server)
├── tasks.py             ← Background tasks (Celery)
├── config.py            ← Settings management
├── database.py          ← Database connection
├── models.py            ← ORM models (User, Story, Reaction)
├── schemas.py           ← Request/response validation
├── routes/              ← HTTP route handlers (thin layer)
│   ├── story.py        ← Story endpoints
│   ├── reaction.py     ← Reaction endpoints
│   └── search.py       ← Search endpoints
├── services/            ← Business logic (main layer)
│   ├── auth_service.py         ← User auth
│   ├── story_service.py        ← Story CRUD
│   ├── reaction_service.py     ← Reaction handling
│   └── search_service.py       ← Search logic
└── utils/               ← Utilities
    ├── constants.py    ← Constants & validation values
    ├── validators.py   ← Input validation functions
    └── ai.py           ← AI integration stubs
```

## 🎯 KEY ENDPOINTS

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | /auth/signup | No | Create new anonymous user |
| POST | /auth/login | No | Login with credentials |
| GET | /auth/me | No | Get current user info |
| POST | /api/v1/stories | Yes | Create new story |
| GET | /api/v1/stories | No | Get story feed |
| GET | /api/v1/stories/{id} | No | Get story details |
| DELETE | /api/v1/stories/{id} | Yes | Delete own story |
| POST | /api/v1/reactions | No | Add reaction |
| GET | /api/v1/reactions/{id} | No | Get reaction counts |
| POST | /api/v1/search | No | Search stories |
| GET | /api/v1/search/categories | No | Get categories |
| GET | /api/v1/search/trending | No | Get trending stories |
| GET | /health | No | Health check |

## 🔐 AUTHENTICATION

Authentication via anonymous number + password:

```bash
# Example: Add auth to story creation
curl -X POST "http://localhost:8000/api/v1/stories?anon_num=%234821&password=MyPass123" \
  -H "Content-Type: application/json" \
  -d '{"content": "My story...", "category": "Life Lessons"}'
```

## ⚙️ ENVIRONMENT VARIABLES

Required (.env):
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/lifeecho
REDIS_URL=redis://localhost:6379/0
```

Optional:
```env
DEBUG=False                      # Development mode
OPENAI_API_KEY=sk-...           # For AI features
MEILISEARCH_URL=http://...      # For advanced search
SECRET_KEY=your-secret-key      # Security key
```

See `.env.example` for all options.

## 🚀 TROUBLESHOOTING

### "Connection refused" on database
- Check PostgreSQL is running: `psql -U user -d lifeecho`
- Update DATABASE_URL in .env

### "Connection refused" on Redis
- Check Redis is running: `redis-cli ping`
- Update REDIS_URL in .env

### Import errors
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

### Celery tasks not processing
- Check Redis is running
- Check Celery worker terminal has no errors
- Run: `celery -A app.tasks purge` (clear queue)

## 📚 FULL DOCUMENTATION

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Detailed Setup**: See [README.md](README.md)
- **Project Status**: See [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)
- **Product Spec**: See [appDoc.md](appDoc.md)

## ✅ QUICK VERIFICATION

```bash
# Check API is running
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"LifeEcho API","version":"1.0.0"}

# Check API docs exist
# Open: http://localhost:8000/docs
```

---

**Ready to go!** 🚀

If you encounter any issues, check:
1. All services are running (PostgreSQL, Redis)
2. Environment variables in .env are correct
3. Virtual environment is activated
4. Dependencies installed: `pip install -r requirements.txt`
