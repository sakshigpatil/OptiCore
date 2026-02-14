from django.db import models
from django.conf import settings


class ChatConversation(models.Model):
    """Model to store chat conversations"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_conversations'
    )
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class ChatMessage(models.Model):
    """Model to store individual chat messages"""
    
    SENDER_CHOICES = [
        ('USER', 'User'),
        ('BOT', 'Bot'),
        ('SYSTEM', 'System')
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # For storing additional data like suggestions, quick replies
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        return f"{self.sender} - {self.message[:50]}"


class ChatbotKnowledge(models.Model):
    """Model to store chatbot knowledge base"""
    
    CATEGORY_CHOICES = [
        ('GENERAL', 'General HR Queries'),
        ('LEAVE', 'Leave Management'),
        ('ATTENDANCE', 'Attendance'),
        ('PAYROLL', 'Payroll'),
        ('EMPLOYEE', 'Employee Management'),
        ('POLICY', 'Company Policies'),
        ('BENEFITS', 'Benefits'),
        ('RECRUITMENT', 'Recruitment'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField()
    answer = models.TextField()
    keywords = models.JSONField(default=list)  # Keywords for better matching
    priority = models.IntegerField(default=0)  # Higher priority questions appear first
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'Chatbot Knowledge'
        verbose_name_plural = 'Chatbot Knowledge Base'

    def __str__(self):
        return f"{self.category} - {self.question[:50]}"
