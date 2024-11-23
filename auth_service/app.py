import json
import jwt
import requests
from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from pathlib import Path

app = Flask(__name__)

# Define the security schema for Swagger
authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Enter 'Bearer <your-token>'"
    }
}

# Initialize API with security definitions
api = Api(app, doc='/', title="Auth Service API", authorizations=authorizations, security='Bearer')

# JWT secret key shared with user_service
SECRET_KEY = 'supersecretkey'

USER_SERVICE_URL = "http://localhost:5001"
DESTINATION_SERVICE_URL = "http://localhost:5002"

# Helper function to verify JWT token
def verify_token(token):
    try:
        # Decode JWT token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded  # Return decoded token if valid
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Create an API namespace for auth operations
auth_ns = api.namespace('auth', description='Authentication and access operations')

@auth_ns.route('/profile')
class Profile(Resource):
    @auth_ns.doc(security='Bearer')  # This route requires a valid token
    def get(self):
        """Get the user profile"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token is missing or invalid'}, 401

        token = auth_header.split(' ')[1]
        decoded_token = verify_token(token)
        
        if not decoded_token:
            return {'message': 'Invalid or expired token'}, 401
        
        # Forward request to user_service to get user profile
        user_profile = requests.get(f"{USER_SERVICE_URL}/users/profile", headers={'Authorization': f'Bearer {token}'})


        if user_profile.status_code == 200:
            return user_profile.json(), 200
        else:
            return {'message': 'Failed to retrieve user profile from User Service'}, 500


@auth_ns.route('/destinations')
class Destinations(Resource):
    @auth_ns.doc(security='Bearer')  # This route requires a valid token
    def get(self):
        """Get the list of all destinations (only accessible to authenticated users)"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token is missing or invalid'}, 401

        token = auth_header.split(' ')[1]
        decoded_token = verify_token(token)
        
        if not decoded_token:
            return {'message': 'Invalid or expired token'}, 401

        # Optionally, you can check the role of the user
        user_role = decoded_token.get('role')
        if user_role not in ['User', 'Admin']:
            return {'message': 'You do not have permission to access destinations'}, 403

        # Forward request to destination_service to get the list of destinations
        destinations = requests.get(f"{DESTINATION_SERVICE_URL}/destinations")
        
        if destinations.status_code == 200:
            return destinations.json(), 200
        else:
            return {'message': 'Failed to retrieve destinations from Destination Service'}, 500
        
if __name__ == '__main__':
    app.run(port=5003, debug=True)
