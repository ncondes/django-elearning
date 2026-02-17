# eLearning Application Development Plan

## Overview

A Django-based eLearning platform supporting two user types (students and teachers), course management, real-time chat via WebSockets, and a REST API for user data.

---

## Requirements Checklist

### R1: Functional Requirements
| ID | Requirement | Phase |
|----|-------------|-------|
| R1a | Users create accounts | 1 |
| R1b | Users log in/out | 1 |
| R1c | Teachers search for students/teachers | 2 |
| R1d | Teachers add new courses | 2 |
| R1e | Students enrol on courses | 2 |
| R1f | Students leave course feedback | 2 |
| R1g | Real-time chat (WebSockets) | 3 |
| R1h | Teachers remove/block students | 2 |
| R1i | Users add status updates to home page | 2 |
| R1j | Teachers upload course materials | 2 |
| R1k | Notify teacher when student enrols | 3 |
| R1l | Notify student when new material added | 3 |

### R2: Technical Requirements
| ID | Requirement | Phase |
|----|-------------|-------|
| R2a | Correct use of models and migrations | 1-3 |
| R2b | Correct use of forms, validators, serializers | 1-3 |
| R2c | Correct use of django-rest-framework | 2 |
| R2d | Correct use of URL routing | 1-3 |
| R2e | Appropriate unit testing | 1-3 |

### R3-R5: Architecture Requirements
- **R3**: Appropriate database model for accounts, data, relationships
- **R4**: REST interface for user data access
- **R5**: Server-side code tests

---

## Project Structure

```
awd-final-coursework/
├── manage.py
├── requirements.txt
├── README.md
├── DEVELOPMENT_PLAN.md
│
├── config/                     # Project configuration
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Dev settings
│   │   └── production.py      # Prod settings
│   ├── urls.py                # Root URL configuration
│   ├── asgi.py                # ASGI config (for WebSockets)
│   └── wsgi.py
│
├── apps/                       # Django applications
│   ├── __init__.py
│   │
│   ├── accounts/              # User management
│   │   ├── __init__.py
│   │   ├── models.py          # Custom User, Student, Teacher profiles
│   │   ├── views.py           # Registration, login, profile views
│   │   ├── forms.py           # Registration, profile forms
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── signals.py         # Profile creation signals
│   │   ├── permissions.py     # Custom permissions
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_api.py
│   │
│   ├── courses/               # Course management
│   │   ├── __init__.py
│   │   ├── models.py          # Course, Enrollment, Material, Feedback
│   │   ├── views.py           # Course CRUD, enrollment, materials
│   │   ├── forms.py           # Course creation, feedback forms
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   │
│   ├── notifications/         # Notification system
│   │   ├── __init__.py
│   │   ├── models.py          # Notification model
│   │   ├── views.py
│   │   ├── signals.py         # Enrollment/material signals
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── chat/                  # Real-time chat (WebSockets)
│       ├── __init__.py
│       ├── models.py          # ChatRoom, Message
│       ├── consumers.py       # WebSocket consumers
│       ├── routing.py         # WebSocket URL routing
│       ├── views.py           # Chat room views
│       ├── urls.py
│       └── tests/
│
├── api/                        # REST API (DRF)
│   ├── __init__.py
│   ├── urls.py                # API URL routing
│   └── views.py               # API viewsets
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   └── home.html
│   ├── courses/
│   │   ├── course_list.html
│   │   ├── course_detail.html
│   │   ├── course_create.html
│   │   └── enrollment_list.html
│   ├── chat/
│   │   └── room.html
│   └── notifications/
│       └── notification_list.html
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── media/                      # User uploads
    ├── profile_photos/
    └── course_materials/
```

---

## Database Schema

### Core Models

