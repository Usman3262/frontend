# LifeEcho - Anonymous Life Stories Platform

A professional-grade FastAPI backend for an anonymous life stories platform. Users share experiences anonymously using a number-based identity system (`#4821` + password), no email required.

## 📋 Project Structure

```
app/
├── main.py                 # FastAPI app entry point
├── config.py              # Environment configuration
├── database.py            # PostgreSQL connection setup
├── models.py              # SQLAlchemy ORM models
├── schemas.py             # Pydantic request/response schemas
├── tasks.py               # Celery async tasks
│
├── routes/
│   ├── story.py          # Story CRUD endpoints
│   ├── reaction.py       # Reaction endpoints
│   └── search.py         # Search via Meilisearch
│
└── utils/
    ├── auth.py           # Password hashing & auth utilities
    ├── constants.py      # Application constants
    └── validators.py     # Input validation functions
```

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Update .env with your credentials
```

### 3. Setup Database

```bash
# Ensure PostgreSQL is running
# Update DATABASE_URL in .env

# Run the app (will auto-initialize tables)
uvicorn app.main:app --reload
```

### 4. Start Services

**Terminal 1: FastAPI Backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery Worker** (optional but recommended)
```bash
celery -A app.tasks worker --loglevel=info
```

**Terminal 3: Celery Beat** (optional, for scheduled tasks)
```bash
celery -A app.tasks beat --loglevel=info
```

**Terminal 4: Redis**
```bash
redis-server
```

**Terminal 5: Meilisearch**
```bash
./meilisearch
```

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔐 Authentication

All story posting/deletion requires authentication via **anonymous number + password**.

### Example Flow

**1. Signup**
```bash
curl -X POST "http://localhost:8000/auth/signup" \
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

Save your `anonymous_number` (#4821) and password!

**2. Login**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"anonymous_number": "#4821", "password": "MyPass123"}'
```

**3. Post Story**
```bash
curl -X POST "http://localhost:8000/stories" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today I learned that persistence is key. Despite failures...",
    "category": "Life Lessons",
    "image_url": "https://res.cloudinary.com/..."
  }' \
  -G --data-urlencode "anon_num=#4821" \
  --data-urlencode "password=MyPass123"
```

## 📝 Core Features

### Stories
- **POST** `/stories` - Create new story (needs auth)
- **GET** `/stories` - Get story feed (with sorting/filtering)
- **GET** `/stories/{story_id}` - Get story details
- **DELETE** `/stories/{story_id}` - Delete story (author only)

### Reactions
- **POST** `/reactions` - Add emotional reaction (anonymous or authenticated)
- **GET** `/reactions/{story_id}` - Get reaction counts
- **GET** `/reactions/{story_id}/breakdown` - Detailed reaction percentages

Valid reactions:
- `Relatable` - Story resonates with me
- `Inspired` - Story inspires me
- `StayStrong` - Supportive reaction
- `Helpful` - Story provided value

### Search
- **POST** `/search` - Full-text search (Meilisearch)
- **GET** `/search/categories` - Available categories
- **GET** `/search/trending` - Trending stories

## 🗄️ Database Schema

### AnonymousUser
```sql
- id (PK)
- anonymous_number (UNIQUE, e.g., "#4821")
- password_hash (bcrypt)
- created_at
- is_active
```

### Story
```sql
- id (PK)
- author_id (FK → AnonymousUser)
- content (TEXT, max 2000 chars)
- category (VARCHAR)
- image_url (VARCHAR)
- summary (TEXT, AI-generated)
- is_published (BOOLEAN)
- moderation_status (pending/approved/rejected)
- created_at, updated_at
- view_count (INTEGER)
```

### Reaction
```sql
- id (PK)
- story_id (FK → Story)
- user_id (FK → AnonymousUser, nullable)
- reaction_type (VARCHAR)
- created_at
```

## ⚙️ Configuration

All settings load from `.env` file via `pydantic-settings`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/lifeecho

# Cache & Message Queue
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Search
MEILISEARCH_URL=http://localhost:7700

# AI Features
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Application
DEBUG=False
SECRET_KEY=your-secret-key
MAX_STORY_LENGTH=2000
MIN_STORY_LENGTH=10
```

See [app/config.py](app/config.py) for all available settings.

## 🛡️ Validation

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

### Story Content
- 10-2000 characters
- Cannot be empty/whitespace only

### Valid Categories
- Life Lessons
- Achievements
- Regrets
- Career
- Relationships
- Personal Growth

## 📊 Async Architecture

All endpoints are **fully async** using:
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM with asyncpg driver
- **asyncio** - Python async/await

Database queries are non-blocking:
```python
result = await db.execute(select(Story).where(...))
story = result.scalar_one_or_none()
```

## ⏱️ Background Tasks (Celery)

### Implemented Tasks
- `moderate_story` - AI content moderation
- `summarize_story` - Generate AI summaries
- `extract_lessons` - Extract key life lessons
- `generate_daily_digest` - Daily email digest
- `cleanup_expired_sessions` - Session cleanup

### Example Job
```python
from app.tasks import moderate_story

# Queue task
moderate_story.delay(story_id=123)
```

## 🔎 Search (Meilisearch)

Full-text search with:
- Content search
- Category filtering
- Pagination
- Fallback to database LIKE search if Meilisearch unavailable

```python
# Search stories
POST /search
{
  "query": "life lessons learned",
  "category": "Life Lessons",
  "limit": 20,
  "offset": 0
}
```

## 📦 Dependencies

Core:
- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **psycopg** - PostgreSQL driver
- **pydantic** - Data validation

Security & Auth:
- **bcrypt** - Password hashing

Async & Background:
- **celery** - Task queue
- **redis** - Cache & message broker

Search:
- **meilisearch** - Full-text search

AI/ML:
- **openai** - Moderation, summarization (integrated via tasks)

## 🧪 Testing

Create test file `test_api.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_signup():
    response = client.post("/auth/signup", json={"password": "TestPass123"})
    assert response.status_code == 201
    assert "anonymous_number" in response.json()
```

Run tests:
```bash
pytest test_api.py -v
```

## 📖 Error Handling

All endpoints return consistent error format:

```json
{
  "detail": "User not found",
  "status_code": 404,
  "timestamp": "2024-01-15T10:30:00"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad request (validation error)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Server error

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY` to random value
- [ ] Configure CORS origins
- [ ] Setup PostgreSQL backups
- [ ] Configure Redis persistence
- [ ] Setup Meilisearch authentication
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS
- [ ] Setup monitoring & logging
- [ ] Configure rate limiting

## 🔗 Frontend Integration

Example Next.js integration:

```javascript
// Signup
const response = await fetch("http://localhost:8000/auth/signup", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ password: "MyPass123" })
});
const { anonymous_number } = await response.json();

// Post story
await fetch("http://localhost:8000/stories?anon_num=" + anonymous_number + "&password=" + password, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    content: "My story...",
    category: "Life Lessons"
  })
});
```

## 📝 Logging

Logging is configured in `app/main.py`:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("User authenticated: #4821")
```

Logs appear in console and can be integrated with
- ELK Stack
- CloudWatch
- Datadog
- Sentry

## 📄 License

MIT License - See LICENSE file

## 💡 Contributing

1. Fork repo
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m "Add amazing feature"`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📧 Support

For issues, questions, or contributions:
- Create GitHub issue
- Check existing issues first

---

**LifeEcho** - Echoes of people's lives shared anonymously, meaningful & safe 🌍
