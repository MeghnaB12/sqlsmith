"""FastAPI dependency providers."""

from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import User
from app.db.session import get_db
from app.security import decode_access_token
from app.sql.generator import AnthropicSQLGenerator, SQLGenerator, StubSQLGenerator

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_generator() -> SQLGenerator:
    """Provide the configured SQL generator."""
    settings = get_settings()
    if settings.generator_provider == "anthropic":
        return AnthropicSQLGenerator(settings.anthropic_api_key, settings.sql_model)
    return StubSQLGenerator()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the authenticated user from a bearer token."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="valid bearer token required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        user_id = decode_access_token(credentials.credentials)
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise unauthorized from exc

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user
