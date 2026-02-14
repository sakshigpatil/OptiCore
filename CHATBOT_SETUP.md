# HR Chatbot - Quick Setup Guide

## Prerequisites
- Django backend running
- React frontend running
- Database configured (SQLite/PostgreSQL)

## Setup Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and apply migrations
python manage.py makemigrations chatbot
python manage.py migrate chatbot

# Populate knowledge base
python manage.py populate_chatbot_knowledge

# Start the development server
python manage.py runserver
```

### 2. Frontend Setup

The frontend components are already integrated. Just ensure your frontend server is running:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

### 3. Testing the Chatbot

1. **Access the application**
   - Open your browser and go to `http://localhost:5173` (or your configured port)

2. **Login as HR User**
   - Use credentials for a user with `ADMIN_HR` role
   - If you don't have an HR user, create one:
     ```bash
     python manage.py createsuperuser
     # Then update the role in Django admin to 'ADMIN_HR'
     ```

3. **Open the Chatbot**
   - Navigate to HR Dashboard
   - Click the purple floating button in the bottom-right corner
   - The chatbot window will open

4. **Try Sample Queries**
   - "Hi" or "Hello" - Get greeting and suggestions
   - "How many employees are active?" - Get employee statistics
   - "Show pending leave requests" - View pending leaves
   - "What's today's attendance?" - Get attendance summary
   - "Help" - See all available commands

## Verification Checklist

### Backend
- [ ] `apps.chatbot` added to `INSTALLED_APPS` in settings
- [ ] Chatbot URLs included in main `urls.py`
- [ ] Migrations created and applied
- [ ] Knowledge base populated (12 entries)
- [ ] Admin panel shows chatbot models

### Frontend
- [ ] `Chatbot.jsx` component created
- [ ] `chatbot.js` service created
- [ ] Chatbot imported in HR Dashboard
- [ ] Floating button visible on HR Dashboard
- [ ] `date-fns` package available (already in package.json)

### Database Tables
- [ ] `chatbot_chatconversation`
- [ ] `chatbot_chatmessage`
- [ ] `chatbot_chatbotknowledge`

## Troubleshooting

### Issue: Chatbot button not visible
**Solution**: Ensure you're logged in as an HR user (ADMIN_HR role)

### Issue: Import errors in Python
**Solution**: Restart Django development server

### Issue: API 404 errors
**Solution**: Verify chatbot URLs are included in `hrms/urls.py`

### Issue: No bot responses
**Solution**: Check that knowledge base is populated:
```bash
python manage.py populate_chatbot_knowledge
```

### Issue: Frontend component errors
**Solution**: Clear browser cache and restart React dev server

## API Testing (Optional)

Test the API endpoints using curl or Postman:

```bash
# Get auth token first
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "hr@example.com", "password": "password"}'

# Create a conversation
curl -X POST http://localhost:8000/api/v1/chatbot/conversations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'

# Send a message
curl -X POST http://localhost:8000/api/v1/chatbot/conversations/1/send_message/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Next Steps

1. **Customize Knowledge Base**
   - Add company-specific policies
   - Update leave types
   - Add department-specific information

2. **Extend Functionality**
   - Add more intelligent responses
   - Integrate with external APIs
   - Add analytics and metrics

3. **Deploy to Production**
   - Configure environment variables
   - Set up proper database (PostgreSQL)
   - Enable HTTPS
   - Add rate limiting

## Files Created

### Backend
```
backend/apps/chatbot/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── utils.py
├── seed_data.py
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── populate_chatbot_knowledge.py
```

### Frontend
```
frontend/src/
├── components/common/
│   └── Chatbot.jsx
├── services/
│   └── chatbot.js
└── pages/hr/
    └── Dashboard.jsx (modified)
```

### Documentation
```
CHATBOT_DOCUMENTATION.md
CHATBOT_SETUP.md (this file)
```

## Support

If you encounter any issues:
1. Check the logs in terminal/console
2. Review [CHATBOT_DOCUMENTATION.md](./CHATBOT_DOCUMENTATION.md)
3. Inspect network requests in browser DevTools
4. Check Django admin panel for data

---

**Quick Start Time**: ~5 minutes  
**Difficulty**: Easy  
**Status**: ✅ Ready to Use
