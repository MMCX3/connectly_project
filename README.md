# Connectly API 

## MO-IT152 Integrative Programming and Technologies  

---

## Project Overview

### Development Phases

### Milestone 1
- ✅ Phase 1: CRUD Operations (Weeks 1-2)
- ✅ Phase 2: Data Handling & Validation (Week 3)
- ✅ Phase 3: Security Implementation (Week 4)
- ✅ Phase 4: Design Patterns (Week 5)

### Milestone 2
- ✅ Phase 5: Adding User Interactions (Likes and Comments) (Week 6)
- ✅ Phase 6: Integrating Third-Party Services (Week 7)
- ✅ Phase 7: Building a News Feed (Weeks 8-9)

### Terminal Assessment
- 🔄 Phase 8: Privacy Settings and Role-Based Access Control (Week 10)
- 🔄 Phase 9: Performance Optimization — Pagination and Caching (Week 11)

---

## Features

### Milestone 2 Features (Weeks 6-9)

#### News Feed (Weeks 8-9)
- **Personalized feed endpoint** (`GET /feed/`) returning all posts sorted by date (newest first)
- **Pagination support** with `page` and `page_size` query parameters (default 10 posts per page, max 100)
- **Paginated response** includes `next` and `previous` navigation links

#### Third-Party Services (Week 7)
- **Google OAuth 2.0 login** via `django-allauth` and `dj-rest-auth`
- **Social login endpoint** (`POST /auth/google/login/`) accepting a Google ID token
- **Automatic user linking**: existing users are linked to their Google account; new users are auto-created from Google profile info
- **Error handling**: returns 401 for invalid/expired tokens and OAuth denial

#### User Interactions (Week 6)
- **Like system** with `Like` model enforcing unique-per-user constraints
- **Post-specific comments** via dedicated endpoints separate from the global comment list
- **Paginated comments** per post (default 10, max 50) with newest-first ordering
- **Like/unlike toggle** with duplicate-like guard (returns 400 if already liked)
- **Aggregate counts** on posts: `like_count` and `comment_count` returned in all post responses without extra API calls

### Milestone 1 Features (Weeks 1-5)

### Design Patterns (Week 5)
- **Singleton Pattern** for centralized resource management:
  - ConfigManager for application-wide configuration settings
  - LoggerSingleton for consistent logging across all API operations (e.g., API initialization, user/post creation, post retrieval, etc.)
- **Factory Pattern** for standardized object creation:
  - PostFactory for validated post creation with type-specific requirements
  - Centralized validation logic for text, image, and video posts
- **Extensible post types** with metadata support (text, image, video)

### Security Implementation (Week 4)
- **Token-based authentication** (REST Framework Token Auth)
- **Role-based access control (RBAC)** with custom permissions
- **Custom permissions** (IsPostAuthorOrAdmin) for content ownership and moderation
- **Secure password hashing** using multiple algorithms:
  - Argon2 (primary)
  - PBKDF2 (fallback)
  - BCrypt (fallback)
- **HTTPS support** with self-signed SSL certificates
- **Sensitive data protection** (passwords excluded from API responses)
- **Session and cookie security** (Secure, HttpOnly, HSTS)

### Core Functionality (Weeks 1-3)
- **User management** with secure registration and authentication
- **Post creation and management** with author relationships
- **Comment system** with validation and relational integrity
- **RESTful API design** with proper serialization
- **Data validation** at both serializer and model levels
- **Comprehensive logging** for API operations and error tracking

## CRUD Implementation Strategy

### Posts: Full CRUD (Week 4 Focus)
Posts implement complete CRUD operations (CREATE, READ, UPDATE, DELETE) with role-based access control:
- **Regular users** can create posts and modify/delete their own posts
- **Admin users** can modify/delete any post for content moderation
- Demonstrates RBAC implementation as required by Week 4 manual

### Users & Comments: Basic Operations (Weeks 1-3)
Users and Comments currently implement CREATE and READ operations:
- Foundation established per Weeks 1-3 requirements
- UPDATE/DELETE operations to be considered for future iterations based on:
  - User profile management requirements
  - Comment moderation policies
  - Security considerations
- Current focus aligns with Week 4 manual emphasis on Post modification and RBAC testing

---

## Tech Stack

- **Framework:** Django 5.2.10
- **API Framework:** Django REST Framework 3.16.1
- **Authentication:** Token Authentication, Google OAuth 2.0
- **Social Auth:** django-allauth 0.63.6, dj-rest-auth 7.0.1
- **Database:** SQLite3 (Development)
- **SSL Support:** Werkzeug 3.1.5, pyOpenSSL 25.3.0
- **Extensions:** django-extensions 3.2.3
- **Password Hashing:** argon2-cffi 23.1.0, bcrypt 4.3.0
- **Environment Variables:** python-decouple 3.8
- **HTTP:** requests, PyJWT 2.8.0

---

## API Endpoints

### Authentication Design
Include token in request headers for authenticated operations:
```
Authorization: Token <your-token-here>
```

### Available Endpoints

**Authentication**
- `POST /api-token-auth/` - Obtain authentication token (no auth required)
- `POST /auth/google/login/` - Login or register via Google OAuth (no auth required)

**Users**
- `POST /posts/users/` - Create a new user / Register (no auth required)
- `GET /posts/users/` - List all users (requires authentication)

