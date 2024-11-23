import pytest
import json
from user_service.app import app
from unittest.mock import patch
import bcrypt

# Create a test client using the Flask app
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Helper function to mock user data
def mock_user_data():
    return {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'Test@1234',
        'role': 'User',
    }

# Test case for registering a user
def test_register_user(client):
    user_data = mock_user_data()

    response = client.post('/users/register', json=user_data)
    assert response.status_code == 201
    assert 'Test User registered successfully as User' in response.get_data(as_text=True)

# Test case for registering a user with an invalid email
def test_register_invalid_email(client):
    user_data = mock_user_data()
    user_data['email'] = 'invalidemail'

    response = client.post('/users/register', json=user_data)
    assert response.status_code == 400
    assert 'Invalid email format' in response.get_data(as_text=True)

# Test case for registering a user with a weak password
def test_register_weak_password(client):
    user_data = mock_user_data()
    user_data['password'] = 'weakpass'

    response = client.post('/users/register', json=user_data)
    assert response.status_code == 400
    assert 'Password must be at least 8 characters long' in response.get_data(as_text=True)

# Test case for user login with valid credentials
def test_login_valid(client):
    user_data = mock_user_data()
    # First, register the user
    client.post('/users/register', json=user_data)

    login_data = {
        'email': user_data['email'],
        'password': user_data['password']
    }
    
    response = client.post('/users/login', json=login_data)
    assert response.status_code == 200
    assert 'token' in response.json

# Test case for user login with invalid credentials
def test_login_invalid(client):
    login_data = {
        'email': 'invalid@example.com',
        'password': 'wrongpassword'
    }
    
    response = client.post('/users/login', json=login_data)
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_data(as_text=True)

# Test case for accessing the profile with a valid token
def test_profile_valid(client):
    user_data = mock_user_data()
    # First, register the user and log them in to get a token
    client.post('/users/register', json=user_data)
    login_data = {
        'email': user_data['email'],
        'password': user_data['password']
    }
    login_response = client.post('/users/login', json=login_data)
    token = login_response.json['token']
    
    # Access the profile using the token
    response = client.get('/users/profile', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert user_data['name'] in response.get_data(as_text=True)
    assert user_data['email'] in response.get_data(as_text=True)

# Test case for accessing the profile with an invalid token
def test_profile_invalid_token(client):
    response = client.get('/users/profile', headers={'Authorization': 'Bearer invalidtoken'})
    assert response.status_code == 401
    assert 'Invalid token' in response.get_data(as_text=True)
