# Connectly API 

## MO-IT152 Integrative Programming and Technologies  

---

## Project Overview

### Development Phases

### Milestone 1
- ✅ Phase 1: CRUD Operations (Week 1-2)
- ✅ Phase 2: Data Handling & Validation (Week 3)
- ✅ Phase 3: Security Implementation (Week 4)
- 🔄 Phase 4: Design Patterns (Coming Soon)

**Note:** Milestone 2 and Terminal Assessment to follow.

---

## Features

### Security Implementation
- **Token-based authentication** (REST Framework Token Auth)
- **Role-based access control (RBAC)** with Django Groups
- **Custom permissions** (IsPostAuthor) for content ownership verification
- **Secure password hashing** using multiple algorithms:
  - Argon2 (primary)
  - PBKDF2 (fallback)
  - BCrypt (fallback)
- **HTTPS support** with self-signed SSL certificates
- **Sensitive data protection** (passwords excluded from API responses)
- **Session and cookie security** (Secure, HttpOnly, HSTS)

### Core Functionality
- **User management** with secure registration and authentication
- **Post creation and management** with author relationships
- **Comment system** with validation and relational integrity
- **RESTful API design** with proper serialization
- **Data validation** at both serializer and model levels

---

## Tech Stack

- **Framework:** Django 5.2.10
- **API Framework:** Django REST Framework 3.16.1
- **Authentication:** Token Authentication
- **Database:** SQLite3 (Development)
- **SSL Support:** Werkzeug 3.1.5, pyOpenSSL 25.3.0
- **Extensions:** django-extensions 3.2.3
- **Password Hashing:** argon2-cffi 23.1.0, bcrypt 4.3.0
- **Environment Variables:** python-decouple 3.8

---

## API Endpoints

### Authentication Design
Include token in request headers for authenticated operations:
```
Authorization: Token <your-token-here>
```

## API Endpoints

### Available Endpoints

**Users**
- `GET /posts/users/` - List all users
- `POST /posts/users/` - Create a new user (register)

**Posts**
- `GET /posts/posts/` - List all posts
- `POST /posts/posts/` - Create a new post
- `GET /posts/posts/<id>/` - Retrieve a specific post (requires authentication - author only)

**Comments**
- `GET /posts/comments/` - List all comments
- `POST /posts/comments/` - Create a new comment

**Additional**
- `GET /admin/` - Django admin interface
- `GET /api-auth/` - DRF browsable API login/logout

**Note:** Only `/posts/posts/<id>/` requires authentication and author verification. All other endpoints are publicly accessible.


---

## Installation & Setup

### 1. Clone Repository & Create Virtual Environment

```bash
git clone <repository-url>
cd connectly_project

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
```
- Django==5.2.10 — Core web framework with ORM, auth, and admin.  
- djangorestframework==3.16.1 — REST API toolkit with serializers and viewsets.  
- django-extensions==3.2.3 — Extra management commands for development.  
- Werkzeug==3.1.5 — WSGI utilities and debugger.  
- pyOpenSSL==25.3.0 — SSL/TLS support for secure connections.  
- python-decouple==3.8 — Loads config from .env files.  
- argon2-cffi==23.1.0 — Argon2 password hashing.  
- bcrypt==4.3.0 — Bcrypt password hashing.  

```
### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Note:** The `.env` file is ignored by Git to protect sensitive information.

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to set username, email, and password.

### 6. Generate SSL Certificates

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

This creates `cert.pem` and `key.pem` files needed for HTTPS.

### 7. Create Authentication Token

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.get(username='your_username')
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
exit()
```

**Save your token!** You'll need it for authenticated API requests.

---

## Project Information

**Section:** H3101
**Group:** 6
**Members:** Abdelfattah, R., De Lara, C., Manicad, K., Samaniego, M., Tantoco, H.  
**Last Updated:** January 29, 2026

