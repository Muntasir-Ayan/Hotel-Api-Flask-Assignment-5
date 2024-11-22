from flask import Flask, request
from flask_restx import Api, Resource

app = Flask(__name__)
api = Api(app, doc='/docs', title="Authentication Service API")

auth_ns = api.namespace('auth', description='Authentication operations')

@auth_ns.route('/validate')
class Validate(Resource):
    def post(self):
        """Validate token (stubbed implementation)"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'message': 'Token missing'}, 401
        return {'message': 'Token valid'}, 200

if __name__ == '__main__':
    app.run(port=5003, debug=True)
