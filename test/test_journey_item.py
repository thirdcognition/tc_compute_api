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
def journey_item_id(access_token, journey_id):
    response = requests.post(
        f"{BASE_URL}/journey_item/",
        json={"journey_id": journey_id, "item_name": "New Item"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["journey_item_id"]


def test_create_journey_item(access_token, journey_item_id):
    assert journey_item_id is not None


def test_get_journey_item(access_token, journey_item_id):
    response = requests.get(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to get journey item: {response.text}"


def test_list_journey_items(access_token):
    response = requests.get(
        f"{BASE_URL}/journey_items/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to list journey items: {response.text}"


def test_update_journey_item(access_token, journey_item_id):
    response = requests.put(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        json={"item_name": "Updated Item"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update journey item: {response.text}"


def test_delete_journey_item(access_token, journey_item_id):
    response = requests.delete(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete journey item: {response.text}"
