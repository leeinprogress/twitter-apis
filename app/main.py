"""Twitter API Service - Main Application"""

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="Twitter API Service",
    description="RESTful API for fetching tweets from Twitter",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Twitter API Service",
        "version": "1.0.0"
    }
