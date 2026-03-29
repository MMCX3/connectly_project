# Connectly API 

## MO-IT152 Integrative Programming and Technologies  

---

## Project Overview

<details>
<summary>Branch History</summary>

| Milestone | Branch |
|---|---|
| Milestone 1 | `main` |
| Milestone 2 | `functionality` |
| Milestone 2 Revised | `functionality-revised-ms2` |
| Terminal Assessment | `enhancement` |

</details>

<details>
<summary>Development Phases</summary>

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
- ✅ Phase 8: Privacy Settings and Role-Based Access Control (Week 10)
- ✅ Phase 9: Performance Optimization — Pagination and Caching (Week 11)

</details>

---

## Features

<details>
<summary>Terminal Assessment Features (Weeks 10-11)</summary>

### Privacy Settings and Role-Based Access Control (Week 10)
- **Privacy field on posts** (`public` / `private`) controlling post visibility
- **Private post enforcement** across all read endpoints: `GET /posts/posts/`, `GET /posts/posts/<id>/`, `GET /posts/<id>/comments/`, `GET /posts/comments/`, and `GET /feed/` — private posts visible only to their owner
- **Role-based access control** with three roles: `admin`, `user`, and `guest`
- **Guest restrictions**: read access to public posts only; blocked from creating posts, comments, and likes
- **Admin-only delete**: only admin users can delete posts (`DELETE /posts/posts/<id>/`) or comments (`DELETE /posts/<id>/comment/<id>/`)
- **Two-layer privacy defense**: query-level filtering (Q filter) combined with object-level permission enforcement (`EnforcePrivacySettings`)
- **Automatic UserProfile creation** via Django signal on every new user registration

### Performance Optimization (Week 11)
- **Feed pagination** via `GET /feed/` with `page` and `page_size` query parameters (default: 10, max: 100)
- **Feed, post list, and post detail caching** using Django's built-in cache framework — per-user per-page cache keys with 5-minute TTL
- **Targeted cache invalidation** on post/comment/like mutations — invalidates only the acting user's relevant cache keys instead of clearing the entire cache
- **`X-Cache-Status` response header** (`HIT` / `MISS`) to observe cache behavior during testing
- **ConfigManager-driven pagination defaults** — single source of truth for page size across all paginated endpoints

</details>

<details>
<summary>Milestone 2 Features (Weeks 6-9)</summary>

### News Feed (Weeks 8-9)
- **Personalized feed endpoint** (`GET /feed/`) returning all posts sorted by date (newest first)
- **Pagination support** with `page` and `page_size` query parameters (default 10 posts per page, max 100)
- **Paginated response** includes `next` and `previous` navigation links

### Third-Party Services (Week 7)
- **Google OAuth 2.0 login** via `django-allauth` and `dj-rest-auth`
- **Social login endpoint** (`POST /auth/google/login/`) accepting a Google ID token
- **Automatic user linking**: existing users are linked to their Google account; new users are auto-created from Google profile info
- **Error handling**: returns 401 for invalid/expired tokens and OAuth denial

### User Interactions (Week 6)
- **Like system** with `Like` model enforcing unique-per-user constraints
- **Post-specific comments** via dedicated endpoints separate from the global comment list
- **Paginated comments** per post (default 10, max 50) with newest-first ordering
- **Like/unlike toggle** with duplicate-like guard (returns 400 if already liked)
- **Aggregate counts** on posts: `like_count` and `comment_count` returned in all post responses without extra API calls

</details>

<details>
<summary>Milestone 1 Features (Weeks 1-5)</summary>

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
- **Custom permissions** (`RoleBasedAccessControl`, `EnforcePrivacySettings`) for content ownership and moderation
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

</details>

---

## CRUD Implementation Strategy

<details>
<summary>Posts: CREATE, READ, DELETE (Week 4 + Terminal Assessment)</summary>

Posts implement CREATE, READ, and DELETE operations with role-based access control:
- **All authenticated users** can create posts and read public posts
- **Post owners** can read their own private posts
- **Admin users** can delete any post for content moderation
- Demonstrates RBAC and privacy enforcement as required by Terminal Assessment

</details>

<details>
<summary>Users & Comments: Basic Operations (Weeks 1-3)</summary>

