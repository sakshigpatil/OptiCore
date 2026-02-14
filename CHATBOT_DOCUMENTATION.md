# HR Chatbot - Documentation

## Overview

The HR Chatbot is an intelligent AI assistant integrated into the HR dashboard that helps HR personnel with various tasks such as:

- **Employee Statistics** - Get real-time employee counts, department breakdowns
- **Leave Management** - View pending leave requests, leave statistics
- **Attendance Tracking** - Check today's attendance, absence reports
- **Department Information** - View department distribution and details
- **HR Knowledge Base** - Answer common HR policy and process questions

## Features

### 1. Conversational Interface
- Natural language processing for user queries
- Context-aware responses
- Quick action buttons for common tasks
- Message history and conversation management

### 2. Real-time Data Integration
- Live employee statistics
- Pending leave request counts
- Today's attendance summary
- Department distribution

### 3. Knowledge Base
The chatbot includes a comprehensive knowledge base covering:
- Leave policies and approval processes
- Attendance tracking procedures
- Employee management
- Payroll information
- Company policies
- Benefits and recruitment

### 4. Multiple Conversations
- Create and manage multiple chat conversations
- Conversation history saved
- Quick access to previous chats
- Delete old conversations

## How to Use

### Accessing the Chatbot

1. **Log in** as an HR user (role: ADMIN_HR)
2. Navigate to the **HR Dashboard**
3. Click the **floating chat button** (purple button with AI badge) in the bottom-right corner

### Asking Questions

You can ask the chatbot questions in natural language:

**Example Queries:**
- "How many employees are active?"
- "Show pending leave requests"
- "What's today's attendance?"
- "Show department statistics"
- "How do I approve a leave request?"
- "What is the leave policy?"

### Quick Actions

The chatbot provides quick action buttons for common tasks:
- 👥 Employee Stats
- 📅 Pending Leaves
- ⏰ Today's Attendance
- 🏢 Departments
- ❓ Help

### Managing Conversations

- **New Conversation**: Click the "New Chat" button
- **Switch Conversations**: Click on any conversation in the left sidebar
- **Delete Conversation**: Hover over a conversation and click the trash icon

## API Endpoints

### Conversations

```
GET    /api/v1/chatbot/conversations/              # List all conversations
POST   /api/v1/chatbot/conversations/              # Create new conversation
GET    /api/v1/chatbot/conversations/{id}/         # Get conversation details
DELETE /api/v1/chatbot/conversations/{id}/         # Delete conversation
POST   /api/v1/chatbot/conversations/{id}/send_message/  # Send message
POST   /api/v1/chatbot/conversations/{id}/mark_read/     # Mark as read
GET    /api/v1/chatbot/conversations/quick_actions/      # Get quick actions
```

### Messages

```
GET /api/v1/chatbot/messages/               # List messages
GET /api/v1/chatbot/messages/unread_count/  # Get unread count
```

### Knowledge Base

```
GET /api/v1/chatbot/knowledge/         # List knowledge entries
GET /api/v1/chatbot/knowledge/search/  # Search knowledge base
```

## Database Models

### ChatConversation
- `user` - ForeignKey to User
- `title` - Conversation title
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `is_active` - Active status

### ChatMessage
- `conversation` - ForeignKey to ChatConversation
- `sender` - USER, BOT, or SYSTEM
- `message` - Message text
- `metadata` - JSON field for additional data
- `created_at` - Creation timestamp
- `is_read` - Read status

### ChatbotKnowledge
- `category` - Category (GENERAL, LEAVE, ATTENDANCE, etc.)
- `question` - Question text
- `answer` - Answer text
- `keywords` - JSON array of keywords
- `priority` - Display priority
- `is_active` - Active status

## Customization

### Adding New Knowledge

You can add new knowledge entries through:

1. **Django Admin Panel**:
   - Go to `/admin/chatbot/chatbotknowledge/`
   - Click "Add Chatbot Knowledge"
   - Fill in the fields and save

2. **Management Command**:
   - Edit `apps/chatbot/seed_data.py`
   - Add new entries to `CHATBOT_KNOWLEDGE` list
   - Run: `python manage.py populate_chatbot_knowledge`

### Extending Chatbot Capabilities

Edit `apps/chatbot/utils.py` to add new message processing logic:

```python
def process_chat_message(message, user):
    # Add your custom logic here
    if 'custom_keyword' in message_lower:
        # Process and return response
        return {
            'message': 'Your response',
            'metadata': {'type': 'custom'}
        }
```

## Frontend Components

### Chatbot Component
Location: `frontend/src/components/common/Chatbot.jsx`

**Props:**
- `isOpen` (boolean) - Controls chatbot visibility
- `onClose` (function) - Callback when chat is closed

**Features:**
- Responsive design
- Real-time message updates
- Typing indicators
- Auto-scroll to latest message
- Suggestion chips

### Integration

The chatbot is integrated into the HR Dashboard:

```jsx
import Chatbot from '../../components/common/Chatbot';

const [isChatbotOpen, setIsChatbotOpen] = useState(false);

// Floating button
<button onClick={() => setIsChatbotOpen(true)}>
  <ChatBubbleLeftRightIcon />
</button>

// Chatbot component
<Chatbot 
  isOpen={isChatbotOpen} 
  onClose={() => setIsChatbotOpen(false)} 
/>
```

## Styling

The chatbot uses Tailwind CSS with a purple/indigo gradient theme:
- Primary: Indigo-600 to Purple-600
- Background: White with gray accents
- Shadows: Soft shadow-lg for depth
- Animations: Smooth transitions and hover effects

## Troubleshooting

### Chatbot doesn't open
- Ensure you're logged in as HR user (ADMIN_HR role)
- Check browser console for JavaScript errors
- Verify backend API is running

### Messages not sending
- Check network tab for API errors
- Ensure conversation is created
- Verify authentication token is valid

### No responses from chatbot
- Check `apps/chatbot/utils.py` for errors
- Verify database has knowledge entries
- Check Django logs for exceptions

### Knowledge base empty
- Run: `python manage.py populate_chatbot_knowledge`
- Check Django admin for knowledge entries
- Verify migrations are applied

## Future Enhancements

Potential improvements:
- [ ] Integration with OpenAI/GPT for more intelligent responses
- [ ] Voice input/output
- [ ] File upload support (documents, images)
- [ ] Chatbot analytics and metrics
- [ ] Multi-language support
- [ ] Sentiment analysis
- [ ] Automated workflows (approve leaves via chat)
- [ ] Integration with calendar for scheduling
- [ ] Employee-facing chatbot version

## Security Considerations

- Only HR users (ADMIN_HR) can access the chatbot
- All API requests require authentication
- Messages are stored securely in the database
- No sensitive data (passwords, PII) should be exposed in responses
- Implement rate limiting for production use

## Performance

- Conversations are paginated
- Messages load on-demand
- Database queries are optimized with select_related/prefetch_related
- Frontend uses React state management for efficient rendering

## Support

For issues or questions:
1. Check Django logs: `backend/logs/`
2. Check browser console for frontend errors
3. Review API responses in Network tab
4. Contact development team

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Author**: HRMS Development Team
