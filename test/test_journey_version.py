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
def journey_version_id(access_token, journey_id):
    response = requests.post(
        f"{BASE_URL}/journey_version/",
        json={
            "journey_id": journey_id,
            "name": "Version 1",
            "description": "Initial version",
            "disabled": False,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["journey_version_id"]


def test_create_journey_version(access_token, journey_version_id):
    assert journey_version_id is not None


def test_get_journey_version(access_token, journey_version_id):
    response = requests.get(
        f"{BASE_URL}/journey_version/{journey_version_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to get journey version: {response.text}"


def test_list_journey_versions(access_token):
    response = requests.get(
        f"{BASE_URL}/journey_versions/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to list journey versions: {response.text}"


def test_update_journey_version(access_token, journey_version_id, journey_id):
    response = requests.put(
        f"{BASE_URL}/journey_version/{journey_version_id}",
        json={
            "journey_id": journey_id,
            "name": "Updated Version 1",
            "description": "Updated description",
            "disabled": True,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update journey version: {response.text}"


def test_delete_journey_version(access_token, journey_version_id):
    response = requests.delete(
        f"{BASE_URL}/journey_version/{journey_version_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete journey version: {response.text}"
