# Secure Hero Missions API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.22-4479A1?logo=sqlite)](https://sqlmodel.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Future Improvements](#future-improvements)
- [Screenshots](#screenshots)
- [Author](#author)

---

## 📖 Overview

**Secure Hero Missions API** is a production-oriented REST API built with FastAPI for managing a superhero organization. The system handles **users**, **heroes**, and **missions** with role-based access control (RBAC) using JWT authentication.

The project demonstrates best practices in FastAPI development including:
- Separation of concerns with modular architecture
- Type safety with Pydantic and SQLModel
- Dependency injection for clean, testable code
- Comprehensive error handling and validation
- Full test coverage with pytest

---

## ✨ Features

### 🔐 Authentication & Authorization
- **User Registration** - Create new accounts with hashed passwords
- **JWT Authentication** - Secure login returns Bearer tokens
- **Role-Based Access** - Normal users vs Admin users
- **Protected Routes** - Authentication required for creating/updating resources

### 🦸 Hero Management (CRUD)
| Action | Access | Description |
|--------|--------|-------------|
| `POST /heroes` | Authenticated | Create a new hero |
| `GET /heroes` | Public | List all heroes |
| `GET /heroes/{id}` | Public | Get hero by ID |
| `PATCH /heroes/{id}` | Authenticated | Update hero (partial) |
| `DELETE /heroes/{id}` | Admin Only | Delete hero |

**Hero Validation Rules:**
- `name`: Minimum 3 characters
- `power`: Minimum 3 characters
- `level`: Integer between 1 and 100
- `active`: Boolean (default: true)

**Role-Based Restrictions:**
- **Normal Users**: Can only set `name` and `power` (level=1, active=true forced)
- **Admin Users**: Full control over `level` and `active` status

### 📋 Mission Management (CRUD)
| Action | Access | Description |
|--------|--------|-------------|
| `POST /missions` | Authenticated | Create a mission for a hero |
| `GET /missions` | Public | List all missions |
| `GET /missions/{id}` | Public | Get mission by ID |
| `PATCH /missions/{id}` | Authenticated | Update mission (partial) |
| `DELETE /missions/{id}` | Admin Only | Delete a mission |

**Mission Validation Rules:**
- `title`: Minimum 5 characters
- `difficulty`: Integer between 1 and 10
- `completed`: Boolean (default: false)
- `hero_id`: Must reference an existing hero

### 🛡️ Business Rules
- ✅ Cannot create a mission for a non-existent hero
- ✅ Cannot delete a hero with active (incomplete) missions
- ✅ Only admin users can delete heroes and missions
- ✅ Passwords are stored as bcrypt hashes only (no plain text)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework for building APIs |
| **SQLModel** | ORM combining SQLAlchemy + Pydantic |
| **SQLite** | Lightweight database (production-ready) |
| **JWT** | Authentication with `python-jose` |
| **Bcrypt** | Password hashing with `passlib` |
| **Pydantic** | Data validation and serialization |
| **Pytest** | Testing framework |
| **Uvicorn** | ASGI server for FastAPI |

---

## 📁 Project Structure

```
hero_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings with pydantic-settings
│   ├── crud.py              # create_admin_user and create_user helping functions
│   ├── db.py                # Database engine, session, table creation
│   ├── dependencies.py      # Dependency injection (auth, roles)
|   ├── security.py          # Password hashing, JWT helpers
│   │
│   ├── models/              # SQLModel database tables
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── hero.py
│   │   └── mission.py
│   │
│   ├── schemas/             # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py          # Token schemas
│   │   ├── user.py          # UserCreate, UserLogin, UserOut
│   │   ├── hero.py          # HeroCreate, HeroUpdate, Admin variants
│   │   └── mission.py       # MissionCreate, MissionUpdate, MissionOut
│   │
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── auth.py          # /auth/register, /auth/login, /auth/me
│       ├── heroes.py        # /heroes CRUD with role checks
│       └── missions.py      # /missions CRUD with validation
|
|── screenshots/*             # .png files for use from README.md
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Fixtures & test database setup
│   └── test_api.py          # 10+ test cases
│
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── hero_database.db         # SQLite database (auto-created)
└── README.md                # This file
```

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone git@github.com:serendipity019/AI_for_developers_exercises.git
cd hero_api
```

### 2️⃣ Create a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install fastapi uvicorn[standard] sqlmodel python-jose[cryptography] passlib[bcrypt] pydantic-settings pytest httpx
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
# JWT Secret (change this in production!)
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-characters

# Database (optional - defaults to sqlite:///./hero_database.db)
# DATABASE_URL=sqlite:///./hero_database.db

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## ▶️ Running the Application

### Development Mode (with auto-reload)

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the server
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔌 API Endpoints

### 🔐 Authentication Routes

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/auth/register` | Public | Register a new user |
| `POST` | `/auth/login` | Public | Login and get JWT token |
| `GET` | `/auth/me` | Authenticated | Get current user details |

#### Register Request
```json
POST /auth/register
{
    "username": "superhero_fan",
    "password": "securepassword123"
}
```

#### Login Request
```json
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=superhero_fan&password=securepassword123
```

#### Login Response
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

---

### 🦸 Hero Routes

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/heroes` | Authenticated | Create a hero |
| `GET` | `/heroes` | Public | List all heroes |
| `GET` | `/heroes/{id}` | Public | Get hero by ID |
| `PATCH` | `/heroes/{id}` | Authenticated | Update hero (partial) |
| `DELETE` | `/heroes/{id}` | Admin Only | Delete hero |

#### Create Hero (Normal User)
```json
POST /heroes
Authorization: Bearer <token>

{
    "name": "Swift Arrow",
    "power": "Super Speed"
}
```
*Response*: `level: 1`, `active: true` (forced)

#### Create Hero (Admin)
```json
POST /heroes
Authorization: Bearer <admin_token>

{
    "name": "Omega Supreme",
    "power": "Reality Manipulation",
    "level": 100,
    "active": false
}
```

#### Update Hero (Normal User)
```json
PATCH /heroes/{id}
Authorization: Bearer <token>

{
    "name": "Swift Arrow II",
    "power": "Enhanced Speed"
}
```

#### Update Hero (Admin)
```json
PATCH /heroes/{id}
Authorization: Bearer <admin_token>

{
    "name": "Omega Supreme",
    "power": "Ultimate Reality",
    "level": 100,
    "active": true
}
```

---

### 📋 Mission Routes

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/missions` | Authenticated | Create a mission |
| `GET` | `/missions` | Public | List all missions |
| `GET` | `/missions/{id}` | Public | Get mission by ID |
| `PATCH` | `/missions/{id}` | Authenticated | Update mission (partial) |
| `DELETE` | `/missions/{id}` | Admin Only | Delete mission |

#### Create Mission
```json
POST /missions
Authorization: Bearer <token>

{
    "title": "Save the City from Villain",
    "difficulty": 7,
    "hero_id": 1,
    "completed": false
}
```

#### Update Mission
```json
PATCH /missions/{id}
Authorization: Bearer <token>

{
    "title": "Save the City from Villain - Priority",
    "difficulty": 9,
    "completed": true
}
```

---

## 🧪 Testing

### Running All Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Test Coverage

The test suite includes **10+ test cases** covering:

| Test | Description |
|------|-------------|
| ✅ `test_register_user` | User registration |
| ✅ `test_login_returns_token` | Login returns JWT token |
| ✅ `test_create_hero_requires_authentication` | Protected route check |
| ✅ `test_create_hero_with_token` | Authenticated hero creation |
| ✅ `test_create_mission_for_missing_hero_returns_404` | Hero existence check |
| ✅ `test_normal_user_cannot_delete_hero` | Role-based deletion |
| ✅ `test_admin_can_delete_mission` | Admin privileges |
| ✅ `test_normal_user_cannot_create_hero_with_level` | Schema restrictions |
| ✅ `test_admin_can_create_hero_with_custom_level` | Admin full control |
| ✅ `test_cannot_delete_hero_with_active_missions` | Business rule enforcement |

### Running a Single Test

```bash
pytest tests/test_api.py::TestAuth::test_register_user -v
```

---

## ⚠️ Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| `200 OK` | Successful request |
| `201 Created` | Resource successfully created |
| `204 No Content` | Resource successfully deleted |
| `400 Bad Request` | Invalid request data |
| `401 Unauthorized` | Missing or invalid token |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | Resource not found |
| `422 Unprocessable Entity` | Validation error |

### Example Error Responses

```json
{
    "detail": "Hero not found"
}
```

```json
{
    "detail": "Incorrect username or password"
}
```

```json
{
    "detail": "Could not validate credentials"
}
```

```json
{
    "detail": "The user doesn't have enough privileges"
}
```

---

## 🚀 Some Future Improvements

1. **Soft Delete** - Implement soft delete with `deleted_at` timestamp
2. **Audit Logs** - Track who created/updated/deleted resources
3. **Email Notifications** - Send emails on mission assignment
4. **Search & Filter** - Advanced filtering for heroes and missions
5. **API Rate Limiting** - Prevent abuse with rate limits
6. **Dockerization** - Dockerfile and docker-compose for containerized deployment
7. **CI/CD Pipeline** - GitHub Actions for automated testing and deployment
8. **API Versioning** - Support for multiple API versions
9. **Database Migrations** - Replace `create_all()` with Alembic migrations

---

## 📸 Screenshots

### Swagger UI - API Documentation
![Authentication](/screenshots/authentication_api.png)
![Heroes](/screenshots/heroes_api.png)
![Missions](/screenshots/missions_api.png)

### API Response Example
#### First need to make user register. 
![API register](/screenshots/user_register.png)
[register response](/screenshots/user_register_response.png)
#### Then in authentication:
![User Authentication](/screenshots/authentication_api.png)
[User authorized](/screenshots/user_authorized.png)
[Token creation](/screenshots/token_creation.png)
[If am I authenticate](/screenshots/auth_me.png)
#### Related with the Hero API
[Make a Hero](/screenshots/make_hero_api.png)
[Make a hero api response](/screenshots/make_hero_response.png)
[Delete Hero with Id. Only admin delete.](/screenshots/delete_hero.png)
[delete hero api response for a non admin user](/screenshots/delete_hero_response.png)
#### Related with the Mission API
[Mission create API](/screenshots/mission_create_api.png)
[Mission creation API response](/screenshots/mission_creation_response.png)
#### Logout and try to make hero and mission again to see the difference. 
[Logout](/screenshots/Logout.png)

### Test Results
![Test Results](/screenshots/tests.png)
[Test Coverage (percent)](/screenshots/test_coverage.png)

### SQLite DataBase view exapmles
[User Table](/screenshots/user_table.png)
[Mission Table](/screenshots/mission_table.png)
[Hero Table](/screenshots/hero_table.png)

---

## 👨‍💻 Author

**PAPAPANAGIOTOU PANAGIOTIS**

---

## 📝 License

This project is for educational purposes as part of the "AI for Developers" course.

---

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- SQLModel for seamless ORM + Pydantic integration
- Course instructors for the project requirements

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [JWT.io](https://jwt.io/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Made with ❤️ for the "AI for Developers" course**