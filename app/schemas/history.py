"""Persistent query history schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QueryHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    sql: str
    executed: bool
    row_count: int
    created_at: datetime
