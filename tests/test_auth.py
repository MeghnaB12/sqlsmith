"""Authentication contract tests."""

from httpx import AsyncClient


async def test_register_and_login(client: AsyncClient) -> None:
    payload = {"email": "user@example.com", "password": "a-secure-password"}

    registered = await client.post("/v1/auth/register", json=payload)
    assert registered.status_code == 201
    assert registered.json()["email"] == payload["email"]
    assert registered.json()["access_token"]

    logged_in = await client.post("/v1/auth/login", json=payload)
    assert logged_in.status_code == 200
    assert logged_in.json()["access_token"]


async def test_duplicate_registration_is_rejected(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "a-secure-password"}
    assert (await client.post("/v1/auth/register", json=payload)).status_code == 201
    assert (await client.post("/v1/auth/register", json=payload)).status_code == 409


async def test_bad_password_is_rejected(client: AsyncClient) -> None:
    await client.post(
        "/v1/auth/register",
        json={"email": "login@example.com", "password": "right-password"},
    )
    response = await client.post(
        "/v1/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
