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


@pytest.fixture(scope="module")
def journey_structure_id(access_token, journey_id):
    response = requests.post(
        f"{BASE_URL}/journey_structure/",
        json={"journey_id": journey_id, "structure_name": "New Structure"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["journey_structure_id"]


def test_create_journey_structure(access_token, journey_structure_id):
    assert journey_structure_id is not None


def test_get_journey_structure(access_token, journey_structure_id):
    response = requests.get(
        f"{BASE_URL}/journey_structure/{journey_structure_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to get journey structure: {response.text}"


def test_list_journey_structures(access_token):
    response = requests.get(
        f"{BASE_URL}/journey_structures/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to list journey structures: {response.text}"


def test_update_journey_structure(access_token, journey_structure_id):
    response = requests.put(
        f"{BASE_URL}/journey_structure/{journey_structure_id}",
        json={"structure_name": "Updated Structure"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update journey structure: {response.text}"


def test_delete_journey_structure(access_token, journey_structure_id):
    response = requests.delete(
        f"{BASE_URL}/journey_structure/{journey_structure_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete journey structure: {response.text}"
