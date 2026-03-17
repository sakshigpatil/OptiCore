"""
AI-powered utility functions for chatbot processing
"""
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import re


def process_chat_message(message, user):
    """
    Process user message and generate AI-powered bot response
    
    Args:
        message: User's message text
        user: User object
        
    Returns:
        dict: Bot response with message and metadata
    """
    from .ai_service import chatbot_ai
    
    # Use AI to process the message
    user_name = user.get_full_name() or user.username
    response = chatbot_ai.process_message(message, user_name)
    
    # Add quick suggestions based on response type
    if 'suggestions' not in response.get('metadata', {}):
        response['metadata'] = response.get('metadata', {})
        response['metadata']['suggestions'] = [
            "Show employee statistics",
            "Pending leave requests",
            "Today's attendance",
            "Department information"
        ]
    
    return response


def get_hr_quick_actions(user):
    """
    Get quick action buttons for the chatbot
    
    Args:
        user: User object
        
    Returns:
        list: Quick action buttons
    """
    return [
        {
            'id': 'employee_stats',
            'label': '📊 Show employee statistics',
            'message': 'Show employee statistics'
        },
        {
            'id': 'pending_leaves',
            'label': '📅 Pending leave requests',
            'message': 'Show pending leave requests'
        },
        {
            'id': 'attendance_today',
            'label': '⏰ Today\'s attendance',
            'message': 'What is today\'s attendance?'
        },
        {
            'id': 'department_info',
            'label': '🏢 Department information',
            'message': 'Show department information'
        }
    ]