```
┌─────────────────────────────────────────────────────────────────┐
│                           User                                   │
│  (AbstractUser - extends Django's built-in)                     │
├─────────────────────────────────────────────────────────────────┤
│  - email (unique)                                                │
│  - user_type: 'student' | 'teacher'                             │
│  - photo (ImageField)                                            │
│  - bio (TextField)                                               │
│  - created_at, updated_at                                        │
└─────────────────────────────────────────────────────────────────┘
           │
           │ 1:1
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              StudentProfile / TeacherProfile                     │
├─────────────────────────────────────────────────────────────────┤
│  StudentProfile:                                                 │
│    - user (OneToOne)                                             │
│    - enrolled_courses (M2M via Enrollment)                       │
│    - is_blocked (Boolean)                                        │
│                                                                  │
│  TeacherProfile:                                                 │
│    - user (OneToOne)                                             │
│    - department (CharField)                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         StatusUpdate                             │
├─────────────────────────────────────────────────────────────────┤
│  - user (FK → User)                                              │
│  - content (TextField)                                           │
│  - created_at                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                           Course                                 │
├─────────────────────────────────────────────────────────────────┤
│  - title                                                         │
│  - description                                                   │
│  - teacher (FK → User, teacher only)                            │
│  - created_at, updated_at                                        │
└─────────────────────────────────────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CourseMaterial                             │
├─────────────────────────────────────────────────────────────────┤
│  - course (FK → Course)                                          │
│  - title                                                         │
│  - file (FileField: pdf, images, etc.)                          │
│  - uploaded_at                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Enrollment                                │
├─────────────────────────────────────────────────────────────────┤
│  - student (FK → User, student only)                            │
│  - course (FK → Course)                                          │
│  - enrolled_at                                                   │
│  - is_blocked (Boolean)                                          │
│  unique_together: (student, course)                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       CourseFeedback                             │
├─────────────────────────────────────────────────────────────────┤
│  - enrollment (FK → Enrollment)                                  │
│  - rating (1-5)                                                  │
│  - comment (TextField)                                           │
│  - created_at                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Notification                               │
├─────────────────────────────────────────────────────────────────┤
│  - recipient (FK → User)                                         │
│  - message (TextField)                                           │
│  - notification_type: 'enrollment' | 'material' | 'other'       │
│  - is_read (Boolean)                                             │
│  - created_at                                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         ChatRoom                                 │
├─────────────────────────────────────────────────────────────────┤
│  - name                                                          │
│  - participants (M2M → User)                                     │
│  - course (FK → Course, optional, for course-specific chats)    │
│  - created_at                                                    │
└─────────────────────────────────────────────────────────────────┘
           │
           │ 1:N
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Message                                 │
├─────────────────────────────────────────────────────────────────┤
│  - room (FK → ChatRoom)                                          │
│  - sender (FK → User)                                            │
│  - content (TextField)                                           │
│  - timestamp                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Development Phases

### Phase 1: Foundation & Authentication (Week 1)

**Goal**: Set up project structure, custom user model, authentication system.

#### 1.1 Project Setup
- [ ] Restructure `config/` with split settings (base, dev, prod)
- [ ] Create `apps/` directory structure
- [ ] Set up `requirements.txt` with initial dependencies:
  ```
  Django>=5.0
  djangorestframework
  channels
  channels-redis
  Pillow
  django-crispy-forms
  crispy-bootstrap5
  ```
- [ ] Configure static/media file handling
- [ ] Set up base templates with Bootstrap 5

#### 1.2 Accounts App
- [x] Create custom User model with `user_type` field
- [x] Create StudentProfile and TeacherProfile models
- [x] Implement signals for auto-creating profiles
- [x] Create registration form with user type selection
- [x] Create login/logout views
- [x] Create profile view and edit form
- [x] Create home page view (user dashboard)
- [x] Implement StatusUpdate model and form
- [x] Write unit tests for models and views

#### 1.3 Permissions System
- [x] Create custom permission classes:
  - `IsTeacher`
  - `IsStudent`
  - `IsOwnerOrReadOnly`
- [x] Apply permissions to views

**Deliverables Phase 1**: ✅ COMPLETED
- Working registration/login system
- User profiles with photos
- Home page with status updates
- Basic permission system
- Unit tests for accounts

---

### Phase 2: Core Features (Week 2)

**Goal**: Implement courses, enrollments, search, and REST API.

#### 2.1 Courses App
- [x] Create Course model
- [x] Create CourseMaterial model with file upload
- [x] Create Enrollment model
- [x] Create CourseFeedback model
- [x] Implement course CRUD views (teacher only)
- [x] Implement course list view (all users)
- [x] Implement course detail view
- [x] Implement enrollment view (students)
- [x] Implement feedback form (enrolled students)
- [x] Implement material upload (teachers)
- [x] Implement student blocking (teachers)
- [x] Write unit tests

#### 2.2 Search Functionality
- [x] Implement user search view (teachers only)
- [x] Search by username, name, user type
- [x] Display search results with links to profiles

#### 2.3 REST API
- [x] Set up DRF configuration
- [x] Create User serializer
- [x] Create Course serializer
- [x] Create API viewsets:
  - `CourseViewSet` (CRUD for teachers, read for students)
  - `EnrollmentViewSet`
- [x] Configure API URL routing
- [x] Add API authentication (Session-based)
- [x] Write API tests

**Deliverables Phase 2**: ✅ COMPLETED
- Full course management system
- Enrollment and feedback system
- Teacher search functionality
- Student blocking
- REST API for user/course data
- Unit tests for courses and API

---

### Phase 3: Real-time Features & Notifications (Week 3)

**Goal**: Implement WebSocket chat and notification system.

#### 3.1 Notifications App
- [x] Create Notification model
- [x] Create signals for:
  - Student enrollment → notify teacher
  - New material → notify enrolled students
  - Course rating → notify teacher
- [x] Create notification list view
- [x] Mark notifications as read
- [x] Write tests

#### 3.2 Chat App (WebSockets)
- [x] Configure Django Channels
- [x] Set up ASGI application
- [x] Create ChatRoom and Message models
- [x] Create WebSocket consumer for chat
- [x] Create chat room view
- [x] Implement JavaScript WebSocket client
- [x] Features:
  - Real-time message sending/receiving
  - Message history
  - Online user indicators
- [x] Write tests for chat (models, views)

#### 3.3 Integration & Polish
- [x] Connect chat rooms to courses
- [x] Add real-time notification delivery (WebSocket)
- [x] UI/UX improvements (docs-style sidebar layout)
- [x] Responsive design check

#### 3.4 Markdown Support
- [x] Add markdown rendering for status updates (posts)
- [x] Add markdown rendering for course material descriptions
- [x] Server-side rendering with Python `markdown` library
- [x] XSS sanitization with `bleach` (no images/scripts/iframes)
- [x] Client-side live preview with `marked.js` + `DOMPurify`
- [x] Reusable markdown editor component with Write/Preview tabs

**Deliverables Phase 3**: ✅ COMPLETED
- Working notification system
- Real-time chat via WebSockets
- Complete integration of all features

---

### Phase 4: Testing & Refinement (Week 4)

**Goal**: Comprehensive testing, bug fixes, documentation.

#### 4.1 Testing
- [x] Ensure all models have tests
- [x] Ensure all views have tests
- [x] Ensure all API endpoints have tests
- [x] Test WebSocket consumers (model/view tests)
- [x] Test permission restrictions
- [ ] Integration tests for user flows

#### 4.2 Documentation
- [x] Update README with setup instructions
- [x] Document API endpoints (Swagger UI)
- [x] Add Swagger/OpenAPI documentation (drf-spectacular)
- [ ] Add inline code comments where needed

#### 4.3 Final Polish
- [x] Fix any bugs discovered
- [x] Security review (CSRF, XSS - markdown sanitization)
- [x] Final UI cleanup

**Deliverables Phase 4**: ✅ COMPLETED
- Comprehensive test suite (97 tests)
- API Documentation (Swagger UI at /api/docs/)
- Production-ready application

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | Django 5.x |
| REST API | Django REST Framework |
| WebSockets | Django Channels |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Django Templates + Bootstrap 5 |
| Real-time | Channels + Redis |
| File Storage | Django FileField (local/S3) |
| Authentication | Django built-in + DRF tokens |

---

## Key Design Decisions

### 1. Custom User Model
Using `AbstractUser` with a `user_type` field instead of separate models. This allows:
- Single authentication system
- Easy querying across user types
- Profile models for type-specific data

### 2. App Separation
Four main apps with clear responsibilities:
- **accounts**: User management, profiles, status updates
- **courses**: Course content, enrollments, feedback
- **notifications**: Cross-app notification system
- **chat**: WebSocket-based real-time communication

### 3. Split Settings
Separate settings files for different environments:
- `base.py`: Shared configuration
- `development.py`: Debug mode, SQLite
- `production.py`: Security settings, PostgreSQL

### 4. API Design
RESTful API using DRF ViewSets:
- `/api/users/` - User data (R4 requirement)
- `/api/courses/` - Course management
- `/api/enrollments/` - Enrollment management

---

## URL Structure

```
/                           → Home/landing page
/accounts/
    register/               → User registration
    login/                  → Login
    logout/                 → Logout
    profile/                → Own profile
    profile/<username>/     → View user profile
    profile/edit/           → Edit profile
    search/                 → Search users (teachers only)

