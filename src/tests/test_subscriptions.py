import pytest
from .utils import create_user, login_user, create_plan, create_magazine

def test_create_subscription(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    plan = create_plan(client, headers)
    name_suffix = "create_sub"
    magazine = create_magazine(client, headers, name_suffix)

    response = client.post("/subscriptions/", json={
        "user_id": 1,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "price": 10.0,
        "next_renewal_date": "2024-12-31"
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 10.0

def test_get_subscriptions(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    plan = create_plan(client, headers)
    name_suffix = "get_sub"
    magazine = create_magazine(client, headers, name_suffix)

    client.post("/subscriptions/", json={
        "user_id": 1,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "price": 10.0,
        "next_renewal_date": "2024-12-31"
    }, headers=headers)

    response = client.get("/subscriptions/", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    subscriptions = response.json()
    assert isinstance(subscriptions, list)
    assert len(subscriptions) > 0

def test_update_subscription(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    plan = create_plan(client, headers)
    name_suffix = "update_sub"
    magazine = create_magazine(client, headers, name_suffix)

    response = client.post("/subscriptions/", json={
        "user_id": 1,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "price": 10.0,
        "next_renewal_date": "2024-12-31"
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    subscription_id = response.json()["id"]

    response = client.put(f"/subscriptions/{subscription_id}", json={
        "user_id": 1,
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "price": 15.0,
        "next_renewal_date": "2025-01-31"
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 15.0

def test_delete_subscription(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    plan = create_plan(client, headers)
    name_suffix = "delete_sub"
    magazine = create_magazine(client, headers, name_suffix)

    response = client.post("/subscriptions/", json={
        "user_id": 1,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "price": 10.0,
        "next_renewal_date": "2024-12-31"
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    subscription_id = response.json()["id"]

    response = client.delete(f"/subscriptions/{subscription_id}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify subscription is marked as inactive
    response = client.get(f"/subscriptions/{subscription_id}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert not response.json()["is_active"], f"Subscription is not marked as inactive: {response.json()}"
