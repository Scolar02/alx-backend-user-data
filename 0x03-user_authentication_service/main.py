#!/usr/bin/env python3
"""E2E (End-to-End) integration test for `app.py`.
"""
import requests


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"
BASE_URL = "http://0.0.0.0:5000"


def register_user(email: str, password: str) -> None:
    """Function to verify the registration process for a new user.
    """
    url = f"{BASE_URL}/users"
    data = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=data)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "user created"}
    res = requests.post(url, data=data)
    assert res.status_code == 400
    assert res.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Function to test login with incorrect password.
    """
    url = f"{BASE_URL}/sessions"
    data = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=data)
    assert res.status_code == 401


def log_in(email: str, password: str) -> str:
    """Function to verify successful login.
    """
    url = f"{BASE_URL}/sessions"
    data = {
        'email': email,
        'password': password,
    }
    res = requests.post(url, data=data)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "logged in"}
    return res.cookies.get('session_id')


def profile_unlogged() -> None:
    """Function to test accessing profile information without being logged in.
    """
    url = f"{BASE_URL}/profile"
    res = requests.get(url)
    assert res.status_code == 403


def profile_logged(session_id: str) -> None:
    """Function to verify profile access when logged in.
    """
    url = f"{BASE_URL}/profile"
    cookies = {
        'session_id': session_id,
    }
    res = requests.get(url, cookies=cookies)
    assert res.status_code == 200
    assert "email" in res.json()


def log_out(session_id: str) -> None:
    """Function to check the logout process.
    """
    url = f"{BASE_URL}/sessions"
    cookies = {
        'session_id': session_id,
    }
    res = requests.delete(url, cookies=cookies)
    assert res.status_code == 200
    assert res.json() == {"message": "Bienvenue"}


def reset_password_token(email: str) -> str:
    """Function to test requesting a password reset token.
    """
    url = f"{BASE_URL}/reset_password"
    data = {'email': email}
    res = requests.post(url, data=data)
    assert res.status_code == 200
    assert res.json()["email"] == email
    assert "reset_token" in res.json()
    return res.json().get('reset_token')


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Function to test updating the user's password.
    """
    url = f"{BASE_URL}/reset_password"
    data = {
        'email': email,
        'reset_token': reset_token,
        'new_password': new_password,
    }
    res = requests.put(url, data=data)
    assert res.status_code == 200
    assert res.json() == {"email": email, "message": "Password updated"}


if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
