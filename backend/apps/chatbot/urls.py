from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatConversationViewSet, ChatMessageViewSet, ChatbotKnowledgeViewSet

router = DefaultRouter()
router.register(r'conversations', ChatConversationViewSet, basename='conversation')
router.register(r'messages', ChatMessageViewSet, basename='message')
router.register(r'knowledge', ChatbotKnowledgeViewSet, basename='knowledge')

urlpatterns = [
    path('', include(router.urls)),
]