Users and Comments currently implement CREATE and READ operations:
- Foundation established per Weeks 1-3 requirements
- Comment DELETE added in Terminal Assessment, restricted to admin only
- Current focus aligns with Terminal Assessment emphasis on privacy and RBAC

</details>

---

## Tech Stack

<details>
<summary>View Tech Stack</summary>

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

</details>

---

## API Endpoints

<details>
<summary>Authentication Design</summary>

Include token in request headers for authenticated operations:
```
Authorization: Token <your-token-here>
```

</details>

<details>
<summary>Available Endpoints</summary>

**Authentication**
- `POST /api-token-auth/` - Obtain authentication token (no auth required)
- `POST /auth/google/login/` - Login or register via Google OAuth (no auth required)

**Users**
- `POST /posts/users/` - Create a new user / Register (no auth required)
- `GET /posts/users/` - List all users (requires authentication)

**Posts**
- `GET /posts/posts/` - List all posts (requires authentication; private posts visible to owner only)
- `POST /posts/posts/` - Create a new post (requires authentication; guests blocked)
- `GET /posts/posts/<id>/` - Retrieve a specific post (requires authentication; private posts visible to owner only)
- `DELETE /posts/posts/<id>/` - Delete a specific post (requires authentication + admin role)

**Comments**
- `GET /posts/comments/` - List all comments (requires authentication; filters out comments on private posts)
- `POST /posts/comments/` - Create a new comment (requires authentication; guests blocked)
- `GET /posts/<id>/comments/` - List comments for a specific post, paginated (requires authentication; private posts visible to owner only)
- `POST /posts/<id>/comment/` - Add a comment to a specific post (requires authentication; guests blocked)
- `DELETE /posts/<id>/comment/<comment_id>/` - Delete a specific comment (requires authentication + admin role)

**Likes**
- `POST /posts/<id>/like/` - Like a post (requires authentication; guests blocked)
- `DELETE /posts/<id>/like/` - Unlike a post (requires authentication; guests blocked)

**Feed**
- `GET /feed/` - Retrieve paginated feed sorted by newest first (requires authentication; private posts visible to owner only)
  - Query params: `?page=<n>` and `?page_size=<n>` (default: 10, max: 100)

**Additional**
- `GET /admin/` - Django admin interface
- `GET /api-auth/` - DRF browsable API login/logout

**Note:** Only user registration (`POST /posts/users/`), token authentication (`POST /api-token-auth/`), and Google OAuth (`POST /auth/google/login/`) are publicly accessible without a token. All other endpoints require token authentication.

</details>

<details>
<summary>Role-Based Access Control Summary</summary>

| Endpoint | Method | Guest | User | Admin |
|---|---|---|---|---|
| `POST /posts/users/` | Register | ✅ | ✅ | ✅ |
| `GET /posts/users/` | List users | ✅ | ✅ | ✅ |
| `POST /api-token-auth/` | Get token | ✅ | ✅ | ✅ |
| `POST /auth/google/login/` | Google login | ✅ | ✅ | ✅ |
| `GET /posts/posts/` | List posts | ✅ public only | ✅ public + own private | ✅ public + own private |
| `POST /posts/posts/` | Create post | ❌ 403 | ✅ | ✅ |
| `GET /posts/posts/<id>/` | Get post | ✅ public only | ✅ public + own private | ✅ public + own private |
| `DELETE /posts/posts/<id>/` | Delete post | ❌ 403 | ❌ 403 | ✅ |
| `GET /posts/comments/` | List all comments | ✅ public posts only | ✅ public + own private | ✅ public + own private |
| `POST /posts/comments/` | Create comment | ❌ 403 | ✅ | ✅ |
| `GET /posts/<id>/comments/` | List post comments | ✅ public posts only | ✅ public + own private | ✅ public + own private |
| `POST /posts/<id>/comment/` | Add comment to post | ❌ 403 | ✅ public + own private | ✅ |
| `DELETE /posts/<id>/comment/<id>/` | Delete comment | ❌ 403 | ❌ 403 | ✅ |
| `POST /posts/<id>/like/` | Like post | ❌ 403 | ✅ | ✅ |
| `DELETE /posts/<id>/like/` | Unlike post | ❌ 403 | ✅ | ✅ |
| `GET /feed/` | News feed | ✅ public only | ✅ public + own private | ✅ public + own private |

</details>

---

## Installation & Setup

<details>
<summary>1. Clone Repository & Create Virtual Environment</summary>
  
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

