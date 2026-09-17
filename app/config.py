"""Application settings loaded from environment / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "sqlsmith"
    environment: str = "local"
    log_level: str = "INFO"

    # Which SQL generator to use: "stub" (no key, deterministic) or "anthropic".
    generator_provider: str = "stub"
    anthropic_api_key: str = ""
    sql_model: str = "claude-sonnet-4-5"

    # Safety: hard cap on rows returned from the sandbox.
    max_rows: int = 100

    # Product persistence. PostgreSQL is the production/local-compose target;
    # SQLite remains useful for deterministic tests and lightweight local runs.
    database_url: str = "sqlite:///./sqlsmith.db"

    # Authentication.
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24

    # Browser client origins, comma separated.
    cors_origins: str = "http://localhost:3000"

    @property
    def allowed_origins(self) -> list[str]:
        """Return normalized browser origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
