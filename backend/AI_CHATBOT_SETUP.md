# AI-Powered HR Chatbot Setup Guide

## 🤖 Overview

Your HR chatbot now uses **Google Gemini AI** to intelligently answer any HR-related question while accessing real-time data from your database.

## ⚡ Features

✅ **Natural Language Understanding** - Ask questions in plain English  
✅ **Database Integration** - Access real employee, leave, and attendance data  
✅ **Context Awareness** - Understands follow-up questions  
✅ **Free Tier** - Google Gemini offers generous free limits  
✅ **Function Calling** - AI automatically queries your database when needed  

## 🚀 Quick Setup (5 minutes)

### Step 1: Get Your Free API Key

1. Visit: **https://makersuite.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated key

### Step 2: Add API Key to Environment

**Option A: Using .env file (Recommended)**

1. Create `.env` file in backend folder (if it doesn't exist):
   ```bash
   cd /home/sakshi/vsCode/MajorProject/backend
   touch .env
   ```

2. Add your API key to `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```

**Option B: Export as environment variable**

```bash
export GEMINI_API_KEY="AIzaSy...your_actual_key_here"
```

### Step 3: Restart Django Server

```bash
# Stop current server (Ctrl+C)
# Start again
python manage.py runserver 8000
```

### Step 4: Test the Chatbot

Open your HRMS frontend and try asking:
- "How many employees do we have?"
- "Show me pending leave requests"
- "What's today's attendance rate?"
- "Who works in the Marketing department?"
- "Tell me about employee benefits"

## 🎯 What the AI Can Do

### Database Queries (Real-Time Data)
- **Employee Statistics** - Total, active, department breakdown
- **Leave Management** - Pending/approved/rejected leaves
- **Attendance Data** - Daily statistics, trends
- **Department Info** - Employee counts, distributions
- **Employee Search** - Find by name, department, role

### Natural Conversations
```
User: "How many people work in marketing?"
AI: "Currently, there are 7 employees in the Marketing department."

User: "What about engineering?"
AI: "The Engineering department has 15 employees."

User: "Show me the leave requests from marketing"
AI: "Here are the pending leave requests from Marketing:..."
```

## 📊 Free Tier Limits

Google Gemini Free Tier:
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

More than enough for development and small teams!

## 🛠️ How It Works

```
User Message → Gemini AI → Understands Intent
                ↓
         Calls Database Function
                ↓
    query: get_employee_statistics()
                ↓
         Returns Real Data
                ↓
       AI Formats Response
                ↓
    User Gets Natural Answer
```

## 🔧 Configuration

The AI service is configured in:
- **AI Logic**: `apps/chatbot/ai_service.py`
- **Integration**: `apps/chatbot/utils.py`
- **Settings**: `hrms/settings/base.py`

## 🐛 Troubleshooting

### "AI Mode Not Configured" message

**Solution**: Add `GEMINI_API_KEY` to your `.env` file

### API Key Invalid Error

**Solutions**:
1. Check if key starts with `AIzaSy`
2. Verify key is not expired
3. Generate a new key from MakerSuite

### Slow Responses

**Causes**:
- First request initializes the AI (takes 2-3 seconds)
- Complex queries with large datasets
- Network latency

## 📝 Example Queries

### Employee Management
- "How many employees are active?"
- "List all departments"
- "Who works in Sales?"
- "Show employee statistics"

### Leave Management
- "Show pending leave requests"
- "How many leaves were approved this month?"
- "Who applied for leave today?"

### Attendance
- "What's today's attendance?"
- "How many people are late?"
- "Show attendance rate"

### General HR
- "What are the leave policies?"
- "Tell me about benefits"
- "What's the holiday policy?"

## 🔐 Security Notes

- ✅ API key is stored in environment variables (not in code)
- ✅ Never commit `.env` file to git
- ✅ AI only accesses data the logged-in user can see
- ✅ All database queries respect Django permissions

## 🎨 Customization

To adjust AI behavior, edit the system instruction in `apps/chatbot/ai_service.py`:

```python
self.system_instruction = """
Your custom instructions here...
"""
```

## 📚 Resources

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Get API Key](https://makersuite.google.com/app/apikey)
- [Pricing](https://ai.google.dev/pricing)

## ⚙️ Fallback Mode

If API key is not configured, the chatbot runs in **pattern-matching mode** with limited capabilities. Set up the API key to unlock full AI features!

## 🎉 Enjoy Your Intelligent HR Assistant!

Your chatbot can now understand and answer virtually any HR question while accessing real-time data from your HRMS system.
