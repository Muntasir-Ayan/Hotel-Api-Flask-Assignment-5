import re
from flask import Flask, request
from flask_restx import Api, Resource, fields
import json
from pathlib import Path
import jwt

app = Flask(__name__)

# Define the security schema for Swagger UI
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Enter 'Bearer <your-token>'"
    }
}

# Initialize the API with security definitions
api = Api(app, doc='/', title="Destination Service API", authorizations=authorizations, security='Bearer')

DEST_FILE = Path(__file__).parent / 'models' / 'destinations.json'

DEST_FILE.parent.mkdir(parents=True, exist_ok=True)
if not DEST_FILE.exists():
    with open(DEST_FILE, 'w') as f:
        json.dump([], f)

# JWT secret key from user service
SECRET_KEY = 'supersecretkey'

# Destination model for the API
destination_model = api.model('Destination', {
    'name': fields.String(required=True, description='Destination name'),
    'description': fields.String(required=True, description='Short description'),
    'location': fields.String(required=True, description='Location name')
})

def get_destinations():
    """Load the destination data from the file"""
    try:
        with open(DEST_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {'message': f'Error reading destinations: {str(e)}'}, 500

def save_destinations(destinations):
    """Save destination data to the file"""
    try:
        with open(DEST_FILE, 'w') as f:
            json.dump(destinations, f, indent=4)
    except Exception as e:
        return {'message': f'Error saving destinations: {str(e)}'}, 500

def verify_admin_token(auth_header):
    """Verify if the user has admin privileges"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]  # Extract token from the header
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded.get('role') == 'Admin'  # Check if role is Admin
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def generate_id(destinations):
    """Generate a new unique ID for a destination"""
    if destinations:
        return max(dest['id'] for dest in destinations) + 1
    return 1  # Start with 1 if no destinations exist

# Create an API namespace for destinations
dest_ns = api.namespace('destinations', description='Destination operations')

@dest_ns.route('/')
class Destinations(Resource):
    def get(self):
        """List all destinations"""
        destinations = get_destinations()
        if isinstance(destinations, dict):  # In case of error
            return destinations
        return destinations, 200

    @dest_ns.expect(destination_model)
    @dest_ns.doc(security='Bearer')  # Security required for this endpoint
    def post(self):
        """Add a new destination (admin-only)"""
        auth_header = request.headers.get('Authorization')
        if not verify_admin_token(auth_header):
            return {'message': 'Admin token required'}, 403  # Forbidden if not Admin

        data = request.json
        # Validate the input
        if not data.get('name') or not data.get('description') or not data.get('location'):
            return {'message': 'All fields (name, description, location) are required.'}, 400
        
        destinations = get_destinations()

        # Check if a destination with the same name already exists
        if any(dest['name'].lower() == data['name'].lower() for dest in destinations):
            return {'message': 'Destination with this name already exists'}, 400  # Bad request if duplicate found

        # If no duplicate, add the new destination with a generated ID
        data['id'] = generate_id(destinations)
        destinations.append(data)
        save_destinations(destinations)
        return {'message': 'Destination added'}, 201

@dest_ns.route('/<int:id>')
class Destination(Resource):
    @dest_ns.doc(security='Bearer')  # Security required for this endpoint
    def delete(self, id):
        """Delete a destination by ID (admin-only)"""
        auth_header = request.headers.get('Authorization')
        if not verify_admin_token(auth_header):
            return {'message': 'Admin token required'}, 403  # Forbidden if not Admin

        destinations = get_destinations()
        destination = next((dest for dest in destinations if dest['id'] == id), None)
        if destination:
            destinations.remove(destination)
            save_destinations(destinations)
            return {'message': 'Destination deleted'}, 200
        else:
            return {'message': 'Destination not found'}, 404
        
@dest_ns.route('/<string:name>')
class Destination(Resource):

    @dest_ns.expect(destination_model)  # Expect the new destination data
    @dest_ns.doc(security='Bearer')  # Security required for this endpoint
    def put(self, name):
        """Edit a destination's description and location (admin-only)"""
        auth_header = request.headers.get('Authorization')
        if not verify_admin_token(auth_header):
            return {'message': 'Admin token required'}, 403  # Forbidden if not Admin

        # Fetch the updated data from the request body
        data = request.json
        if not data.get('description') and not data.get('location'):
            return {'message': 'At least one of description or location must be provided to update.'}, 400

        destinations = get_destinations()

        # Find the destination by name
        destination = next((dest for dest in destinations if dest['name'] == name), None)

        if destination:
            # Update the destination's description and location
            if 'description' in data:
                destination['description'] = data['description']
            if 'location' in data:
                destination['location'] = data['location']
            save_destinations(destinations)
            return {'message': 'Destination updated'}, 200
        else:
            return {'message': 'Destination not found'}, 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)
