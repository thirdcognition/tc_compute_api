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
def organization_id(access_token, request):
    response = requests.post(
        f"{BASE_URL}/organization/create",
        json={"name": "test org", "website": "https://test.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    org_id = response.json()["id"]

    def teardown():
        requests.delete(
            f"{BASE_URL}/organization/{org_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    request.addfinalizer(teardown)
    return org_id


@pytest.fixture(scope="module")
def journey_id(access_token, organization_id):
    response = requests.post(
        f"{BASE_URL}/journey/",
        json={},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["journey_id"]


@pytest.fixture(scope="module")
def journey_item_id(access_token, journey_id):
    response = requests.post(
        f"{BASE_URL}/journey_item/",
        json={"journey_id": journey_id, "disabled": False},
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


def test_update_journey_item(access_token, journey_id, journey_item_id):
    response = requests.put(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        json={"journey_id": journey_id, "disabled": True},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update journey item: {response.text}"

    # Verify the update
    response = requests.get(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["disabled"] is True
    ), "Journey item disabled status not updated correctly"


def test_delete_journey_item(access_token, journey_item_id):
    response = requests.delete(
        f"{BASE_URL}/journey_item/{journey_item_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete journey item: {response.text}"


def test_delete_journey(access_token, journey_id):
    response = requests.delete(
        f"{BASE_URL}/journey/{journey_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to delete journey: {response.text}"
