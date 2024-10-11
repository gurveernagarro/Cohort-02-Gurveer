import pytest
from .utils import create_user, login_user

def test_create_plan(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Monthly",
        "description": "Monthly subscription plan",
        "renewal_period": 1
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["title"] == "Monthly"
    assert response.json()["description"] == "Monthly subscription plan"

def test_get_plans(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/plans/", json={
        "title": "Monthly",
        "description": "Monthly subscription plan",
        "renewal_period": 1
    }, headers=headers)

    response = client.get("/plans/", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plans = response.json()
    assert isinstance(plans, list)
    assert len(plans) > 0

def test_update_plan(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Monthly",
        "description": "Monthly subscription plan",
        "renewal_period": 1
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plan_id = response.json()["id"]

    response = client.put(f"/plans/{plan_id}", json={
        "title": "Updated Monthly",
        "description": "Updated monthly subscription plan",
        "renewal_period": 1
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["title"] == "Updated Monthly"
    assert response.json()["description"] == "Updated monthly subscription plan"

def test_delete_plan(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Monthly",
        "description": "Monthly subscription plan",
        "renewal_period": 1
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plan_id = response.json()["id"]

    response = client.delete(f"/plans/{plan_id}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify plan is deleted
    response = client.get(f"/plans/{plan_id}", headers=headers)
    assert response.status_code == 404, f"Response status code: {response.status_code}, Response body: {response.text}"

def test_create_plan_with_zero_renewal_period(client, unique_username, unique_email):
    username, _ = create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Invalid Plan",
        "description": "Plan with zero renewal period",
        "renewal_period": 0
    }, headers=headers)
    assert response.status_code == 422, f"Response status code: {response.status_code}, Response body: {response.text}"
