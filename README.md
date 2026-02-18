# Twitter API Service

RESTful API service for Twitter API v2, showcasing software architecture principles and design patterns.

## 🎯 Purpose

Demonstrates:
- **Clean Architecture** with strict layer separation
- **SOLID principles** and design patterns
- **Production-ready** backend structure
- **Async Python** best practices

## ✨ Key Features

- Clean Architecture with 4 layers (Core, Application, Infrastructure, Presentation)
- Custom Twitter API v2 client (no SDK)
- Async/await throughout
- Repository & Strategy patterns
- Pluggable caching (Memory/Redis)
- Rate limiting with retry logic
- 49 tests with 79% coverage

## 🏗️ Architecture

Clean Architecture with strict layer separation and dependency inversion:

```
┌─────────────────────────────────────┐
│   Presentation (FastAPI)            │  ← API endpoints, middleware
├─────────────────────────────────────┤
│   Application (Use Cases)           │  ← Business logic
├─────────────────────────────────────┤
│   Infrastructure (External)         │  ← TwitterClient, Cache, HTTP
├─────────────────────────────────────┤
│   Core (Domain)                     │  ← Entities, Interfaces, Exceptions
└─────────────────────────────────────┘
```

**Dependency Rule**: Dependencies flow inward only. Core has zero external dependencies.


## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/leeinprogress/twitter-apis.git
cd twitter-api-service
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your TWITTER_BEARER_TOKEN

# Run
uvicorn app.main:app --reload
```

**Docker:**
```bash
docker-compose up --build
```

**API Docs:** http://localhost:8000/docs

**Testing:**
```bash
pytest --cov=app
```


## 📁 Project Structure

```
app/
├── core/                   # Domain layer (entities, interfaces, exceptions)
├── application/            # Use cases (TweetService)
├── infrastructure/         # External services (TwitterClient, Cache, HTTP)
├── presentation/           # API layer (FastAPI endpoints, middleware)
├── bootstrap/              # App initialization (factory, config, DI)
└── utils/                  # Shared utilities (decorators, logging)

tests/
├── unit/                   # 41 unit tests
└── integration/            # 8 integration tests
```


## 💡 Technical Highlights

**Custom Twitter Client**: Built from scratch using `aiohttp` for learning purposes
- No SDK dependency
- Bearer token authentication
- Rate limiting (12-100 req/min)
- Retry with exponential backoff

**Design Patterns**:
- Factory, Repository, Strategy, Decorator
- Dependency Injection throughout
- Interface-based abstractions

**Caching**: Pluggable strategy (Memory/Redis)
```python
cache: ICacheService = RedisCacheService() if settings.redis_enabled else InMemoryCacheService()
```


## 🎯 Use Cases

- Learning Clean Architecture in Python
- Understanding SOLID principles through real code
- Backend interview preparation
- Reference implementation for new projects

## 📝 License

MIT

