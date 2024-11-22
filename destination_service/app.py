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
    with open(DEST_FILE, 'r') as f:
        return json.load(f)

def save_destinations(destinations):
    """Save destination data to the file"""
    with open(DEST_FILE, 'w') as f:
        json.dump(destinations, f, indent=4)

def verify_admin_token(auth_header):
    """Verify if the user has admin privileges"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]  # Extract token from the header
    print(f"Received token: {token}")  # Debugging statement to check the token
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(f"Decoded token: {decoded}")  # Debugging statement to check the decoded token
        return decoded.get('role') == 'Admin'  # Check if role is Admin
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

# Create an API namespace for destinations
dest_ns = api.namespace('destinations', description='Destination operations')

@dest_ns.route('/')
class Destinations(Resource):
    def get(self):
        """List all destinations"""
        destinations = get_destinations()
        return destinations, 200

    @dest_ns.expect(destination_model)
    @dest_ns.doc(security='Bearer')  # Security required for this endpoint
    def post(self):
        """Add a new destination (admin-only)"""
        auth_header = request.headers.get('Authorization')
        if not verify_admin_token(auth_header):
            return {'message': 'Admin token required'}, 403  # Forbidden if not Admin

        data = request.json
        destinations = get_destinations()

        # Check if a destination with the same name already exists
        if any(dest['name'].lower() == data['name'].lower() for dest in destinations):
            return {'message': 'Destination with this name already exists'}, 400  # Bad request if duplicate found

        # If no duplicate, add the new destination
        destinations.append(data)
        save_destinations(destinations)
        return {'message': 'Destination added'}, 201

@dest_ns.route('/<string:name>')
class Destination(Resource):
    @dest_ns.doc(security='Bearer')  # Security required for this endpoint
    def delete(self, name):
        """Delete a destination (admin-only)"""
        auth_header = request.headers.get('Authorization')
        if not verify_admin_token(auth_header):
            return {'message': 'Admin token required'}, 403  # Forbidden if not Admin

        destinations = get_destinations()
        destination = next((dest for dest in destinations if dest['name'] == name), None)
        if destination:
            destinations.remove(destination)
            save_destinations(destinations)
            return {'message': 'Destination deleted'}, 200
        else:
            return {'message': 'Destination not found'}, 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)
