import pytest
import requests

HOST = "http://127.0.0.1"
PORT = 4000
BASE_URL = f"{HOST}:{PORT}"

EMAIL = "user1@example.com"
PASSWORD = "password123"


@pytest.fixture(scope="module")
def access_token():
    response = requests.post(
        f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}
    )
    response.raise_for_status()
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def journey_id(access_token):
    response = requests.post(
        f"{BASE_URL}/journey/",
        json={"name": "New Journey", "description": "Description of the new journey"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["journey_id"]


def test_create_journey(access_token, journey_id):
    assert journey_id is not None


def test_get_journey(access_token, journey_id):
    response = requests.get(
        f"{BASE_URL}/journey/{journey_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to get journey: {response.text}"


def test_list_journeys(access_token):
    response = requests.get(
        f"{BASE_URL}/journeys/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, f"Failed to list journeys: {response.text}"


def test_update_journey(access_token, journey_id):
    response = requests.put(
        f"{BASE_URL}/journey/{journey_id}",
        json={
            "name": "Updated Journey",
            "description": "Updated description of the journey",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to update journey: {response.text}"


def test_delete_journey(access_token, journey_id):
    response = requests.delete(
        f"{BASE_URL}/journey/{journey_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to delete journey: {response.text}"
