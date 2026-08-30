"""FastAPI dependency providers."""

from functools import lru_cache

from app.config import get_settings
from app.sql.generator import AnthropicSQLGenerator, SQLGenerator, StubSQLGenerator


@lru_cache
def get_generator() -> SQLGenerator:
    """Provide the configured SQL generator."""
    settings = get_settings()
    if settings.generator_provider == "anthropic":
        return AnthropicSQLGenerator(settings.anthropic_api_key, settings.sql_model)
    return StubSQLGenerator()
