# REST API enpoints for chat, history, and clearing conversations

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .ai_service import AIService
from .models import ChatMessage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    """Endpoint for chatting with the AI HR assistant"""
    message = request.data.get('message', '').strip()

    if not message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ai_service = AIService()
        response_text = ai_service.process_query(message, request.user)

        # Save the conversation
        ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=response_text,
            is_ai_response=True
        )

        return Response({
            'message': message,
            'response': response_text,
            'timestamp': ChatMessage.objects.filter(user=request.user).first().timestamp
        })

    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {'error': f'AI service error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """Get chat history for the authenticated user"""
    messages = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:50]
    data = [{
        'id': msg.id,
        'message': msg.message,
        'response': msg.response,
        'timestamp': msg.timestamp
    } for msg in messages]

    return Response(data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_chat_history(request):
    """Clear chat history for the authenticated user"""
    ChatMessage.objects.filter(user=request.user).delete()
    return Response({'message': 'Chat history cleared'})