</details>

<details>
<summary>2. Install Dependencies</summary>

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

</details>

<details>
<summary>3. Configure Environment Variables</summary>

Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Note:** The `.env` file is ignored by Git to protect sensitive information.

</details>

<details>
<summary>4. Run Migrations</summary>

```bash
python manage.py makemigrations
python manage.py migrate
```

</details>

<details>
<summary>5. Create Superuser (Optional)</summary>

```bash
python manage.py createsuperuser
```

Follow prompts to set username, email, and password.

</details>

<details>
<summary>6. Set Up Admin Group for RBAC</summary>

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

</details>

<details>
<summary>7. Set User Role via Django Shell</summary>

New users are assigned the `user` role by default. To assign a different role:

```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
user.profile.role = 'admin'  # options: 'user', 'admin', 'guest'
user.profile.save()

print(f"Role set: {user.profile.role}")
exit()
```

</details>

<details>
<summary>8. Generate SSL Certificates</summary>

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

This creates `cert.pem` and `key.pem` files needed for HTTPS.

</details>

<details>
<summary>9. Create Authentication Token</summary>

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

**IMPORTANT!** Save your token — you'll need it for authenticated API requests.

</details>

<details>
<summary>10. Configure Google OAuth</summary>

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

</details>

---

## Supplementary Files

> **Note:** Files are accessible via MMDC email only.

- [Milestone 1 — Google Sheets](<https://docs.google.com/spreadsheets/d/1eOkYaJPecwkgnQrIF1lsgMLdo0pJ7jp2sNyWqmKj8rI/edit?usp=sharing>)
- [Milestone 2 & TA — Google Sheets](<https://docs.google.com/spreadsheets/d/1RcifZ7vuT8dULLdRq9ptvxSHtVkN-Y3yuMrduax9S2M/edit?usp=sharing>)

---

## Project Information

**Section:** H3101  
**Group:** 6  
**Members:** Abdelfattah, R., De Lara, C., Manicad, K., Samaniego, M., Tantoco, H.  
**Last Updated:** March 29, 2026

<details>
<summary>Revision History</summary>

**March 15, 2026 (MS2 Revisions):** Modified code to meet MS2 grading criteria - upgraded django-allauth to 0.63.6 and dj-rest-auth to 7.0.1 for Python 3.14 compatibility, applied code improvements for correctness, variable naming, and reusability.

**March 16, 2026 (MS2 Revisions):** Applied overall format consistency across all Python files - added missing class docstrings, method docstrings, and inline comments. Wired `ConfigManager.DEFAULT_PAGE_SIZE` into pagination classes. Registered Post, Comment, and Like models in Django Admin. Updated default page size from 5 to 10 to match ConfigManager.

**March 20, 2026 (Terminal Assessment):** Implemented Phase 8 and Phase 9 requirements. Added privacy field to Post model and PostSerializer. Enforced privacy across all read endpoints using Q filters and EnforcePrivacySettings permission class. Added EnforcePrivacySettings to PostCommentView. Fixed privacy leak in CommentListCreate. Removed IsOwnerOrAdmin dead code. Admin-only delete enforced on posts and comments via RoleBasedAccessControl. Feed pagination and caching implemented with per-user per-page cache keys, 5-minute TTL, cache invalidation on mutation, and X-Cache-Status response header.

**March 24, 2026 (Logging Enhancement):** Added cache HIT and MISS logger calls to `FeedView` in `views.py` for improved observability — terminal now logs `Feed cache HIT for <username> (page <n>)` and `Feed cache MISS for <username> (page <n>)` on every feed request.

**March 29, 2026 (TA Revisions):** Applied post-feedback code improvements — extended caching to `PostListCreate` and `PostDetailView` with per-user cache keys and `X-Cache-Status` headers; replaced `cache.clear()` with targeted `invalidate_post_caches()` helper for surgical cache invalidation; scoped `RoleBasedAccessControl.has_object_permission()` DELETE restriction to `Post` and `Comment` objects only, excluding `Like` deletions (unlike is a user action, not a moderation action); fixed `PostLikeView.delete()` to manually enforce privacy instead of calling `check_object_permissions()` to prevent regular users from being incorrectly blocked when unliking; added privacy enforcement to `CommentListCreate.post()` to close the privacy hole on the global comment endpoint.

</details>
