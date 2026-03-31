# LifeThreads - Complete Project Documentation

**Project**: LifeEcho - Story sharing platform with AI-powered full-text search  
**Stack**: Python FastAPI (backend) + Next.js/TypeScript (frontend)  
**Status**: MVP Development (Meilisearch integration in progress)  
**Last Updated**: March 31, 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure](#directory-structure)
4. [Backend (Python/FastAPI)](#backend-pythonfastapi)
5. [Frontend (Next.js/TypeScript)](#frontend-nextjstypescript)
6. [Database & External Services](#database--external-services)
7. [API Reference](#api-reference)
8. [Configuration](#configuration)
9. [Deployment](#deployment)
10. [Development Guide](#development-guide)

---

## Project Overview

### Purpose
LifeThreads (LifeEcho) is a web platform for anonymous users to share personal stories and life experiences. Features include:
- **Story Posting**: Anonymous, category-based story sharing
- **Full-Text Search**: AI-powered search via Meilisearch
- **Reactions**: Like and engage with stories
- **Notifications**: Push notifications via Firebase
- **Daily Digest**: Curated story recommendations

### Tech Stack

**Backend:**
- Python 3.13.12
- FastAPI 0.104.1+ (async web framework)
- SQLAlchemy 2.0.48 (async ORM)
- Celery 5.6.2 (background tasks with threads pool)
- PostgreSQL (database)
- Redis (cache/queue)
- Meilisearch (full-text search engine)

**Frontend:**
- Next.js 15+ (React framework)
- TypeScript (type-safe JavaScript)
- Firebase (push notifications, authentication)
- Tailwind CSS (styling)

**Deployment:**
- Backend: Railway (Python/FastAPI)
- Database: Railway PostgreSQL
- Cache: Railway Redis
- Search: Railway Meilisearch
- Frontend: Vercel/Railway

**Development Tools:**
- VS Code
- Git/GitHub
- Docker (optional)

---

## System Architecture

### High-Level Flow

```
[Browser Client]
    ↓
[Next.js Frontend] (port 3000)
    ↓ HTTP/REST
[FastAPI Backend] (port 8000)
    ├── Database: PostgreSQL (Railway)
    ├── Cache: Redis (Railway)
    ├── Search: Meilisearch (Railway)
    └── Queue: Celery Worker (threads pool)
            ↓
    [Background Tasks]
    - Story moderation
    - Search indexing
    - Notifications
    - Daily digest
```

### Data Flow for Story Publishing

```
1. User submits story → Frontend POST /api/v1/stories/post-story
2. Backend validates & creates story in PostgreSQL
3. Backend auto-publishes if content safe (AI moderation)
4. Backend queues Celery task: process_story_event(story_id, "published")
5. Celery worker fetches story from DB
6. Celery indexes story in Meilisearch
7. Story becomes searchable
8. Frontend searches via GET /api/v1/stories/search?search_text=...
9. Search hits Meilisearch first, falls back to DB LIKE query
```

---

## Directory Structure

```
LifeThreads/
├── app/                          # Python backend (FastAPI)
│   ├── models.py                 # SQLAlchemy database models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── config.py                 # Configuration (env vars)
│   ├── database.py               # PostgreSQL async session setup
│   ├── main.py                   # FastAPI app initialization
│   ├── tasks.py                  # Celery background tasks
│   ├── task_queue.py             # Celery app configuration
│   ├── background_tasks.py       # One-off background operations
│   ├── routes/                   # API endpoint routes
│   │   ├── __init__.py
│   │   ├── story.py              # Story CRUD endpoints
│   │   ├── search.py             # Search endpoints
│   │   ├── reaction.py           # Like/reaction endpoints
│   │   └── notification.py       # Push notification endpoints
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── story_service.py      # Story operations (create, read, list)
│   │   ├── search_service.py     # Search logic (Meilisearch + fallback)
│   │   ├── reaction_service.py   # Reaction/like logic
│   │   ├── notification_service.py # Notifications
│   │   └── auth_service.py       # Anonymous user authentication
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── ai.py                 # AI functions (moderation, summarization)
│       ├── constants.py          # Constants (categories, error messages)
│       └── validators.py         # Input validation
│
├── frontend/                     # Next.js frontend (TypeScript)
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # Reusable React components
│   ├── lib/                      # Utilities and helpers
│   │   └── firebase.ts           # Firebase Cloud Messaging setup
│   ├── src/                      # Styles and assets
│   ├── public/                   # Static files
│   ├── package.json              # npm dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   ├── next.config.js            # Next.js configuration
│   └── .env.local                # Frontend environment variables
│
├── .env                          # Backend environment variables (PROD)
├── .env.example                  # Env template
├── .env.firebase                 # Firebase configuration
├── requirements-pinned.txt       # Python dependencies (pinned versions)
├── package.json                  # Root package.json (if monorepo)
├── README.md                     # Project README
├── QUICKSTART.md                 # Quick setup guide
├── appDoc.md                     # Architecture documentation
├── PWA_FCM_SETUP.md              # Firebase PWA setup guide
│
├── test_*.py                     # Test scripts
├── verify_config.py              # Config verification script
├── reset_db.py                   # Database reset utility
│
└── venv/                         # Python virtual environment
```

---

## Backend (Python/FastAPI)

### 1. **Main Application** (`app/main.py`)

Initializes FastAPI app with:
```python
- CORS middleware (allow frontend requests)
- Request ID middleware (request tracking)
- Exception handlers (error responses)
- Route registration (story, search, reaction, notification)
- Database initialization (create tables)
- Logging setup
```

**Key Endpoints:**
- GET `/api/v1/health` - Health check
- POST/GET `/api/v1/stories/**` - Story operations
- GET/POST `/api/v1/search/**` - Search operations
- POST `/api/v1/reactions/**` - Reactions
- POST `/api/v1/notifications/**` - Notifications

---

### 2. **Database Models** (`app/models.py`)

#### AnonymousUser
```python
- id (int, PK)
- anonymous_number (str, unique)       # Identifier: "User#ABC123"
- password_hash (str)                  # Hashed password
- is_active (bool)                     # Account status
- created_at (datetime)
- updated_at (datetime)
```

#### Story
```python
- id (int, PK)
- author_id (int, FK)                  # References AnonymousUser
- content (str, 1000+ chars)           # Story text
- summary (str, nullable)              # AI-generated summary
- lessons (str, nullable)              # Extracted life lessons
- category (str)                       # One of 6 categories
- image_url (str, nullable)            # Cover image URL
- is_published (bool)                  # Visibility in feed
- moderation_status (str)              # approved/pending/rejected
- view_count (int)                     # Number of views
- created_at (datetime)
- updated_at (datetime)
```

#### Reaction
```python
- id (int, PK)
- story_id (int, FK)                   # References Story
- reaction_type (str)                  # Type: "like", etc.
- count (int)                          # Reaction count
- created_at (datetime)
```

#### NotificationToken
```python
- id (int, PK)
- user_id (int, FK)                    # References AnonymousUser
- token (str)                          # Firebase FCM token
- is_active (bool)
- created_at (datetime)
```

#### NotificationPreference
```python
- id (int, PK)
- user_id (int, FK)
- receive_digests (bool)               # Daily digest emails
- receive_reactions (bool)             # Reaction notifications
- receive_trending (bool)              # Trending stories
- created_at (datetime)
```

---

### 3. **Schemas (DTOs)** (`app/schemas.py`)

Request/Response models for API validation:

**Story Schemas:**
- `StoryCreateRequest` - Create story with auth
- `PostStoryRequest` - Create story (new or existing user)
- `StoryResponse` - Single story response
- `StoryListItemResponse` - Story list item (snippet + reactions)
- `StoryListResponse` - Paginated story list

**Search Schemas:**
- `SearchRequest` - Search query
- `SearchResponse` - Search results
- `SearchResult` - Individual search result

**Reaction Schemas:**
- `ReactResponse` - Reaction response
- `ReactionCountResponse` - Reaction counts per story

**Notification Schemas:**
- `RegisterTokenRequest` - Push token registration
- `NotificationPreferences` - User notification settings

---

### 4. **Configuration** (`app/config.py`)

Loads environment variables using Pydantic:

```python
# Database
DATABASE_URL = postgresql+asyncpg://user:pass@host/db

# Cache & Queue
REDIS_URL = redis://host:port
CELERY_BROKER_URL = redis result backend

# Search
MEILISEARCH_URL = https://meilisearch-xxxx.railway.app
MEILISEARCH_API_KEY = qz0by0v0vsbkpa58...

# AI Services
OPENAI_API_KEY = sk-...
MODERATION_MODEL = text-moderation-latest

# Firebase
FIREBASE_API_KEY = AIza...
FIREBASE_PROJECT_ID = lifeecho-xxx

# Features
DEBUG = false
LOG_LEVEL = INFO
```

---

### 5. **Database Connection** (`app/database.py`)

Async SQLAlchemy setup:

```python
# Engine
create_async_engine(
    DATABASE_URL,
    echo=False,          # SQL query logging
    pool_size=10,        # Connection pool
    max_overflow=20,
)

# Session Factory
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Initialization
async def init_db():
    # Create all tables
    await conn.run_sync(Base.metadata.create_all)
```

---

### 6. **Routes** (`app/routes/`)

#### Story Routes (`story.py`)

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/v1/stories/post-story` | POST | Create new story | Anonymous user |
| `/api/v1/stories` | POST | Create story (existing auth) | Anonymous number + password |
| `/api/v1/stories` | GET | Get story feed (paginated) | None |
| `/api/v1/stories/{id}` | GET | Get single story | None |
| `/api/v1/stories/{id}` | DELETE | Delete story | Anonymous number + password |

**Query Parameters:**
- `category` - Filter by category
- `sort_by` - Sort order (new, top, trending)
- `limit` - Results per page (1-100)
- `offset` - Pagination offset

#### Search Routes (`search.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/search` | POST | Full-text search (Meilisearch) |
| `/api/v1/search/categories` | GET | Available categories |
| `/api/v1/search/trending` | GET | Trending stories (last 24h) |

**Search Query:**
```json
{
  "query": "hello",
  "category": "Life Lessons",
  "limit": 20,
  "offset": 0
}
```

#### Reaction Routes (`reaction.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/reactions/react` | POST | Add reaction to story |
| `/api/v1/reactions/{story_id}` | GET | Get reaction count |
| `/api/v1/reactions/{story_id}/breakdown` | GET | Get reaction breakdown |

#### Notification Routes (`notification.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/notifications/register-token` | POST | Register FCM token |
| `/api/v1/notifications/unsubscribe` | POST | Unsubscribe from notifications |
| `/api/v1/notifications/top-story-digest` | GET | Get top story digest |
| `/api/v1/notifications/daily-digest` | GET | Get daily digest |
| `/api/v1/notifications/preferences` | GET/PUT | Manage notification preferences |

---

### 7. **Services** (`app/services/`)

#### Story Service (`story_service.py`)

**Methods:**

| Method | Purpose |
|--------|---------|
| `create_story()` | Create story with auth (anonymous_number + password) |
| `post_story()` | Create story (new user auto-generated password, existing user auth) |
| `get_story_feed()` | Get paginated feed with filtering & sorting |
| `get_story()` | Get single story by ID |
| `delete_story()` | Delete story (auth required) |
| `update_story_moderation()` | Update moderation status |

**Flow:**
1. Validate content length & profanity
2. Validate category
3. Authenticate user (hash password, verify)
4. Check content safety (AI moderation)
5. Create Story model
6. Save to PostgreSQL
7. Queue Celery task for post-processing

---

#### Search Service (`search_service.py`)

**Methods:**

| Method | Purpose |
|--------|---------|
| `search_stories()` | Try Meilisearch, fallback to DB |
| `_meilisearch_search()` | Meilisearch search (low-level) |
| `_database_search()` | PostgreSQL LIKE search fallback |
| `search_stories_with_filters()` | Filtered search with full response |
| `_meilisearch_search_with_filters()` | Meilisearch with category/sort |
| `_database_search_with_filters()` | DB search with category/sort |
| `index_story()` | **NEW**: Index story in Meilisearch |
| `delete_story_from_index()` | **NEW**: Remove from Meilisearch |
| `get_trending_stories()` | Stories trending (24h activity) |
| `get_categories()` | List unique categories |

**Meilisearch Document Structure:**
```json
{
  "id": "123",
  "title": "My Life Lesson",
  "content": "Full story content...",
  "category": "Life Lessons"
}
```

---

#### Reaction Service (`reaction_service.py`)

**Methods:**

| Method | Purpose |
|--------|---------|
| `add_reaction()` | Add/increment reaction |
| `get_reaction_count()` | Get reaction count for story |
| `get_reaction_breakdown()` | Count by reaction type |
| `remove_reaction()` | Decrement reaction count |

---

#### Auth Service (`auth_service.py`)

**Methods:**

| Method | Purpose |
|--------|---------|
| `hash_password()` | Hash password with bcrypt |
| `verify_password()` | Verify password hash |
| `generate_random_password()` | Generate random 12-char password |
| `generate_anonymous_number()` | Generate "User#ABC123" identifier |
| `get_user_by_number()` | Fetch user from DB |
| `create_user()` | Create new anonymous user |

---

#### Notification Service (`notification_service.py`)

**Methods:**

| Method | Purpose |
|--------|---------|
| `register_token()` | Store Firebase FCM token |
| `send_push_notification()` | Send push via Firebase |
| `send_digest()` | Send digest email |
| `get_user_preferences()` | Fetch user notification settings |
| `update_preferences()` | Update notification settings |

---

### 8. **Celery Tasks** (`app/tasks.py`)

Background task queue using Celery with Redis broker and threads pool (Windows compatible).

#### Tasks Defined:

**1. process_story_event** (PRIMARY - IMPLEMENTED)
```python
@celery_app.task(name="process_story_event")
def process_story_event(story_id: int, event_type: str):
    """
    Called when: Story published/updated/deleted
    Flow:
    1. If published:
       - Fetch story from DB
       - Index in Meilisearch via SearchService.index_story()
       - Update Meilisearch document
    2. If deleted:
       - Remove from Meilisearch index
    3. If updated:
       - Re-index in Meilisearch
    """
```

**2. moderate_story** (TODO)
```python
# AI content moderation
# Check: profanity, spam, adult content, etc.
```

**3. summarize_story** (TODO)
```python
# Generate AI summary
# Store in Story.summary field
```

**4. extract_story_lessons** (TODO)
```python
# Extract key life lessons from story
# Store in Story.lessons field
```

**5. generate_daily_digest** (SCHEDULED)
```python
# Cron: Every day at 8 AM UTC
# Get top stories, create digest, send notifications
```

**6. cleanup_cache** (SCHEDULED)
```python
# Cron: Every 6 hours
# Remove expired Redis/cache entries
```

**Configuration:**
```python
celery_app.conf.update(
    task_serializer="json",       # Message format
    accept_content=["json"],      # Accept formats
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,      # Track task execution
    task_time_limit=30 * 60,      # 30 min timeout
    worker_pool="threads",        # Windows compatibility!
)
```

**Running Celery Worker:**
```bash
celery -A app.tasks worker -l info --pool=threads
```

---

### 9. **Utilities** (`app/utils/`)

#### AI Functions (`ai.py`)

**Functions:**

| Function | Purpose |
|----------|---------|
| `moderate_content(text)` | Check content safety (OpenAI API) |
| `summarize_story(text)` | Generate summary (OpenAI) |
| `extract_lessons(text)` | Extract key lessons (OpenAI) |

**Models Used:**
- Moderation: `text-moderation-latest`
- Summarization: `gpt-3.5-turbo`
- Extraction: `gpt-3.5-turbo`

---

#### Constants (`constants.py`)

```python
# Valid story categories
VALID_CATEGORIES = [
    "Personal Growth",
    "Relationships",
    "Career",
    "Achievements",
    "Regrets",
    "Life Lessons"
]

# Error messages
ERROR_STORY_NOT_FOUND = "Story not found"
ERROR_USER_NOT_FOUND = "User not found"
ERROR_INVALID_PASSWORD = "Invalid password"
ERROR_CONTENT_TOO_SHORT = "Story too short (min 10 chars)"
ERROR_CONTENT_TOO_LONG = "Story too long (max 5000 chars)"

# Reaction types
REACTION_TYPES = ["like", "love", "support"]
```

---

#### Validators (`validators.py`)

**Functions:**

| Function | Purpose |
|----------|---------|
| `validate_story_content(text)` | Check length & format |
| `validate_category(cat)` | Verify valid category |
| `validate_password(pwd)` | Password strength |
| `validate_anonymous_number(num)` | Format check |

---

### 10. **Configuration & Environment**

**`.env` File:**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@turntable.proxy.rlwy.net:49976/railway

# Cache
REDIS_URL=redis://trolley.proxy.rlwy.net:34074/0

# Search
MEILISEARCH_URL=https://getmeilimeilisearchv190-production-8932.up.railway.app
MEILISEARCH_API_KEY=qz0by0v0vsbkpa58hinlam80x9ryqqjq

# Celery
CELERY_BROKER_URL=redis://trolley.proxy.rlwy.net:34074/1
CELERY_RESULT_BACKEND=redis://trolley.proxy.rlwy.net:34074/2

# OpenAI
OPENAI_API_KEY=sk-...

# Firebase
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=lifeecho-xxx.firebaseapp.com
FIREBASE_PROJECT_ID=lifeecho-xxx
FIREBASE_STORAGE_BUCKET=lifeecho-xxx.appspot.com
FIREBASE_MESSAGING_SENDER_ID=...

# App
DEBUG=False
LOG_LEVEL=INFO
```

---

### 11. **Error Handling & Logging**

**Exception Handlers:**
```python
# 404: Resource not found
# 400: Bad request (validation error)
# 401: Unauthorized (auth failed)
# 403: Forbidden (user inactive)
# 500: Server error (logged for debugging)
```

**Logging:**
```python
# Per-module logger
logger = logging.getLogger(__name__)

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.info(f"Story {id} published")
logger.error(f"DB error: {exc}")
```

---

## Frontend (Next.js/TypeScript)

### 1. **Project Structure**

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout wrapper
│   ├── page.tsx                 # Home page (/)
│   ├── (routes)/                # Route group
│   │   ├── stories/
│   │   │   ├── page.tsx        # Stories list/feed
│   │   │   └── [id]/page.tsx   # Single story view
│   │   ├── post/page.tsx        # Post new story
│   │   └── search/page.tsx      # Search results
│   └── api/                     # API routes (optional)
│
├── components/                  # Reusable React components
│   ├── story/
│   │   ├── StoryCard.tsx       # Story card component
│   │   ├── StoryList.tsx       # Stories grid/list
│   │   └── StoryDetail.tsx     # Full story view
│   ├── search/
│   │   ├── SearchBar.tsx       # Search input
│   │   └── SearchResults.tsx   # Results display
│   ├── common/
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Footer.tsx          # Footer
│   │   └── LoadingSpinner.tsx  # Loader
│   └── auth/
│       ├── LoginModal.tsx      # Login/register
│       └── UserMenu.tsx        # User account menu
│
├── lib/                        # Utilities & helpers
│   ├── api.ts                 # API client (fetch wrapper)
│   ├── firebase.ts            # Firebase Cloud Messaging
│   ├── constants.ts           # Constants
│   └── types.ts               # TypeScript type definitions
│
├── src/                       # Styles & assets
│   ├── styles/
│   │   └── globals.css       # Global styles (Tailwind)
│   └── assets/
│       └── images/           # Images/icons
│
├── public/                    # Static files
│   ├── favicon.ico
│   ├── sw.js                 # Service worker (PWA)
│   └── manifest.json         # PWA manifest
│
├── package.json              # npm dependencies
├── tsconfig.json             # TypeScript config
├── next.config.js            # Next.js config
├── tailwind.config.js        # Tailwind CSS config
├── postcss.config.mjs        # PostCSS config
├── eslint.config.mjs         # ESLint config
└── .env.local                # Local environment variables
```

---

### 2. **Pages (Routing)**

#### Home Page (`app/page.tsx`)
```
Route: /
Purpose: Landing page, story feed
Component: StoryList + SearchBar
Features: Infinite scroll, category filter, sort options
```

#### Stories Page (`app/(routes)/stories/page.tsx`)
```
Route: /stories
Purpose: Full story feed with filters
Component: StoryList with advanced filtering
Query Params: 
  - category
  - sort_by (new, top, trending)
  - page (pagination)
```

#### Single Story (`app/(routes)/stories/[id]/page.tsx`)
```
Route: /stories/:id
Purpose: View full story
Component: StoryDetail
Features: View count, reactions, comments
```

#### Post Story (`app/(routes)/post/page.tsx`)
```
Route: /post
Purpose: Create new story
Component: StoryForm
Features: Anonymous login, category select, content editor
```

#### Search Results (`app/(routes)/search/page.tsx`)
```
Route: /search?q=...
Purpose: Display search results
Component: SearchResults + SearchBar
Features: Filter by category, sort, pagination
```

---

### 3. **Components**

#### Story Components

**StoryCard.tsx**
```typescript
interface StoryCardProps {
  story: Story;
  onReact?: (storyId: number, reaction: string) => void;
}

Features:
- Story snippet (150 chars)
- Category badge
- View count & reaction count
- Click to view full story
```

**StoryList.tsx**
```typescript
interface StoryListProps {
  category?: string;
  sortBy?: 'new' | 'top' | 'trending';
  page?: number;
}

Features:
- Grid/list view toggle
- Infinite scroll pagination
- Loading skeleton
- Empty state handling
```

**StoryDetail.tsx**
```typescript
interface StoryDetailProps {
  storyId: number;
}

Features:
- Full story content
- Author anonymous number
- Created/updated timestamps
- Reaction buttons
- Related stories (sidebar)
```

---

#### Search Components

**SearchBar.tsx**
```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

Features:
- Text input with debounce
- Search suggestions
- Category filter dropdown
- Clear button
```

**SearchResults.tsx**
```typescript
interface SearchResultsProps {
  query: string;
  results: SearchResult[];
  loading?: boolean;
}

Features:
- Display search results
- Result count
- Sort options
- No results message
```

---

#### Common Components

**Header.tsx**
- Navigation menu
- Logo
- Search bar
- User menu (Login/Logout)

**Footer.tsx**
- Links (About, Privacy, Terms)
- Social media
- Copyright

**LoadingSpinner.tsx**
- Animated spinner
- Optional message

---

#### Auth Components

**LoginModal.tsx**
```typescript
Features:
- Input for anonymous_number
- Password input
- Forgot password link
- Register button
- Login button
```

**UserMenu.tsx**
```typescript
Features:
- Display user (User#ABC123)
- My Stories link
- Settings link
- Logout button
```

---

### 4. **Libraries & Utilities**

#### API Client (`lib/api.ts`)

```typescript
// Wrapper around fetch with:
// - Base URL configuration
// - Error handling
// - Request/response interceptors
// - Auth token management
// - Retry logic

export async function fetchStories(
  category?: string,
  sortBy?: string,
  limit?: number,
  offset?: number
): Promise<StoryListResponse> {
  return api.get('/stories', { 
    params: { category, sortBy, limit, offset } 
  });
}

export async function postStory(
  content: string,
  category: string,
  imageUrl?: string
): Promise<PostStoryResponse> {
  return api.post('/stories/post-story', {
    content,
    category,
    image_url: imageUrl
  });
}

export async function searchStories(
  query: string,
  category?: string,
  limit?: number
): Promise<SearchResponse> {
  return api.post('/search', { query, category, limit });
}

export async function addReaction(
  storyId: number,
  reactionType: string
): Promise<ReactResponse> {
  return api.post(`/reactions/react`, {
    story_id: storyId,
    reaction_type: reactionType
  });
}
```

---

#### Firebase (`lib/firebase.ts`)

```typescript
// Firebase Cloud Messaging for push notifications

export const initializeFirebase = (): FirebaseApp => {
  // Initialize Firebase with config from env vars
};

export const getFirebaseMessaging = (): Messaging => {
  // Get messaging instance (creates if needed)
  // Checks for service worker support
};

// Usage:
// 1. Call initializeFirebase() on app startup
// 2. Request notification permission
// 3. Get token and send to backend /notifications/register-token
// 4. Receive push notifications in browser
```

---

#### Types (`lib/types.ts`)

```typescript
interface Story {
  id: number;
  content: string;
  summary?: string;
  lessons?: string;
  category: string;
  image_url?: string;
  view_count: number;
  reactions_count: number;
  created_at: string;
  updated_at: string;
}

interface StoryListResponse {
  total: number;
  limit: number;
  offset: number;
  stories: StoryListItemResponse[];
}

interface StoryListItemResponse {
  id: number;
  snippet: string;        // First 150 chars
  category: string;
  media_url?: string;
  reactions_count: number;
  summary?: string;
  lessons?: string;
  created_at: string;
  view_count: number;
}

interface SearchResult {
  id: number;
  content: string;
  category: string;
  created_at: string;
  view_count: number;
}

interface PostStoryResponse {
  success: boolean;
  message: string;
  story_id: number;
  anonymous_number: string;
  password?: string;  // Only for new users
}

interface ReactResponse {
  success: boolean;
  reactions_count: number;
}
```

---

### 5. **Configuration Files**

#### `tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

#### `next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { hostname: '**.railway.app' },
      { hostname: 'firebasestorage.googleapis.com' }
    ]
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    // ... more configs
  }
};

module.exports = nextConfig;
```

#### `tailwind.config.js`
```javascript
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        // Custom color palette
      }
    }
  },
  plugins: []
};
```

---

### 6. **PWA & Service Worker**

#### Manifest (`public/manifest.json`)
```json
{
  "name": "LifeEcho - Share Your Stories",
  "short_name": "LifeEcho",
  "description": "Anonymous story sharing platform",
  "start_url": "/",
  "display": "standalone",
  "scope": "/",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "background_color": "#ffffff",
  "theme_color": "#000000"
}
```

#### Service Worker (`public/sw.js`)
```javascript
// Handles:
// - Offline caching
// - Background sync
// - Push notifications (Firebase FCM)
// - Periodic sync for daily digest
```

---

### 7. **Environment Variables**

**`.env.local`:**
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
# or production: https://lifeecho-backend.railway.app/api/v1

# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lifeecho-xxx.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lifeecho-xxx
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lifeecho-xxx.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=1:...:web:...
```

---

## Database & External Services

### 1. **PostgreSQL Database** (Railway)

**Connection:** `postgresql+asyncpg://username:password@turntable.proxy.rlwy.net:49976/railway`

**Tables:**
- `anonymous_users` - User accounts
- `stories` - Story content & metadata
- `reactions` - Likes/reactions
- `notification_tokens` - Firebase FCM tokens
- `notification_preferences` - User settings

**Indexes:**
```sql
CREATE INDEX idx_story_author ON stories(author_id);
CREATE INDEX idx_story_published ON stories(is_published);
CREATE INDEX idx_story_category ON stories(category);
CREATE INDEX idx_story_created_at ON stories(created_at DESC);
CREATE INDEX idx_reaction_story ON reactions(story_id);
CREATE INDEX idx_token_user ON notification_tokens(user_id);
```

---

### 2. **Redis** (Railway)

**Connection:** `redis://trolley.proxy.rlwy.net:34074/0`

**Usage:**
- **DB 0**: Cache (session data, story counts)
- **DB 1**: Celery broker (task queue)
- **DB 2**: Celery result backend (task results)

**Keys:**
```
story:{id}:reactions - Reaction count cache
user:{id}:tokens - User notification tokens
celery-task:{id} - Celery task status
cache:trending:24h - Trending stories cache
```

---

### 3. **Meilisearch** (Railway)

**URL:** `https://getmeilimeilisearchv190-production-8932.up.railway.app`  
**API Key:** `qz0by0v0vsbkpa58hinlam80x9ryqqjq`

**Index:** `stories`

**Documents:**
```json
{
  "id": "123",
  "title": "My Story Title",
  "content": "Full story content with all details...",
  "category": "Life Lessons",
  "created_at": "2026-03-31T10:00:00Z",
  "view_count": 42
}
```

**Searchable Fields:**
- `title` (weighted higher)
- `content`
- `category`

**Filtering:**
```
category = "Life Lessons"
OR
view_count >= 10
```

**Indexing Workflow:**
1. Story created in PostgreSQL
2. If safe (moderation passes), `is_published = true`
3. Celery task `process_story_event("published")` queued
4. Celery worker fetches story from DB
5. Celery calls `SearchService.index_story()` to add to Meilisearch
6. Story now appears in search results

---

### 4. **Firebase** (Google)

**Project:** `lifeecho-xxx`

**Features Used:**
- **Cloud Messaging (FCM)** - Push notifications
- **Authentication** (optional) - OAuth signin
- **Storage** (optional) - Story images

**Setup:**
1. Create Firebase project
2. Generate web app credentials
3. Enable Cloud Messaging
4. Frontend requests notification permission
5. Frontend gets FCM token
6. Frontend sends token to `/notifications/register-token`
7. Backend stores token in DB
8. Backend sends notifications via Firebase API

---

### 5. **OpenAI API**

**Models Used:**
- `text-moderation-latest` - Content moderation
- `gpt-3.5-turbo` - Summarization & lesson extraction

**Calls Made:**
1. **Moderation:** Check if story content is safe
   - Returns: `{"is_safe": true/false, "reason": "..."}`
2. **Summarization:** Generate story summary
   - Prompt: "Summarize this story in 1-2 sentences"
3. **Lesson Extraction:** Extract life lessons
   - Prompt: "What life lessons are in this story?"

---

## API Reference

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://lifeecho-backend.railway.app/api/v1
```

### Authentication

**Anonymous User Flow:**
```
1. POST /stories/post-story
   Request:
   {
     "content": "My story...",
     "category": "Life Lessons",
     "image_url": null
   }
   Response:
   {
     "success": true,
     "story_id": 123,
     "anonymous_number": "User#XYZ789",
     "password": "RandomPass123"  // Save this!
   }

2. For future stories, include credentials:
   POST /stories
   Headers:
     X-Anonymous-Number: User#XYZ789
     X-Password: RandomPass123
   Request:
   {
     "content": "Another story...",
     "category": "Career"
   }
```

---

### Stories API

#### Get Story Feed
```
GET /stories?category=Life Lessons&sort_by=new&limit=20&offset=0

Query Params:
- category (optional): Filter by category
- sort_by (new|top|trending): Sort order
- limit (1-100): Results per page
- offset (0+): Pagination offset

Response:
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "stories": [
    {
      "id": 123,
      "snippet": "My life story about...",
      "category": "Life Lessons",
      "media_url": null,
      "reactions_count": 5,
      "summary": null,
      "lessons": null,
      "created_at": "2026-03-31T10:00:00Z",
      "view_count": 42
    }
  ]
}
```

#### Get Single Story
```
GET /stories/123

Response:
{
  "id": 123,
  "content": "Full story content...",
  "category": "Life Lessons",
  "image_url": null,
  "author": "User#XYZ789",
  "is_published": true,
  "moderation_status": "approved",
  "view_count": 42,
  "reactions_count": 5,
  "created_at": "2026-03-31T10:00:00Z",
  "updated_at": "2026-03-31T10:00:00Z"
}
```

#### Create Story (New User)
```
POST /stories/post-story

Request:
{
  "content": "My first story about personal growth...",
  "category": "Personal Growth",
  "image_url": "https://..."
}

Response:
{
  "success": true,
  "message": "Story posted successfully",
  "story_id": 123,
  "anonymous_number": "User#ABC123",
  "password": "GeneratedPass123"
}
```

#### Delete Story
```
DELETE /stories/123

Headers:
  X-Anonymous-Number: User#ABC123
  X-Password: Pass123

Response:
{
  "success": true,
  "message": "Story deleted successfully"
}
```

---

### Search API

#### Full-Text Search
```
POST /search

Request:
{
  "query": "hello world",
  "category": "Life Lessons",
  "limit": 20,
  "offset": 0
}

Response:
{
  "query": "hello world",
  "total": 5,
  "results": [
    {
      "id": 123,
      "content": "Hello world! My story...",
      "category": "Life Lessons",
      "created_at": "2026-03-31T10:00:00Z",
      "view_count": 42
    }
  ],
  "limit": 20,
  "offset": 0
}
```

#### Get Categories
```
GET /search/categories

Response:
[
  "Personal Growth",
  "Relationships",
  "Career",
  "Achievements",
  "Regrets",
  "Life Lessons"
]
```

#### Get Trending Stories
```
GET /search/trending?limit=10

Query Params:
- limit (1-100): Number of stories

Response:
[
  {
    "id": 123,
    "content": "Trending story...",
    "category": "Life Lessons",
    "created_at": "2026-03-31T08:00:00Z",
    "view_count": 150
  }
]
```

---

### Reactions API

#### React to Story
```
POST /reactions/react

Request:
{
  "story_id": 123,
  "reaction_type": "like"
}

Response:
{
  "success": true,
  "reactions_count": 6
}
```

#### Get Reaction Count
```
GET /reactions/123

Response:
{
  "story_id": 123,
  "reactions_count": 5
}
```

#### Get Reaction Breakdown
```
GET /reactions/123/breakdown

Response:
{
  "story_id": 123,
  "like": 5,
  "love": 2,
  "support": 1,
  "total": 8
}
```

---

### Notifications API

#### Register Token
```
POST /notifications/register-token

Request:
{
  "anonymous_number": "User#ABC123",
  "token": "firebase_fcm_token_here"
}

Response:
{
  "success": true,
  "message": "Token registered successfully"
}
```

#### Get Preferences
```
GET /notifications/preferences?user_id=1

Response:
{
  "receive_digests": true,
  "receive_reactions": true,
  "receive_trending": true
}
```

#### Update Preferences
```
PUT /notifications/preferences

Request:
{
  "receive_digests": false,
  "receive_reactions": true,
  "receive_trending": false
}

Response:
{
  "success": true,
  "preferences": { ... }
}
```

---

## Configuration

### 1. Environment Variables

**Backend (`.env`):**

```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:pass@turntable.proxy.rlwy.net:49976/railway

# Cache & Queue (Railway Redis)
REDIS_URL=redis://trolley.proxy.rlwy.net:34074/0
CELERY_BROKER_URL=redis://trolley.proxy.rlwy.net:34074/1
CELERY_RESULT_BACKEND=redis://trolley.proxy.rlwy.net:34074/2

# Search (Railway Meilisearch)
MEILISEARCH_URL=https://getmeilimeilisearchv190-production-8932.up.railway.app
MEILISEARCH_API_KEY=qz0by0v0vsbkpa58hinlam80x9ryqqjq

# AI Services (OpenAI)
OPENAI_API_KEY=sk-proj-...

# Firebase (Google Cloud)
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=lifeecho-xxx.firebaseapp.com
FIREBASE_PROJECT_ID=lifeecho-xxx
FIREBASE_STORAGE_BUCKET=lifeecho-xxx.appspot.com
FIREBASE_MESSAGING_SENDER_ID=...

# App Settings
DEBUG=False
LOG_LEVEL=INFO
DATABASE_ECHO=False
CORS_ORIGINS=["http://localhost:3000", "https://lifeecho-frontend.vercel.app"]
```

**Frontend (`.env.local`):**

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Firebase (Client-side)
NEXT_PUBLIC_FIREBASE_API_KEY=AIza...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lifeecho-xxx.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=lifeecho-xxx
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=lifeecho-xxx.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=1:...:web:...
```

---

### 2. Python Dependencies

**Key Packages (`requirements-pinned.txt`):**

```
# Web Framework
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.48
asyncpg==0.29.0
alembic==1.13.0

# Task Queue
celery==5.3.4
redis==5.0.1

# Search
meilisearch==0.31.1

# API Clients
httpx==0.25.1
requests==2.31.0
openai==1.3.6

# Auth & Security
bcrypt==4.1.1
python-jose==3.3.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2

# Logging & Monitoring
structlog==23.3.0

# Testing
pytest==7.4.4
pytest-asyncio==0.21.1
```

---

### 3. Development Setup

**Step 1: Clone Repository**
```bash
git clone https://github.com/yourusername/lifeecho.git
cd lifeecho
```

**Step 2: Backend Setup**
```bash
# Create Python venv
python -m venv venv

# Activate venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-pinned.txt

# Copy .env.example to .env and update values
cp .env.example .env

# Initialize database
python reset_db.py

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Celery Worker**
```bash
# In new terminal, activate venv
celery -A app.tasks worker -l info --pool=threads
```

**Step 4: Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Copy .env.example to .env.local
cp .env.example .env.local

# Start dev server
npm run dev
```

**URLs:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

### 4. Database Migrations (Alembic)

```bash
# Generate migration after model changes
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Deployment

### 1. Railway Deployment

**Backend:**
```bash
# Push to Railway (automated from Git)
git push railway main

# Or manual deployment
railway up

# View logs
railway logs
```

**Frontend (Vercel):**
```bash
# Connect GitHub repo to Vercel
# Auto-deploys on push

# Manual deployment
vercel deploy --prod
```

---

### 2. Environment Setup on Railway

1. Create PostgreSQL database
2. Create Redis cache
3. Create Meilisearch instance
4. Set all `.env` variables in Railway project settings
5. Deploy Python backend
6. Deploy Next.js frontend
7. Update CORS_ORIGINS to point to production frontend URL

---

### 3. Production Checklist

- [ ] Database backups enabled
- [ ] Redis persistence enabled
- [ ] Error logging configured (Sentry/etc)
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] SSL/TLS certificates installed
- [ ] Environment variables all set
- [ ] Database migrations applied
- [ ] Celery worker running
- [ ] Firebase configured for production
- [ ] OpenAI API key valid
- [ ] Testing completed
- [ ] Monitoring/alerting setup

---

## Development Guide

### 1. Adding a New Feature

**Example: Add story tags**

**Step 1: Database Model**
```python
# app/models.py
class Story:
    tags: Mapped[list[str]] = mapped_column(String[], nullable=True)
```

**Step 2: Schema**
```python
# app/schemas.py
class StoryCreateRequest(BaseModel):
    tags: list[str] = []
```

**Step 3: Service Logic**
```python
# app/services/story_service.py
story.tags = story_data.tags
```

**Step 4: API Route**
```python
# app/routes/story.py
# Update POST endpoint to accept tags
```

**Step 5: Frontend Component**
```typescript
// frontend/components/story/TagInput.tsx
// Add tag input field
```

**Step 6: Migration**
```bash
alembic revision --autogenerate -m "Add story tags"
alembic upgrade head
```

---

### 2. Testing Workflow

**Backend Tests:**
```bash
pytest tests/

# Test specific file
pytest tests/test_story_service.py

# Run with coverage
pytest --cov=app tests/
```

**Frontend Tests:**
```bash
cd frontend
npm test

# Watch mode
npm test -- --watch
```

---

### 3. Debugging

**Backend:**
```python
# Add print statements
print(f"DEBUG: Story {id} = {story}")

# Or use logger
logger.debug(f"Story {id} = {story}")

# Use debugger
import pdb; pdb.set_trace()
```

**Frontend:**
```typescript
console.log('DEBUG:', value);
debugger;  // Breakpoint
```

---

### 4. Common Issues

**Issue: Celery tasks not running**
```bash
# Check worker is running
celery -A app.tasks worker -l debug

# Check Redis connection
redis-cli ping  # Should return PONG

# Check logs for errors
```

**Issue: Search returns empty results**
```python
# Verify Meilisearch is online
meilisearch_client.health()

# Check if stories are indexed
meilisearch_client.index('stories').get_stats()

# Manually index a story
from app.services.search_service import SearchService
SearchService.index_story(123, "Story Title", "Content...", "Category")
```

**Issue: Frontend can't connect to backend**
```bash
# Check CORS configuration in app/main.py
# Verify .env.local has correct NEXT_PUBLIC_API_URL
# Check backend is running on :8000
# Check no proxy issues
```

---

## Project Status & Roadmap

### ✅ Completed
- FastAPI backend setup
- PostgreSQL database connection
- Celery task queue with threads pool
- Story CRUD operations
- Anonymous user authentication
- Basic story feed
- Database LIKE search fallback
- Firebase notifications setup
- React system

### 🟡 In Progress
- Meilisearch full-text search integration
  - ✅ Infrastructure deployed on Railway
  - ✅ Celery indexing task implemented
  - 🔄 Testing search results
  - 🔄 Debugging empty results issue

### ⏳ Pending
- [ ] OpenAI content moderation
- [ ] Story summarization
- [ ] Life lessons extraction
- [ ] Daily digest generation
- [ ] Push notifications frontend
- [ ] Frontend components (post form, story cards, etc)
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance optimization
- [ ] Security audit
- [ ] SEO optimization

---

## Key Constants

```python
# Story categories
VALID_CATEGORIES = [
    "Personal Growth",
    "Relationships",
    "Career",
    "Achievements",
    "Regrets",
    "Life Lessons"
]

# Content limits
MIN_STORY_LENGTH = 10  # characters
MAX_STORY_LENGTH = 5000  # characters

# Pagination
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
DEFAULT_OFFSET = 0

# Reaction types
REACTION_TYPES = ["like", "love", "support"]

# Task timeouts
CELERY_TASK_TIMEOUT = 30 * 60  # 30 minutes
```

---

## Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Invalid category | Category not in VALID_CATEGORIES |
| 400 | Content too short | < 10 characters |
| 400 | Content too long | > 5000 characters |
| 401 | Invalid password | Password hash doesn't match |
| 403 | User account inactive | User.is_active == False |
| 404 | Story not found | Story ID doesn't exist |
| 404 | User not found | Anonymous number doesn't exist |
| 500 | Server error | Uncaught exception |

---

## Contact & Support

For issues or questions:
- GitHub Issues: [link]
- Email: support@lifeecho.app
- Discord: [link]

---

**Document Version**: 1.0  
**Last Updated**: March 31, 2026  
**Maintained By**: Development Team
