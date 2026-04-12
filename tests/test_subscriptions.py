import pytest

from tests.conftest import login_and_get_headers


@pytest.mark.asyncio
async def test_user_a_cannot_receive_user_b_subscriptions(client):
    headers = await login_and_get_headers(client, "usera@example.com", "password123")

    response = await client.get("/api/subscriptions/my", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert all(item["user_id"] != 2 for item in data)
    assert all(item.get("custom_name") != "Spotify Premium" for item in data)
    assert data[0]["user_id"] == 1


@pytest.mark.asyncio
async def test_create_custom_subscription_returns_201(client):
    headers = await login_and_get_headers(client, "usera@example.com", "password123")

    response = await client.post(
        "/api/subscriptions/",
        headers=headers,
        json={
            "custom_name": "Notion Plus",
            "price": 8.5,
            "currency": "USD",
            "billing_cycle": "monthly",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1
    assert data["custom_name"] == "Notion Plus"
    assert data["subscription_id"] is None


@pytest.mark.asyncio
async def test_create_catalog_subscription_returns_201(client):
    headers = await login_and_get_headers(client, "usera@example.com", "password123")

    response = await client.post(
        "/api/subscriptions/",
        headers=headers,
        json={
            "subscription_id": 2,
            "billing_cycle": "monthly",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1
    assert data["subscription_id"] == 2
    assert data["price"] == 9.99
    assert data["currency"] == "USD"
