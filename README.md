# eLearning Platform

A Django-based eLearning platform supporting students and teachers, with course management and real-time features.

## Features

- **User Authentication**: Register, login, logout with role selection (Student/Teacher)
- **User Profiles**: View and edit profiles with bio and photo
- **Status Updates**: Post updates with Markdown support
- **Course Management**: Teachers can create/edit courses, upload materials
- **Enrollment System**: Students can enroll in courses and leave feedback
- **Real-time Chat**: Course chat rooms with WebSocket support
- **Notifications**: Real-time notifications for enrollments, materials, ratings
- **Markdown Support**: Live preview editor with XSS sanitization
- **User Search**: Teachers can search for students and other teachers
- **REST API**: Full API with Swagger documentation (`/api/docs/`)
- **Responsive Design**: Bootstrap 5 with custom minimalistic styling

## Tech Stack

- **Backend**: Django 5.x, Django Channels (WebSockets)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Database**: SQLite (development)
- **Real-time**: Redis (via Docker)
- **Forms**: Django Crispy Forms with Bootstrap 5

## Prerequisites

- Python 3.10+
- Docker & Docker Compose (for Redis)

## Quick Start

### 1. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

### 4. Start Redis (required for real-time chat)

```bash
docker-compose up -d
```

Verify Redis is running:

```bash
docker-compose ps
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed the database (optional)

```bash
python manage.py seed_db
```

This creates:
- Superuser: `admin` / `admin123`
- Sample users (students and teachers)
- Default password for seeded users: `password123`

### 7. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Real-time Chat

The platform includes real-time course chat powered by Django Channels and Redis.

### Testing Chat with Two Users

1. Ensure Redis is running: `docker-compose up -d`
2. Start Django: `python manage.py runserver`
3. Open two browser windows (or use incognito for the second)
4. Login as different users in each window
5. Navigate to the same course and click "Chat"
6. Messages sync in real-time between both users

### Redis Management

```bash
# Start Redis
docker-compose up -d

# Stop Redis
docker-compose down

# View Redis logs
docker-compose logs redis

# Check Redis status
docker-compose ps
```

### Redis CLI (Debugging)

Access the Redis CLI to inspect keys and values:

```bash
# Open interactive Redis CLI
docker exec -it elearning_redis redis-cli

# Common commands inside Redis CLI:
KEYS *                    # List all keys
GET <key>                 # Get string value
TYPE <key>                # Check key type (string, list, set, zset, hash)
ZRANGE <key> 0 -1         # List all members of a sorted set
LRANGE <key> 0 -1         # List all items in a list
HGETALL <key>             # Get all fields in a hash
TTL <key>                 # Check time-to-live (expiration)
MONITOR                   # Watch all commands in real-time (Ctrl+C to exit)
FLUSHALL                  # Clear all data (use with caution!)
```

**Example - Inspecting Django Channels keys:**

```bash
# List all channel layer keys
docker exec elearning_redis redis-cli KEYS '*'

# Keys typically look like:
# asgi:group:chat_<course_id>       - Chat room groups
# asgi:group:notifications_<user_id> - Notification groups

# View members of a group (sorted set)
docker exec elearning_redis redis-cli ZRANGE "asgi:group:chat_1" 0 -1
```

## Management Commands

### Seed Database

```bash
# Standard seed (10 users, 8 courses)
python manage.py seed_db

# Custom number of users
python manage.py seed_db --users 20

# Large dataset (50 users, 20 courses, 100+ enrollments)
python manage.py seed_db --large
```

**Options:**
- `--users N`: Number of users to create (default: 10, ignored if --large)
- `--large`: Create a large dataset for testing pagination

**What gets created:**

| Mode             | Users | Courses | Enrollments | Feedback |
|------------------|-------|---------|-------------|----------|
| Standard         | 10    | 8       | ~20         | ~10      |
| Large (`--large`)| 50    | 20      | 100+        | 50+      |

### Flush Database

```bash
python manage.py flush_db [--keep-superusers] [--yes]
```

Options:
- `--keep-superusers`: Keep superuser accounts when flushing
- `--yes`: Skip confirmation prompt

## Project Structure

```text
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── courses/           # Course management and enrollment
│   ├── notifications/     # Real-time notifications
│   └── chat/              # WebSocket chat rooms
├── config/
│   └── settings/          # Django settings (base, development, production)
├── static/
│   └── css/               # Custom styles
├── templates/
│   ├── accounts/          # Auth templates (login, register, profile)
│   ├── courses/           # Course templates
│   ├── notifications/     # Notification templates
│   ├── chat/              # Chat templates
│   └── base_sidebar.html  # Main layout with sidebar
├── manage.py
└── requirements.txt
```

## Default Accounts

After running `seed_db`:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |
| (seeded users) | password123 | Student/Teacher |

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

*Developed for the University of London*
