from django.contrib import admin
from .models import ChatConversation, ChatMessage, ChatbotKnowledge


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'title']
    date_hierarchy = 'created_at'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_preview', 'created_at', 'is_read']
    list_filter = ['sender', 'is_read', 'created_at']
    search_fields = ['message', 'conversation__user__email']
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'question_preview', 'priority', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    list_editable = ['priority', 'is_active']
    
    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_preview.short_description = 'Question'
