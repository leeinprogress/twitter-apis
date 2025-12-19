from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    debug: bool
    host: str
    port: int = Field(ge=1, le=65535)

    twitter_bearer_token: str
    twitter_api_base_url: str
    twitter_max_results: int = Field(ge=10, le=100)
    twitter_request_timeout: int = Field(ge=5, le=60)

    cache_enabled: bool
    cache_ttl: int = Field(ge=0, le=3600)
    redis_url: str
    redis_enabled: bool

    log_level: str
    log_format: str

    cors_origins: str

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        if v not in ["json", "console"]:
            raise ValueError("log_format must be 'json' or 'console'")
        return v

    @field_validator("twitter_bearer_token")
    @classmethod
    def validate_bearer_token(cls, v: str) -> str:
        if v and len(v) < 10:
            raise ValueError("twitter_bearer_token seems invalid (too short)")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins or self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        from app.bootstrap.env import load_environment
        env_vars = load_environment()
        _settings = Settings(**env_vars)
    return _settings
