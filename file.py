import jwt
import datetime

# Example user data
user = {
    'email': 'user@example.com',
    'role': 'Admin'
}

# Generate the token
token = jwt.encode({
    'email': user['email'],
    'role': user['role'],
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
}, 'your_secret_key', algorithm='HS256')

print(token)
