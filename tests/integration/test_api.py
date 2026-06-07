import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_google_oauth_stub(client):
    response = await client.get("/auth/google/url")
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert data.get("mock") == "true"


@pytest.mark.asyncio
async def test_selftest_endpoint(client):
    response = await client.get("/tools/selftest")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 6
    assert data["all_passed"] is True


@pytest.mark.asyncio
async def test_telegram_webhook_mock(client):
    response = await client.post(
        "/bot/webhook",
        json={"update_id": 1, "message": {"text": "/start", "chat": {"id": 123}}},
    )
    assert response.status_code == 200
    assert response.json()["handled"] is True


@pytest.mark.asyncio
async def test_dev_login_and_tools(client):
    login = await client.post("/auth/dev-login", json={"user": "mo"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    connections = await client.get("/tools/connections")
    assert connections.status_code == 200
    assert "mo" in connections.json()["users"]

    evaluate = await client.post(
        "/tools/evaluate",
        headers={"Authorization": f"Bearer {token}"},
        params={"scenario": "mo_surf_perfect"},
    )
    assert evaluate.status_code == 200
    body = evaluate.json()
    assert body["user"] == "mo"
    assert len(body["suggestions"]) >= 1
