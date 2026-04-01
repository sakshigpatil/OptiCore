from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# model to store conversation history
class ChatMessage(models.Model):
    """Model to store chat messages for conversation history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_ai_response = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."