**Posts**
- `GET /posts/posts/` - List all posts (requires authentication)
- `POST /posts/posts/` - Create a new post (requires authentication)
- `GET /posts/posts/<id>/` - Retrieve a specific post (requires authentication)
- `PUT /posts/posts/<id>/` - Update a specific post (requires authentication + author or admin)
- `DELETE /posts/posts/<id>/` - Delete a specific post (requires authentication + author or admin)

**Comments**
- `GET /posts/comments/` - List all comments (requires authentication)
- `POST /posts/comments/` - Create a new comment (requires authentication)
- `GET /posts/<id>/comments/` - List comments for a specific post, paginated (requires authentication)
- `POST /posts/<id>/comment/` - Add a comment to a specific post (requires authentication)

**Likes**
- `POST /posts/<id>/like/` - Like a post (requires authentication)
- `DELETE /posts/<id>/like/` - Unlike a post (requires authentication)

**Feed**
- `GET /feed/` - Retrieve paginated feed sorted by newest first (requires authentication)
  - Query params: `?page=<n>` and `?page_size=<n>` (default: 10, max: 100)

**Additional**
- `GET /admin/` - Django admin interface
- `GET /api-auth/` - DRF browsable API login/logout

**Note:** Only user registration (`POST /posts/users/`), token authentication (`POST /api-token-auth/`), and Google OAuth (`POST /auth/google/login/`) are publicly accessible. All other endpoints require token authentication.

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
- django-allauth==0.63.6 — Social account authentication (Google OAuth).  
- dj-rest-auth==7.0.1 — REST endpoints for authentication including social login.
- PyJWT==2.8.0 — JSON Web Token support.  
- requests — HTTP library for third-party service integration.  
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

### 6. Set Up Admin Group for RBAC

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group, User

# Create Admin group
admin_group, created = Group.objects.get_or_create(name="Admin")

# Assign superuser to Admin group
admin_user = User.objects.get(username='your_admin_username')
admin_user.groups.add(admin_group)

print(f"Admin groups: {[g.name for g in admin_user.groups.all()]}")
exit()
```

### 7. Generate SSL Certificates

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

This creates `cert.pem` and `key.pem` files needed for HTTPS.

### 8. Create Authentication Token

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
### IMPORTANT!
**Save your token!** You'll need it for authenticated API requests.

### 9. Configure Google OAuth

> **Prerequisites:** Set up your own Google Cloud project and OAuth credentials before using the Playground. 

**Quick summary of required setup:** 
1. Create a Google Cloud project at [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Enable the **Google People API**
3. Configure the **OAuth consent screen** (External, add email + profile scopes)
4. Create **OAuth credentials** (Web application) and add these redirect URIs:
```
   https://127.0.0.1:8000/accounts/google/login/callback/
   https://developers.google.com/oauthplayground
```
5. Register the credentials in **Django Admin → Social Applications**

**Get a Google OAuth access token:**
1. Go to [https://developers.google.com/oauthplayground/](https://developers.google.com/oauthplayground/)
2. Click the gear icon → check **Use your own OAuth credentials** → paste your Client ID and Secret
3. Select **Google OAuth API v2** (email and profile only) and authorize
4. Click **Exchange authorization code for tokens** and copy the **Access token**

**Get your API token:**
```
POST https://127.0.0.1:8000/auth/google/login/
Content-Type: application/json

{
  "access_token": "PASTE_TOKEN_FROM_PLAYGROUND_HERE"
}
```
The response will return a token key. Use this for all subsequent authenticated requests.

> **Note:** The token returned here is your **Django token key**, not the Google access token. Use the Django token key in the `Authorization: Token ...` header for all protected endpoints. You can also find any user's token at any time in **Django Admin → Auth Token → Tokens**.

**Using the token in protected endpoints:**

In your request headers, add:
```
Key:   Authorization
Value: Token <your-token-key>
```

**Running the server:**
```bash
python manage.py runserver_plus --cert-file cert.pem --key-file key.pem
```
This is required as the project uses HTTPS with SSL cert and RSA encryption.

---
---

## Supplementary Files

> **Note:** Files are accessible via MMDC email only.

- [Milestone 1 — Google Sheets](<https://docs.google.com/spreadsheets/d/1eOkYaJPecwkgnQrIF1lsgMLdo0pJ7jp2sNyWqmKj8rI/edit?usp=sharing>)
- [Milestone 2 — Google Sheets](<https://docs.google.com/spreadsheets/d/1RcifZ7vuT8dULLdRq9ptvxSHtVkN-Y3yuMrduax9S2M/edit?usp=sharing>)

## Project Information

**Section:** H3101  
**Group:** 6  
**Members:** Abdelfattah, R., De Lara, C., Manicad, K., Samaniego, M., Tantoco, H.  
**Last Updated:** March 15, 2026

**March 15, 2026 (MS2 Revisions):** Modified code to meet MS2 grading criteria — upgraded django-allauth to 0.63.6 and dj-rest-auth to 7.0.1 for Python 3.14 compatibility, applied code improvements for correctness, variable naming, and reusability.

**March 16, 2026 (MS2 Revisions):** Applied overall format consistency across all Python files — added missing class docstrings, method docstrings, and inline comments. Wired `ConfigManager.DEFAULT_PAGE_SIZE` into pagination classes. Registered Post, Comment, and Like models in Django Admin. Updated default page size from 5 to 10 to match ConfigManager.