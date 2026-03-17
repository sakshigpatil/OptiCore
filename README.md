# HR Management System

## Project Overview

A comprehensive HR Management System built with Django REST Framework backend and React frontend, providing role-based access control for HR administrators, managers, and employees.

### Key Features

**HR Dashboard:**
- Employee management (CRUD operations)
- Leave request approval/rejection
- Resignation request management
- Attendance overview
- Payroll management
- Department management
- Announcements and notifications

**Employee Dashboard:**
- Project and task management
- Leave application
- Resignation application
- Attendance tracking with clock-in/out
- Salary details and payslips
- Profile management
- Notifications

### Tech Stack

**Backend:**
- Django 4.2+
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- Docker & Docker Compose

**Frontend:**
- React 18+
- TailwindCSS
- React Router v6
- Redux Toolkit
- Axios
- Responsive design

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │  Django API     │    │   PostgreSQL    │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ • HR Dashboard  │    │ • REST API      │    │ • User Models   │
│ • Employee UI   │    │ • JWT Auth      │    │ • Business Data │
│ • Redux Store   │    │ • Permissions   │    │ • Relations     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

1. Clone the repository
2. Set up backend: `cd backend && pip install -r requirements.txt`
3. Set up frontend: `cd frontend && npm install`
4. Run with Docker: `docker-compose up --build`

#### Detailed Setup Instructions

- See individual README files in backend/ and frontend/ directories.


#### To run your Django backend, follow these steps in your terminal:

#### Navigate to your backend directory:
- cd backend

#### Activate your virtual environment (if you have one):
- source venv/bin/activate

#### Apply migrations (if not already done):
- python manage.py migrate

#### Start the Django development server:
- python manage.py runserver
- Your backend will now be running at http://localhost:8000.

#### If you need to run it with Docker, use:
- docker-compose up backend

