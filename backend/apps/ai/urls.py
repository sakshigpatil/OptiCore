from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('chat/', views.chat_with_ai, name='chat'),
    path('history/', views.get_chat_history, name='history'),
    path('clear/', views.clear_chat_history, name='clear'),
]