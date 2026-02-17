# Twitter API Service

RESTful API service for fetching tweets from Twitter API v2.

##  Features

### RESTful API Endpoints

1. **GET /api/v1/hashtags/{hashtag}** - Fetch tweets by hashtag
2. **GET /api/v1/users/{username}** - Fetch user timeline tweets

### Technical Highlights

- **Clean Architecture** with clear separation of concerns (Core, Application, Infrastructure, Presentation)
- **Custom Twitter API v2 client** (no external SDK used, as per requirements)
- **Async/await** throughout for high performance
- **Error handling** with custom exception hierarchy
- **Middleware** for logging and error handling
- **Caching** support (Memory/Redis)
- **Rate limiting** with retry logic
- **Comprehensive testing** with 49 tests (41 unit + 8 integration) achieving 79% code coverage

##  Architecture

Clean Architecture with 4 layers:

```
┌─────────────────────────────────────┐
│   Presentation (FastAPI)            │  ← API endpoints, middleware
├─────────────────────────────────────┤
│   Application (Use Cases)           │  ← TweetService (business logic)
├─────────────────────────────────────┤
│   Infrastructure (External)         │  ← TwitterClient, Cache, HTTP
├─────────────────────────────────────┤
│   Core (Domain)                     │  ← Entities, Interfaces, Exceptions
└─────────────────────────────────────┘
```


##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/leeinprogress/anymind-twitter-apis.git
cd anymind-twitter-apis
```

### 2. Create virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your Twitter Bearer Token:

```env
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```


##  Running

### Local Development

```bash
# Using uvicorn (recommended for development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Make
make run

# Or using Python module
python -m app.main
```

The service will be available at: `http://localhost:8000`

### Docker Development

```bash
# Build and run with Docker Compose
make docker-build
make docker-run

# Or directly
docker-compose up --build

# Stop services
docker-compose down
```

**Redis Support (Optional):**

By default, the application uses in-memory caching. To enable Redis caching:

1. Set `REDIS_ENABLED=true` in your `.env` file or in `docker-compose.yml`
2. Start both app and Redis services:

```bash
docker-compose up
```

The Redis service will be available on port 6379.


##  API Documentation

### Interactive Documentation

After starting the service:

- **Swagger UI**: http://localhost:8000/docs (interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (clean documentation)


##  Testing

### Run All Tests

```bash
# Using Make
make test

# Or directly with pytest
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=html
pytest --cov=app --cov-report=term-missing
```


##  Project Structure

```
anymind-twitter-apis/
├── app/
│   ├── core/                   # Domain layer
│   │   ├── entities.py        # Tweet, Account entities
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── interfaces.py      # Abstract interfaces
│   ├── application/           # Business logic layer
│   │   └── services.py        # TweetService
│   ├── infrastructure/        # External services layer
│   │   ├── twitter/
│   │   │   ├── client.py      # Twitter API client
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── mapper.py      # API response mapping
│   │   │   └── rate_limiter.py
│   │   ├── cache/
│   │   │   └── cache_service.py
│   │   └── http/
│   │       └── client.py      # HTTP client factory
│   ├── presentation/          # API layer
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── v1/
│   │   │       ├── hashtags.py
│   │   │       └── users.py
│   │   ├── middleware/
│   │   │   ├── error_handler.py
│   │   │   └── logging.py
│   │   └── schemas/
│   │       ├── common.py
│   │       └── tweet.py
│   ├── bootstrap/             # App initialization
│   │   ├── app_factory.py    # App factory pattern
│   │   ├── config.py         # Settings with validation
│   │   ├── env.py            # Environment loading
│   │   ├── lifecycle.py      # Startup/shutdown handlers
│   │   ├── middleware.py     # Middleware setup
│   │   └── routes.py         # Route setup
│   ├── utils/                # Utilities
│   │   ├── decorators.py     # Retry & timing decorators
│   │   └── logger.py         # Logging configuration
│   └── main.py               # Application entry point
├── tests/
│   ├── unit/                 # 41 unit tests
│   ├── integration/          # 8 integration tests
│   └── fixtures/            # Test data
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```


##  Key Implementation Details

### Custom Twitter API Client

As per project requirements, this project implements its own Twitter API v2 client without using official Twitter SDK:

- Direct HTTP calls to Twitter API v2
- Custom authentication with Bearer Token
- Manual response parsing and mapping
- Error handling for all API error codes
- Rate limiting based on Twitter API limits

### Rate Limiting

Implements client-side rate limiting to prevent API quota exhaustion:

- **Search tweets**: 12 requests/minute
- **Get user**: 20 requests/minute
- **User timeline**: 100 requests/minute

Includes retry mechanism with exponential backoff for failed requests.

### Caching

Optional caching to improve performance and reduce API calls:

- In-memory cache (default)
- Redis cache (when `REDIS_ENABLED=true`)
- Configurable TTL (default: 300 seconds)


##  API Usage Examples

### Search Tweets by Hashtag

```bash
# Basic request
curl http://localhost:8000/api/v1/hashtags/Python

# With limit
curl http://localhost:8000/api/v1/hashtags/Python?limit=50

# With Accept header
curl -H "Accept: application/json" http://localhost:8000/api/v1/hashtags/Python?limit=40
```


### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Get User Timeline

```bash
# Basic request
curl http://localhost:8000/api/v1/users/twitter

# With limit
curl http://localhost:8000/api/v1/users/twitter?limit=20

# With Accept header
curl -H "Accept: application/json" http://localhost:8000/api/v1/users/twitter?limit=20
```

##  Development Commands

### Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make run           # Run the application
make test          # Run all tests with coverage
make test-unit     # Run unit tests only
make test-int      # Run integration tests only
make lint          # Run linter (ruff)
make format        # Format code with ruff
make clean         # Clean cache and build files
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
```

##  License

MIT

