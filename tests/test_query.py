"""Tests for the /v1/query endpoint (using the stub generator)."""

from httpx import AsyncClient


async def test_query_returns_sql_and_rows(client: AsyncClient) -> None:
    response = await client.post("/v1/query", json={"question": "list customers"})
    assert response.status_code == 200
    body = response.json()
    assert body["sql"].upper().startswith("SELECT")
    assert body["row_count"] == len(body["rows"])
    assert body["row_count"] > 0


async def test_query_can_skip_execution(client: AsyncClient) -> None:
    response = await client.post("/v1/query", json={"question": "list customers", "execute": False})
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == []
    assert body["row_count"] == 0


async def test_empty_question_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/v1/query", json={"question": ""})
    assert response.status_code == 422
