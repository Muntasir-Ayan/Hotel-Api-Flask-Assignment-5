import pytest
from unittest.mock import patch
from app import app, verify_token

@pytest.fixture
def client():
    """Fixture to set up the Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Mock JWT tokens
VALID_USER_TOKEN = "valid_user_token"
VALID_ADMIN_TOKEN = "valid_admin_token"
EXPIRED_TOKEN = "expired_token"
INVALID_TOKEN = "invalid_token"

# Helper function to mock verify_token behavior
def mock_verify_token(token):
    if token == VALID_USER_TOKEN:
        return {"email": "user@example.com", "role": "User"}
    elif token == VALID_ADMIN_TOKEN:
        return {"email": "admin@example.com", "role": "Admin"}
    elif token == EXPIRED_TOKEN:
        return {'message': 'Token has expired'}, 401
    elif token == INVALID_TOKEN:
        return {'message': 'Invalid token'}, 401
    return {'message': 'Token is missing or invalid'}, 401


@patch("app.verify_token", side_effect=mock_verify_token)
@patch("requests.get")
def test_profile_valid_token(mock_requests_get, mock_verify_token, client):
    """Test /auth/profile with a valid token"""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = {"name": "John Doe", "email": "user@example.com", "role": "User"}

    response = client.get('/auth/profile', headers={"Authorization": f"Bearer {VALID_USER_TOKEN}"})
    assert response.status_code == 200
    assert response.json == {"name": "John Doe", "email": "user@example.com", "role": "User"}


@patch("app.verify_token", side_effect=mock_verify_token)
def test_profile_invalid_token(mock_verify_token, client):
    """Test /auth/profile with an invalid token"""
    response = client.get('/auth/profile', headers={"Authorization": f"Bearer {INVALID_TOKEN}"})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'


@patch("app.verify_token", side_effect=mock_verify_token)
def test_profile_missing_token(mock_verify_token, client):
    """Test /auth/profile without an Authorization header"""
    response = client.get('/auth/profile')
    assert response.status_code == 401
    assert response.json['message'] == 'Token is missing or invalid'


@patch("app.verify_token", side_effect=mock_verify_token)
@patch("requests.get")
def test_destinations_valid_user(mock_requests_get, mock_verify_token, client):
    """Test /auth/destinations with a valid user token"""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = [
        {"id": 1, "name": "Paris"},
        {"id": 2, "name": "New York"}
    ]

    response = client.get('/auth/destinations', headers={"Authorization": f"Bearer {VALID_USER_TOKEN}"})
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "name": "Paris"},
        {"id": 2, "name": "New York"}
    ]


@patch("app.verify_token", side_effect=mock_verify_token)
@patch("requests.get")
def test_destinations_valid_admin(mock_requests_get, mock_verify_token, client):
    """Test /auth/destinations with a valid admin token"""
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.json.return_value = [
        {"id": 1, "name": "Tokyo"},
        {"id": 2, "name": "London"}
    ]

    response = client.get('/auth/destinations', headers={"Authorization": f"Bearer {VALID_ADMIN_TOKEN}"})
    assert response.status_code == 200
    assert response.json == [
        {"id": 1, "name": "Tokyo"},
        {"id": 2, "name": "London"}
    ]


@patch("app.verify_token", side_effect=mock_verify_token)
def test_destinations_missing_token(mock_verify_token, client):
    """Test /auth/destinations without an Authorization header"""
    response = client.get('/auth/destinations')
    assert response.status_code == 401
    assert response.json['message'] == 'Token is missing or invalid'


@patch("app.verify_token", side_effect=mock_verify_token)
def test_destinations_invalid_token(mock_verify_token, client):
    """Test /auth/destinations with an invalid token"""
    response = client.get('/auth/destinations', headers={"Authorization": f"Bearer {INVALID_TOKEN}"})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'


@patch("app.verify_token", side_effect=mock_verify_token)
@patch("requests.get", side_effect=Exception("Service unavailable"))
def test_destinations_service_error(mock_requests_get, mock_verify_token, client):
    """Test /auth/destinations with a service error"""
    response = client.get('/auth/destinations', headers={"Authorization": f"Bearer {VALID_USER_TOKEN}"})
    assert response.status_code == 500
    assert 'Error communicating with Destination Service' in response.json['message']
