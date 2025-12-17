"""Application configuration"""

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings"""
    
    # Application
    debug: bool
    host: str
    port: int = Field(ge=1, le=65535)
    
    # Twitter API
    twitter_bearer_token: str
    twitter_api_base_url: str


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        from app.bootstrap.env import load_environment
        env_vars = load_environment()
        _settings = Settings(**env_vars)
    return _settings
