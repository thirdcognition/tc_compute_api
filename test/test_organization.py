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
def organization_id(access_token):
    org_name = "test org"

    # Attempt to create the organization
    response = requests.post(
        f"{BASE_URL}/organization/create",
        json={"name": org_name, "website": "https://test.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # If the organization already exists, (HTTP 409 Conflict) fetch the existing one
    if response.status_code == 409:
        existing_org_response = requests.get(
            f"{BASE_URL}/organizations",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        existing_org_response.raise_for_status()

        # Assuming the API response returns a list of organizations
        organizations = existing_org_response.json()
        for org in organizations:
            if org["name"] == org_name:
                return org["id"]
        raise Exception("Organization exists but could not be fetched.")
    else:
        response.raise_for_status()
        return response.json()["id"]


@pytest.fixture(scope="module")
def user_id(access_token, organization_id):
    response = requests.post(
        f"{BASE_URL}/organization/{organization_id}/user",
        json={"email": "user2@example.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()["user_id"]


def test_login(access_token):
    assert access_token is not None


def test_create_organization(organization_id):
    assert organization_id is not None


def test_get_organization(access_token, organization_id):
    response = requests.get(
        f"{BASE_URL}/organization/{organization_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200, f"Failed to get organization: {response.text}"


def test_list_organizations(access_token):
    response = requests.get(
        f"{BASE_URL}/organizations", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, f"Failed to list organizations: {response.text}"


def test_update_organization(access_token, organization_id):
    response = requests.put(
        f"{BASE_URL}/organization/{organization_id}",
        json={"website": "https://updated-test.com"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update organization: {response.text}"


def test_get_organization_user(access_token, organization_id, user_id):
    response = requests.get(
        f"{BASE_URL}/organization/{organization_id}/user/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to get organization user: {response.text}"


def test_list_organization_users(access_token, organization_id):
    response = requests.get(
        f"{BASE_URL}/organization/{organization_id}/users",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to list organization users: {response.text}"


def test_update_organization_user(access_token, organization_id, user_id):
    response = requests.put(
        f"{BASE_URL}/organization/{organization_id}/user",
        json={"user_id": user_id, "is_admin": True},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update organization user: {response.text}"


def test_delete_organization_user(access_token, organization_id, user_id):
    response = requests.delete(
        f"{BASE_URL}/organization/{organization_id}/user/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete organization user: {response.text}"


def test_delete_organization(access_token, organization_id):
    response = requests.delete(
        f"{BASE_URL}/organization/{organization_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to delete organization: {response.text}"
