import pytest
from app import app, SECRET_KEY
import jwt


# Helper function to generate test tokens
def generate_test_token(role):
    """Generate a valid JWT token for testing."""
    return jwt.encode({"role": role}, SECRET_KEY, algorithm="HS256")


# Fixtures
@pytest.fixture
def client():
    """Provide a test client for Flask app."""
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token():
    """Provide a valid admin token."""
    return f"Bearer {generate_test_token('Admin')}"


@pytest.fixture
def user_token():
    """Provide a valid user token."""
    return f"Bearer {generate_test_token('User')}"


# Test cases


def test_get_destinations(client):
    """Test retrieving all destinations."""
    response = client.get("/destinations/")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_add_destination(client, admin_token):
    """Test adding a new destination (admin-only)."""
    headers = {"Authorization": admin_token}
    new_destination = {
        "name": "New York",
        "description": "The Big Apple",
        "location": "USA",
    }
    response = client.post("/destinations/", json=new_destination, headers=headers)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Destination added"


def test_add_destination_no_token(client):
    """Test adding a destination without a token."""
    new_destination = {
        "name": "New York",
        "description": "The Big Apple",
        "location": "USA",
    }
    response = client.post("/destinations/", json=new_destination)
    assert response.status_code == 403
    assert response.get_json()["message"] == "Admin token required"


def test_add_duplicate_destination(client, admin_token):
    """Test adding a duplicate destination."""
    headers = {"Authorization": admin_token}
    duplicate_destination = {
        "name": "New York",
        "description": "Another description",
        "location": "Another location",
    }
    response = client.post(
        "/destinations/", json=duplicate_destination, headers=headers
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Destination with this name already exists"


def test_delete_destination(client, admin_token):
    """Test deleting a destination by ID (admin-only)."""

    # Ensure there is a destination to delete
    headers = {"Authorization": admin_token}
    new_destination = {
        "name": "Dhaka",
        "description": "City of Traffic",
        "location": "Bangladesh",
    }
    response = client.post("/destinations/", json=new_destination, headers=headers)

    # Print the response data to understand the error
    print(response.json)  # Print the error message or response data

    # Check if status is correct and assert
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}. Error: {response.json}"

    created_destination = response.get_json()
    destination_id = created_destination.get(
        "id"
    )  # Capture the ID of the newly added destination

    # Now attempt to delete destination using the captured ID
    response = client.delete(f"/destinations/{destination_id}", headers=headers)

    # Check the response
    assert response.status_code == 200
    assert response.get_json()["message"] == "Destination deleted"


def test_delete_destination_not_found(client, admin_token):
    """Test deleting a destination that does not exist."""
    headers = {"Authorization": admin_token}
    response = client.delete("/destinations/999", headers=headers)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Destination not found"


def test_update_destination(client, admin_token):
    """Test updating a destination's description and location (admin-only)."""
    headers = {"Authorization": admin_token}
    update_data = {"description": "New Description", "location": "Updated Location"}
    response = client.put("/destinations/New York", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Destination updated"


def test_update_destination_not_found(client, admin_token):
    """Test updating a destination that does not exist."""
    headers = {"Authorization": admin_token}
    update_data = {"description": "New Description"}
    response = client.put("/destinations/Unknown", json=update_data, headers=headers)
    assert response.status_code == 404
    assert response.get_json()["message"] == "Destination not found"


def test_update_destination_invalid_data(client, admin_token):
    """Test updating a destination with invalid data."""
    headers = {"Authorization": admin_token}
    update_data = {}  # Empty data
    response = client.put("/destinations/New York", json=update_data, headers=headers)
    assert response.status_code == 400
    assert (
        response.get_json()["message"]
        == "At least one of description or location must be provided to update."
    )
