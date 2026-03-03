from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


# fixture to reset activities state between tests
@pytest.fixture(autouse=True)
def reset_activities():
    # arrange: make a deep copy of the original dictionary
    original = {name: act.copy() for name, act in activities.items()}
    yield
    # teardown: restore original state
    activities.clear()
    activities.update({name: act.copy() for name, act in original.items()})


client = TestClient(app)


def test_root_redirects():
    # Act
    response = client.get("/", follow_redirects=False)
    # Assert
    assert response.status_code in (307, 308)
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities():
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")
    assert email in activities["Chess Club"]["participants"]


def test_signup_not_found():
    # Act
    response = client.post(
        "/activities/Nonexistent/signup", params={"email": "foo@bar"}
    )
    # Assert
    assert response.status_code == 404


def test_signup_already_registered():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 400


def test_unregister_success():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    # Act
    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email}
    )
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_found_activity():
    # Act
    response = client.delete(
        "/activities/Nope/unregister", params={"email": "foo@bar"}
    )
    # Assert
    assert response.status_code == 404


def test_unregister_not_registered():
    # Arrange
    email = "not@registered.edu"
    # Act
    response = client.delete(
        "/activities/Chess Club/unregister", params={"email": email}
    )
    # Assert
    assert response.status_code == 404
