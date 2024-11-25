# Hotel API Flask Assignment

## Project Overview

The **Hotel API Flask Assignment** is a multi-microservice project designed to provide modular backend functionality for a hotel management system. The project is built using Python's Flask framework and follows a RESTful architecture. It includes the following three microservices:

- **User Service**: Handles user registration, authentication, and profile management.
- **Destination Service**: Manages hotel destination data.
- **Authentication Service**: Provides JWT-based authentication and token management.

This project demonstrates the separation of concerns by splitting responsibilities across microservices and emphasizes secure user authentication.

---

## Project Architecture

The project directory is structured as follows:

```plaintext
Hotel-Api-Flask-Assignment-5/
│
├── user_service/           # User-related operations (register, login, profile)
│   ├── app.py              # Main application file
│   ├── models/             # Stores user data in JSON
│   ├── tests/              # Unit tests for user service
│
├── destination_service/    # Handles hotel destination information
│   ├── app.py              # Main application file
│   ├── models/             # Stores destination data
│   ├── tests/              # Unit tests for destination service
│
├── auth_service/           # Authentication microservice
│   ├── app.py              # Main application file
│   ├── tests/              # Unit tests for authentication service
│
├── .gitignore              # Ignore unnecessary files from version control
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
```


---

## Features

### User Service
- **User Registration**: Create new user accounts with validation.
- **User Login**: Authenticate users and generate JWT tokens.
- **Profile Management**: Retrieve user profile details (requires a valid token).

### Destination Service
- **Destination Data**: Retrieve and manage hotel destinations.

### Authentication Service
- **JWT Handling**: Manage user authentication securely using JWT.

---

## Prerequisites

Ensure you have the following installed:
- **Python 3.7+**
- **Pip** (Python package manager)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Muntasir-Ayan/Hotel-Api-Flask-Assignment-5.git
   cd Hotel-Api-Flask-Assignment-5


2. **Create and activate a virtual environment**:
   ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    venv\Scripts\activate     # Windows
3. **Install project dependencies**:
   ```bash
    pip install -r requirements.txt
   
## Running the Microservices
Each microservice runs independently on a unique port. Navigate to the desired microservice directory and start the server:

1. **User Service**:
   ```bash
    cd user_service
    python app.py
Runs on http://127.0.0.1:5001.

2. **Destination Service**:
    ```bash
    cd destination_service
    python app.py
Runs on http://127.0.0.1:5002.

3. **Authentication Service**:
   ```bash
    cd auth_service
    python app.py
Runs on http://127.0.0.1:5003.

##API Documentation
Each service provides a Swagger UI at the root endpoint (/) for testing and exploring available APIs. Below is a summary of key endpoints: <br>
(After login token will generate, for authorize "Bearer <Token>" have to provide. <br>
For admin register, "secret_key": "supersecretkey")

## API Endpoints

### User Service
| **Method** | **Endpoint**       | **Description**              | **Authentication** |
|------------|--------------------|------------------------------|--------------------|
| POST       | `/users/register`  | Register a new user          | No                 |
| POST       | `/users/login`     | Login and obtain a token     | No                 |
| GET        | `/users/profile`   | Get user profile details     | Yes (JWT)          |

### Destination Service
| **Method** | **Endpoint**          | **Description**                 | **Authentication** |
|------------|-----------------------|---------------------------------|--------------------|
| GET        | `/destinations`       | Retrieve hotel destinations     | No                 |
| POST       | `/destinations`       | Add hotel destinations(Admin)   | Yes (JWT)          |
| DELETE     | `/destinations/{ID}`  | Delete hotel destinations(Admin)| Yes (JWT)          |
| PUT        | `/destinations/{Name}`| Update hotel destinations(Admin)| Yes (JWT)          |

### Authentication Service
| **Method** | **Endpoint**            | **Description**              | **Authentication** |
|------------|-------------------------|------------------------------|--------------------|
| GET        | `/auth/profile`         | Get user profile details     | Yes (JWT)          |
| GET        | `/users/destinations`   | Retrieve hotel destinations  | Yes (JWT)          |


## Running Tests
To run unit tests for each microservice:

1. Navigate to the microservice directory:
    ```bash
    cd user_service  # or destination_service, auth_service
2. Run tests using pytest with coverage:
    ```bash
    pytest --cov=app --cov-report=term-missing

