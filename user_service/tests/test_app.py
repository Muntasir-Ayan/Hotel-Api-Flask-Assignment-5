import pytest
from unittest.mock import patch, MagicMock
from app import app, get_users, save_users
import bcrypt
import jwt
import datetime

VALID_USER = {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "password": bcrypt.hashpw("SecureP@ss123".encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    ),
    "role": "User",
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def mock_get_users():
    return [VALID_USER]


def mock_save_users(users):
    # Mock save_users function (no-op for testing)
    pass


@patch("app.get_users", side_effect=mock_get_users)
@patch("app.save_users", side_effect=mock_save_users)
def test_register_success(mock_save_users, mock_get_users, client):
    new_user = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "SecureP@ss123!",
        "role": "User",
    }
    response = client.post("/users/register", json=new_user)
    assert response.status_code == 201
    assert "registered successfully as User" in response.json["message"]


@patch("app.get_users", side_effect=mock_get_users)
@patch("app.save_users", side_effect=mock_save_users)
def test_register_duplicate_email(mock_save_users, mock_get_users, client):
    duplicate_user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123!",
        "role": "User",
    }
    response = client.post("/users/register", json=duplicate_user)
    assert response.status_code == 400
    assert response.json["message"] == "User already exists"


def test_register_invalid_password(client):
    new_user = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "weakpass",
        "role": "User",
    }
    response = client.post("/users/register", json=new_user)
    assert response.status_code == 400
    assert "Password must be at least 8 characters long" in response.json["message"]


@patch("app.get_users", side_effect=mock_get_users)
@patch("app.save_users", side_effect=mock_save_users)
def test_register_invalid_role(mock_save_users, mock_get_users, client):
    invalid_user = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "SecureP@ss123!",
        "role": "SuperAdmin",
    }
    response = client.post("/users/register", json=invalid_user)
    assert response.status_code == 400
    assert response.json["message"] == "Invalid role specified"


@patch("app.get_users", side_effect=mock_get_users)
def test_login_success(mock_get_users, client):
    login_data = {"email": VALID_USER["email"], "password": "SecureP@ss123"}
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 200
    assert "token" in response.json


@patch("app.get_users", side_effect=mock_get_users)
def test_login_invalid_credentials(mock_get_users, client):
    login_data = {"email": VALID_USER["email"], "password": "WrongP@ss123"}
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 401
    assert response.json["message"] == "Invalid credentials"


@patch("app.get_users", side_effect=mock_get_users)
def test_profile_success(mock_get_users, client):
    token = jwt.encode(
        {
            "email": VALID_USER["email"],
            "role": VALID_USER["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    response = client.get(
        "/users/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["name"] == VALID_USER["name"]
    assert response.json["email"] == VALID_USER["email"]


def test_profile_missing_token(client):
    response = client.get("/users/profile")
    assert response.status_code == 401
    assert response.json["message"] == "Token is missing or invalid"


def test_profile_invalid_token(client):
    response = client.get(
        "/users/profile", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert response.json["message"] == "Invalid token"
