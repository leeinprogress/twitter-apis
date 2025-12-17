# Twitter API Service

A RESTful API service for fetching tweets from Twitter API v2.

## Features

- Search tweets by hashtag
- Get user timeline tweets
- Twitter API v2 integration

## Requirements

- Python 3.12+
- Twitter API Bearer Token

## Installation

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Add your Twitter API credentials to `.env`.

## Running the Application

```bash
# Development mode
uvicorn app.main:app --reload

# Or use Make
make run
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT

