"""Text-to-SQL endpoint: question in, validated SQL (and rows) out."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings
from app.db import sandbox
from app.dependencies import get_generator
from app.schemas.query import QueryRequest, QueryResponse
from app.sql.generator import SQLGenerator
from app.sql.safety import UnsafeSQLError, ensure_read_only

router = APIRouter(prefix="/v1", tags=["query"])


@router.post("/query")
async def query(
    request: QueryRequest,
    generator: Annotated[SQLGenerator, Depends(get_generator)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> QueryResponse:
    """Generate SQL for a question, validate it's read-only, and run it."""
    con = sandbox.new_connection()
    try:
        schema = sandbox.describe_schema(con)
        raw_sql = await generator.generate_sql(request.question, schema)

        try:
            safe_sql = ensure_read_only(raw_sql, max_rows=settings.max_rows)
        except UnsafeSQLError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"unsafe SQL rejected: {exc}",
            ) from exc

        rows = sandbox.run_query(con, safe_sql) if request.execute else []
        return QueryResponse(sql=safe_sql, rows=rows, row_count=len(rows))
    finally:
        con.close()
