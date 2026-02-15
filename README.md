# eLearning Platform

A Django-based eLearning platform supporting students and teachers, with course management and real-time features.

## Features

- **User Authentication**: Register, login, logout with role selection (Student/Teacher)
- **User Profiles**: View and edit profiles with bio and photo
- **Status Updates**: Post updates to your home page
- **Course Management**: Teachers can create/edit courses, upload materials
- **Enrollment System**: Students can enroll in courses and leave feedback
- **User Search**: Teachers can search for students and other teachers
- **REST API**: Full API for courses and enrollments
- **Responsive Design**: Bootstrap 5 with custom minimalistic styling

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Database**: SQLite (development)
- **Forms**: Django Crispy Forms with Bootstrap 5

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

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Seed the database (optional)

```bash
python manage.py seed_db
```

This creates:
- Superuser: `admin` / `admin123`
- Sample users (students and teachers)
- Default password for seeded users: `password123`

### 5. Run the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

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

```
├── apps/
│   └── accounts/          # User authentication and profiles
├── config/
│   └── settings/          # Django settings (base, development, production)
├── static/
│   └── css/               # Custom styles
├── templates/
│   ├── accounts/          # Auth templates (login, register, profile)
│   └── base.html          # Base template
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
