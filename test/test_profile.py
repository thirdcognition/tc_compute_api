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
def user_id(access_token):
    # Assuming the user_id is returned in the login response
    response = requests.post(
        f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}
    )
    response.raise_for_status()
    return response.json()["user"]["id"]


def test_update_user_profile(access_token, user_id):
    # Update current user profile
    response = requests.put(
        f"{BASE_URL}/user/",
        json={"name": "Updated User One"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update user profile: {response.text}"

    # Verify the update
    response = requests.get(
        f"{BASE_URL}/user/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["name"] == "Updated User One"
    ), "User name not updated correctly"

    # Update user profile with user_id
    response = requests.put(
        f"{BASE_URL}/user/{user_id}",
        json={"name": "Updated User Two"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.status_code == 200
    ), f"Failed to update user profile with user_id: {response.text}"

    # Verify the update with user_id
    response = requests.get(
        f"{BASE_URL}/user/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert (
        response.json()["name"] == "Updated User Two"
    ), "User name not updated correctly with user_id"


# Commenting out the delete user profile test as it is commented in the HTTP file
# def test_delete_user_profile(access_token, user_id):
#     response = requests.delete(
#         f"{BASE_URL}/user/{user_id}",
#         headers={"Authorization": f"Bearer {access_token}"},
#     )
#     assert (
#         response.status_code == 403
#     ), "Users should not be able to delete their own profile"
