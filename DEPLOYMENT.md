# Deployment Guide

## Overview
This guide covers deployment of the HR Management System to various cloud platforms.

## Prerequisites
- Docker and Docker Compose installed
- Git repository set up
- Cloud platform account (Vercel, Railway, Render, etc.)

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hrms-system
```

### 2. Environment Setup
```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your configuration

# Frontend  
cd ../frontend
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run with Docker Compose
```bash
# From project root
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/

### 4. Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load seed data
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/departments.json
python manage.py loaddata fixtures/employees.json

# Run development server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Production Deployment

### Option 1: Railway (Recommended for Backend)

#### Backend Deployment on Railway

1. **Create Railway Account**: Sign up at [railway.app](https://railway.app)

2. **Create New Project**: 
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure Environment Variables**:
   ```
   DJANGO_SETTINGS_MODULE=hrms.settings.production
   SECRET_KEY=your-production-secret-key
   DB_NAME=railway
   DB_USER=postgres
   DB_PASSWORD=auto-generated
   DB_HOST=auto-generated
   DB_PORT=5432
   ```

4. **Add PostgreSQL Database**:
   - Add PostgreSQL service to your project
   - Railway will auto-configure database credentials

5. **Deploy Configuration**:
   - Create `railway.json` in project root:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "backend/Dockerfile"
     },
     "deploy": {
       "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn hrms.wsgi:application --bind 0.0.0.0:$PORT",
       "healthcheckPath": "/api/v1/health/",
       "healthcheckTimeout": 100,
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

#### Production Settings (backend/hrms/settings/production.py)
```python
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [
    'your-app-name.railway.app',
    'localhost',
    '127.0.0.1',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",
]

# Static files (use WhiteNoise for serving)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Option 2: Vercel (Recommended for Frontend)

#### Frontend Deployment on Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Build Configuration**:
   - Ensure `vite.config.js` is properly configured
   - Update environment variables in `.env.production`:
   ```
   VITE_API_URL=https://your-backend-domain.railway.app/api/v1
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Configure Environment Variables in Vercel**:
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add your production environment variables

5. **Vercel Configuration** (`vercel.json`):
   ```json
   {
     "framework": "vite",
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "devCommand": "npm run dev",
     "installCommand": "npm install",
     "routes": [
       { "handle": "filesystem" },
       { "src": "/(.*)", "dest": "/index.html" }
     ]
   }
   ```

### Option 3: Docker Deployment (VPS/Cloud)

#### For DigitalOcean, AWS EC2, etc.

1. **Server Setup**:
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clone and Configure**:
   ```bash
   git clone <repository-url>
   cd hrms-system
   
   # Set up environment variables
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit with production values
   ```

3. **Production Docker Compose** (`docker-compose.prod.yml`):
   ```yaml
   version: '3.8'
   
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: ${DB_NAME}
         POSTGRES_USER: ${DB_USER}
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - postgres_data:/var/lib/postgresql/data/
       restart: unless-stopped
   
     backend:
       build: ./backend
       command: gunicorn hrms.wsgi:application --bind 0.0.0.0:8000
       environment:
         - DJANGO_SETTINGS_MODULE=hrms.settings.production
       depends_on:
         - db
       restart: unless-stopped
   
     frontend:
       build: ./frontend
       restart: unless-stopped
   
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
         - ./ssl:/etc/nginx/ssl:ro
       depends_on:
         - backend
         - frontend
       restart: unless-stopped
   
   volumes:
     postgres_data:
   ```

4. **Deploy**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

### Option 4: Heroku

#### Backend on Heroku

1. **Install Heroku CLI**
2. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Configure Environment Variables**:
   ```bash
   heroku config:set DJANGO_SETTINGS_MODULE=hrms.settings.production
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Create Procfile**:
   ```
   release: python manage.py migrate
   web: gunicorn hrms.wsgi:application --log-file -
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

## Database Setup

### Initial Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Load Sample Data
```bash
python manage.py loaddata fixtures/departments.json
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/employees.json
```

## SSL Configuration

### Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Maintenance

### Health Check Endpoints
- Backend: `GET /api/v1/health/`
- Database: `GET /api/v1/health/db/`

### Logging
- Backend logs: `/app/logs/django.log`
- Access logs: Configure in nginx
- Error tracking: Consider Sentry integration

### Backup
```bash
# Database backup
pg_dump -h localhost -U postgres hrms_db > backup.sql

# Restore
psql -h localhost -U postgres -d hrms_db < backup.sql
```

## Performance Optimization

### Backend
- Use Redis for caching
- Optimize database queries
- Configure CDN for static files
- Use connection pooling

### Frontend
- Enable gzip compression
- Optimize images
- Use service workers
- Implement lazy loading

## Security Checklist

- [ ] HTTPS enabled
- [ ] Strong SECRET_KEY in production
- [ ] Database credentials secure
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation in place
- [ ] File upload restrictions
- [ ] Security headers configured
- [ ] Regular security updates

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ALLOWED_ORIGINS in settings
2. **Database Connection**: Verify database credentials
3. **Static Files**: Run `collectstatic` and check STATIC_URL
4. **API Timeouts**: Increase timeout values
5. **Memory Issues**: Monitor and scale as needed

### Debug Commands
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell

# Check migrations
python manage.py showmigrations
```