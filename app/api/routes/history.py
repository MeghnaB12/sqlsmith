"""Authenticated query-history endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import QueryHistory, User
from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.history import QueryHistoryItem

router = APIRouter(prefix="/v1/history", tags=["history"])


@router.get("", response_model=list[QueryHistoryItem])
def list_history(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[QueryHistoryItem]:
    """Return the current user's most recent queries first."""
    items = db.scalars(
        select(QueryHistory)
        .where(QueryHistory.user_id == user.id)
        .order_by(QueryHistory.created_at.desc())
        .limit(100)
    ).all()
    return [QueryHistoryItem.model_validate(item) for item in items]
