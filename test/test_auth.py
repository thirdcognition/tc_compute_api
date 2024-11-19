import requests

HOST = "http://127.0.0.1"
PORT = 4000
BASE_URL = f"{HOST}:{PORT}"

EMAIL = "user1@example.com"
PASSWORD = "password123"


def test_login():
    response = requests.post(
        f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    access_token = response.json().get("access_token")
    assert access_token is not None, "Access token not found in login response"
