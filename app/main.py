"""Application factory and FastAPI instance."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, history, query
from app.config import get_settings
from app.db.models import Base
from app.db.session import get_engine
from app.observability import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize logging and product persistence on startup."""
    settings = get_settings()
    configure_logging(settings.log_level)
    Base.metadata.create_all(bind=get_engine())
    yield


def create_app() -> FastAPI:
    """Build and return a configured FastAPI application."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(query.router)
    app.include_router(history.router)
    return app


app = create_app()
