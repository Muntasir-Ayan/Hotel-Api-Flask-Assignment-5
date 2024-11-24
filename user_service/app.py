import re
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import bcrypt
import jwt
import datetime
import json
from pathlib import Path

app = Flask(__name__)

# Define the security schema for Swagger
authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Enter 'Bearer <your-token>'",
    }
}

# Initialize API with security definitions
api = Api(
    app,
    doc="/",
    title="User Service API",
    authorizations=authorizations,
    security="Bearer",
)

app.config["SECRET_KEY"] = "supersecretkey"
secret_key_admin = app.config["SECRET_KEY"]

USER_FILE = Path(__file__).parent / "models" / "user.json"
USER_FILE.parent.mkdir(parents=True, exist_ok=True)
# Initialize the file with an empty array if it doesn't exist or is empty
if not USER_FILE.exists() or USER_FILE.stat().st_size == 0:
    with open(USER_FILE, "w") as f:
        json.dump([], f)  # Initialize with an empty array

user_ns = api.namespace("users", description="User operations")

user_model = api.model(
    "User",
    {
        "name": fields.String(required=True, description="Full name"),
        "email": fields.String(required=True, description="Email address"),
        "password": fields.String(required=True, description="Password"),
        "role": fields.String(default="User", description="Role (Admin/User)"),
        "secret_key": fields.String(
            required=False, description="Secret key to assign Admin role"
        ),
    },
)

login_model = api.model(
    "Login",
    {
        "email": fields.String(required=True, description="Email address"),
        "password": fields.String(required=True, description="Password"),
    },
)


# Utility functions
def get_users():
    if not USER_FILE.exists() or USER_FILE.stat().st_size == 0:
        with open(USER_FILE, "w") as f:
            json.dump(
                [], f
            )  # Initialize with an empty array if the file is empty or missing
    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def is_strong_password(password):
    """Validate if the password is strong according to defined criteria"""
    pattern = re.compile(
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )
    return bool(pattern.match(password))


@user_ns.route("/register")
class Register(Resource):
    @user_ns.expect(user_model)
    def post(self):
        try:
            data = request.json
            users = get_users()

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data.get("email", "")):
                return {"message": "Invalid email format"}, 400

            # Check if the user already exists
            if any(u["email"] == data["email"] for u in users):
                return {"message": "User already exists"}, 400

            # Check if password is strong
            if not is_strong_password(data["password"]):
                return {
                    "message": "Password must be at least 8 characters long, contain uppercase and lowercase letters, a number, and a special character."
                }, 400

            # Retrieve the secret key from the request data (if provided)
            secret_key = data.get("secret_key")
            role = data.get("role", "User")  # Default to 'User' if no role is specified

            if role == "Admin":
                if secret_key != secret_key_admin:
                    return {"message": "Invalid secret key for Admin role"}, 403
                role = "Admin"

            elif role != "User":
                return {"message": "Invalid role specified"}, 400

            # Hash the password
            hashed_password = bcrypt.hashpw(
                data["password"].encode("utf-8"), bcrypt.gensalt()
            )

            # Create the new user object with the determined role
            new_user = {
                "name": data["name"],
                "email": data["email"],
                "password": hashed_password.decode("utf-8"),
                "role": role,
            }

            # Save the new user to the users list and persist to the file
            users.append(new_user)
            save_users(users)

            return {
                "message": f'{new_user["name"]} registered successfully as {role}'
            }, 201

        except Exception as e:
            return {"message": str(e)}, 500


@user_ns.route("/login")
class Login(Resource):
    @user_ns.expect(login_model)
    def post(self):
        try:
            data = request.json
            users = get_users()
            user = next((u for u in users if u["email"] == data["email"]), None)

            # Validate user credentials
            if not user or not bcrypt.checkpw(
                data["password"].encode("utf-8"), user["password"].encode("utf-8")
            ):
                return {"message": "Invalid credentials"}, 401

            # Generate JWT token including the user's role
            token = jwt.encode(
                {
                    "email": user["email"],
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )

            return {"token": token}, 200

        except Exception as e:
            return {"message": str(e)}, 500


@user_ns.route("/profile")
class Profile(Resource):
    @user_ns.doc(security="Bearer")  # Use the defined security scheme for this route
    def get(self):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"message": "Token is missing or invalid"}, 401

            token = auth_header.split(" ")[1]  # Extract token from the header
            try:
                # Decode the JWT token
                decoded = jwt.decode(
                    token, app.config["SECRET_KEY"], algorithms=["HS256"]
                )
                users = get_users()
                user = next((u for u in users if u["email"] == decoded["email"]), None)
                if not user:
                    return {"message": "User not found"}, 404
                return {
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"],
                }, 200
            except jwt.ExpiredSignatureError:
                return {"message": "Token has expired"}, 401
            except jwt.InvalidTokenError:
                return {"message": "Invalid token"}, 401

        except Exception as e:
            return {"message": str(e)}, 500


if __name__ == "__main__":
    app.run(port=5001, debug=True)