/courses/
    /                       → Course list
    create/                 → Create course (teachers)
    <id>/                   → Course detail
    <id>/edit/              → Edit course (owner)
    <id>/enroll/            → Enroll (students)
    <id>/feedback/          → Leave feedback
    <id>/materials/         → View materials
    <id>/materials/upload/  → Upload material (owner)
    <id>/students/          → View enrolled students (owner)
    <id>/students/<id>/block/ → Block student

/notifications/
    /                       → Notification list
    <id>/read/              → Mark as read

/chat/
    /                       → Chat room list
    <room_id>/              → Chat room

/api/
    users/                  → User API
    courses/                → Course API
    enrollments/            → Enrollment API
```

---

## Development Workflow

1. **Start each feature with tests** (TDD approach)
2. **Create models first**, then run migrations
3. **Build views and templates** together
4. **Add API endpoints** after views work
5. **Commit frequently** with clear messages
6. **Test manually** after each feature

---

## Commands Reference

```bash
# Create new app
python manage.py startapp <appname> apps/<appname>

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Run server
python manage.py runserver

# Create superuser
python manage.py createsuperuser
```

---

## Deployment Notes

### Required Dependencies for Production

When deploying, ensure these dependencies are in `requirements.txt`:

| Package | Purpose |
|---------|---------|
| `daphne>=4.0` | ASGI server for WebSocket support (Django Channels) |
| `channels>=4.0` | WebSocket framework |
| `channels-redis>=4.1` | Redis backend for Channels |

**Why Daphne?**
- Django Channels requires an ASGI server, not WSGI (like Gunicorn)
- Daphne handles both HTTP and WebSocket connections
- It's listed in `INSTALLED_APPS` as `'daphne'` and must be installed

### Build Command

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### Start Command

```bash
daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.production` |
| `REDIS_HOST` | Yes | Redis server hostname |
| `REDIS_PORT` | Yes | Redis server port (default: 6379) |
| `DATABASE_URL` | Prod | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Prod | Comma-separated list of domains |

### Common Deployment Issues

1. **`ModuleNotFoundError: No module named 'daphne'`**
   - Add `daphne>=4.0` to `requirements.txt`

2. **WebSocket connection fails**
   - Ensure Redis is running and accessible
   - Verify `REDIS_HOST` and `REDIS_PORT` are set correctly

3. **Static files not loading**
   - Run `collectstatic` in build command
   - Use WhiteNoise middleware for serving static files

---

*Last updated: February 2026*
