"""Schemas for the text-to-SQL endpoint."""

from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """A natural-language question against the sandbox database."""

    question: str = Field(..., min_length=1, max_length=1000)
    execute: bool = Field(default=True, description="Run the SQL, or just return it.")


class QueryResponse(BaseModel):
    """The generated SQL and (optionally) its results."""

    sql: str
    rows: list[dict[str, Any]]
    row_count: int
