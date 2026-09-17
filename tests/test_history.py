"""Persistent query-history authorization tests."""

from httpx import AsyncClient


async def _register(client: AsyncClient, email: str) -> dict[str, str]:
    response = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": "a-secure-password"},
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_history_is_scoped_to_authenticated_user(client: AsyncClient) -> None:
    alice = await _register(client, "alice@example.com")
    bob = await _register(client, "bob@example.com")

    response = await client.post(
        "/v1/query",
        json={"question": "list customers"},
        headers=alice,
    )
    assert response.status_code == 200

    alice_history = await client.get("/v1/history", headers=alice)
    bob_history = await client.get("/v1/history", headers=bob)

    assert len(alice_history.json()) == 1
    assert bob_history.json() == []


async def test_history_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/v1/history")
    assert response.status_code == 401
