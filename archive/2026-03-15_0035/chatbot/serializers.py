from rest_framework import serializers
from .models import ChatConversation, ChatMessage, ChatbotKnowledge


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'conversation', 'sender', 'message', 'metadata', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']


class ChatConversationSerializer(serializers.ModelSerializer):
    """Serializer for chat conversations"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatConversation
        fields = ['id', 'user', 'title', 'created_at', 'updated_at', 'is_active', 
                  'messages', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'sender': last_msg.sender,
                'message': last_msg.message,
                'created_at': last_msg.created_at
            }
        return None


class ChatConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing conversations"""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatConversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 
                  'message_count', 'last_message', 'unread_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'sender': last_msg.sender,
                'message': last_msg.message[:100],
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        return obj.messages.filter(is_read=False, sender='BOT').count()


class ChatbotKnowledgeSerializer(serializers.ModelSerializer):
    """Serializer for chatbot knowledge base"""
    
    class Meta:
        model = ChatbotKnowledge
        fields = ['id', 'category', 'question', 'answer', 'keywords', 'priority', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
