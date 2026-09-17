"""Tests for the authenticated /v1/query endpoint (using the stub generator)."""

from httpx import AsyncClient


async def test_query_requires_authentication(client: AsyncClient) -> None:
    response = await client.post("/v1/query", json={"question": "list customers"})
    assert response.status_code == 401


async def test_query_returns_sql_and_rows(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/v1/query", json={"question": "list customers"}, headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sql"].upper().startswith("SELECT")
    assert body["row_count"] == len(body["rows"])
    assert body["row_count"] > 0

    history = await client.get("/v1/history", headers=auth_headers)
    assert history.status_code == 200
    assert history.json()[0]["question"] == "list customers"
    assert history.json()[0]["row_count"] == body["row_count"]


async def test_query_can_skip_execution(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post(
        "/v1/query",
        json={"question": "list customers", "execute": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == []
    assert body["row_count"] == 0

    history = await client.get("/v1/history", headers=auth_headers)
    assert history.json()[0]["executed"] is False


async def test_empty_question_is_rejected(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.post("/v1/query", json={"question": ""}, headers=auth_headers)
    assert response.status_code == 422
