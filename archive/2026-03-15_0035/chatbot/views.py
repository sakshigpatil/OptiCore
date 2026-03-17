from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import ChatConversation, ChatMessage, ChatbotKnowledge
from .serializers import (
    ChatConversationSerializer,
    ChatConversationListSerializer,
    ChatMessageSerializer,
    ChatbotKnowledgeSerializer
)
from .utils import process_chat_message, get_hr_quick_actions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from utils.skill_analysis import analyze_employee_skill


class ChatConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat conversations"""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChatConversationListSerializer
        return ChatConversationSerializer
    
    def get_queryset(self):
        """Return conversations for the current user, HR users can see all"""
        user = self.request.user
        if user.is_hr:
            return ChatConversation.objects.all().prefetch_related('messages')
        return ChatConversation.objects.filter(user=user).prefetch_related('messages')
    
    def perform_create(self, serializer):
        """Automatically set the user when creating a conversation"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation and get bot response"""
        try:
            conversation = self.get_object()
            message_text = request.data.get('message', '').strip()
            
            if not message_text:
                return Response(
                    {'error': 'Message cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create user message
            user_message = ChatMessage.objects.create(
                conversation=conversation,
                sender='USER',
                message=message_text
            )
            
            # Process message and get bot response
            try:
                bot_response = process_chat_message(message_text, request.user)
            except Exception as e:
                # Fallback response if processing fails
                import traceback
                traceback.print_exc()
                bot_response = {
                    'message': f"I apologize, but I encountered an error processing your message. Please try again or ask something else.",
                    'metadata': {'type': 'error', 'error': str(e)}
                }
            
            # Create bot message
            bot_message = ChatMessage.objects.create(
                conversation=conversation,
                sender='BOT',
                message=bot_response['message'],
                metadata=bot_response.get('metadata', {})
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            
            # Update conversation title if it's the first message
            if conversation.messages.count() == 2:  # User message + Bot message
                conversation.title = message_text[:50] + ('...' if len(message_text) > 50 else '')
            
            conversation.save()
            
            return Response({
                'user_message': ChatMessageSerializer(user_message).data,
                'bot_message': ChatMessageSerializer(bot_message).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to send message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark all messages in a conversation as read"""
        conversation = self.get_object()
        conversation.messages.filter(is_read=False).update(is_read=True)
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['get'])
    def quick_actions(self, request):
        """Get HR-specific quick actions for the chatbot"""
        actions = get_hr_quick_actions(request.user)
        return Response(actions)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat messages"""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return messages for conversations owned by the current user"""
        user = self.request.user
        if user.is_hr:
            return ChatMessage.objects.all()
        return ChatMessage.objects.filter(conversation__user=user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread messages"""
        user = request.user
        if user.is_hr:
            count = ChatMessage.objects.filter(
                is_read=False,
                sender='USER'
            ).count()
        else:
            count = ChatMessage.objects.filter(
                conversation__user=user,
                is_read=False,
                sender='BOT'
            ).count()
        
        return Response({'unread_count': count})


class ChatbotKnowledgeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chatbot knowledge base (HR Admin only)"""
    
    serializer_class = ChatbotKnowledgeSerializer
    permission_classes = [IsAuthenticated]
    queryset = ChatbotKnowledge.objects.filter(is_active=True)
    
    def get_queryset(self):
        """HR can see all, others can only see active knowledge"""
        if self.request.user.is_hr:
            return ChatbotKnowledge.objects.all()
        return ChatbotKnowledge.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search knowledge base"""
        query = request.query_params.get('q', '').strip()
        category = request.query_params.get('category', '')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(question__icontains=query) |
                Q(answer__icontains=query) |
                Q(keywords__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category=category)
        
        serializer = self.get_serializer(queryset[:10], many=True)
        return Response(serializer.data)



class SkillAnalysisAPIView(APIView):
    """Analyze employee skills against role requirements.

    POST payload examples:
    - {"employee": {"name": "Rahul", "role": "Backend Developer", "skills": [..]}, "required_skills": ["Python", "Django"]}
    - {"employee": {...}, "role_requirements": {"Backend Developer": [...]} }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data or {}
        employee = data.get('employee')
        if not employee:
            return Response({'error': 'employee object is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Accept either a direct list of required skills or a mapping dict
        required_skills = data.get('required_skills')
        role_requirements = data.get('role_requirements')
        role_name = data.get('role_name') or employee.get('role')

        if required_skills is None and role_requirements is None:
            return Response(
                {'error': 'Either required_skills (list) or role_requirements (dict) must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reqs = role_requirements if role_requirements is not None else required_skills

        try:
            result = analyze_employee_skill(employee, reqs, role_name)
            return Response(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
