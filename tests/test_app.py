import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict before/after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister():
    email = "testuser@example.com"
    activity = "Basketball Team"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    res = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert res.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent():
    email = "noone@example.com"
    activity = "Tennis Club"

    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    res = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert res.status_code == 404


def test_signup_existing_student():
    activity = "Basketball Team"
    email = activities[activity]["participants"][0]

    res = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert res.status_code == 400
