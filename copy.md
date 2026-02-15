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
- [ ] Create custom User model with `user_type` field
- [ ] Create StudentProfile and TeacherProfile models
- [ ] Implement signals for auto-creating profiles
- [ ] Create registration form with user type selection
- [ ] Create login/logout views
- [ ] Create profile view and edit form
- [ ] Create home page view (user dashboard)
- [ ] Implement StatusUpdate model and form
- [ ] Write unit tests for models and views

#### 1.3 Permissions System
- [ ] Create custom permission classes:
  - `IsTeacher`
  - `IsStudent`
  - `IsOwnerOrReadOnly`
- [ ] Apply permissions to views

**Deliverables Phase 1**:
- Working registration/login system
- User profiles with photos
- Home page with status updates
- Basic permission system
- Unit tests for accounts

---

### Phase 2: Core Features (Week 2)

**Goal**: Implement courses, enrollments, search, and REST API.

#### 2.1 Courses App
- [ ] Create Course model
- [ ] Create CourseMaterial model with file upload
- [ ] Create Enrollment model
- [ ] Create CourseFeedback model
- [ ] Implement course CRUD views (teacher only)
- [ ] Implement course list view (all users)
- [ ] Implement course detail view
- [ ] Implement enrollment view (students)
- [ ] Implement feedback form (enrolled students)
- [ ] Implement material upload (teachers)
- [ ] Implement student blocking (teachers)
- [ ] Write unit tests

#### 2.2 Search Functionality
- [ ] Implement user search view (teachers only)
- [ ] Search by username, name, user type
- [ ] Display search results with links to profiles

#### 2.3 REST API
- [ ] Set up DRF configuration
- [ ] Create User serializer
- [ ] Create Course serializer
- [ ] Create API viewsets:
  - `UserViewSet` (read own data, update profile)
  - `CourseViewSet` (CRUD for teachers, read for students)
  - `EnrollmentViewSet`
- [ ] Configure API URL routing
- [ ] Add API authentication (Token or Session)
- [ ] Write API tests

**Deliverables Phase 2**:
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
- [ ] Create Notification model
- [ ] Create signals for:
  - Student enrollment → notify teacher
  - New material → notify enrolled students
- [ ] Create notification list view
- [ ] Mark notifications as read
- [ ] Write tests

#### 3.2 Chat App (WebSockets)
- [ ] Configure Django Channels
- [ ] Set up ASGI application
- [ ] Create ChatRoom and Message models
- [ ] Create WebSocket consumer for chat
- [ ] Create chat room view
- [ ] Implement JavaScript WebSocket client
- [ ] Features:
  - Real-time message sending/receiving
  - Message history
  - Online user indicators (optional)
- [ ] Write tests for consumers

#### 3.3 Integration & Polish
- [ ] Connect chat rooms to courses (optional)
- [ ] Add real-time notification delivery (optional)
- [ ] UI/UX improvements
- [ ] Responsive design check

**Deliverables Phase 3**:
- Working notification system
- Real-time chat via WebSockets
- Complete integration of all features

---

### Phase 4: Testing & Refinement (Week 4)

**Goal**: Comprehensive testing, bug fixes, documentation.

#### 4.1 Testing
- [ ] Ensure all models have tests
- [ ] Ensure all views have tests
- [ ] Ensure all API endpoints have tests
- [ ] Test WebSocket consumers
- [ ] Test permission restrictions
- [ ] Integration tests for user flows

#### 4.2 Documentation
- [ ] Update README with setup instructions
- [ ] Document API endpoints
- [ ] Add inline code comments where needed

#### 4.3 Final Polish
- [ ] Fix any bugs discovered
- [ ] Performance review
- [ ] Security review (CSRF, XSS, etc.)
- [ ] Final UI cleanup

**Deliverables Phase 4**:
- Comprehensive test suite
- Documentation
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

## Next Steps

1. **Read and approve this plan**
2. **Start Phase 1.1**: Restructure project and install dependencies
3. **Proceed sequentially** through each phase

---

*Last updated: February 2026*
