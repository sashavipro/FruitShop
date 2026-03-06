"""src/chat/models.py."""

from django.contrib.auth.models import User
from django.db import models


class ChatMessage(models.Model):
    """Model representing a single message in the chat.

    Can belong to an authenticated user or be a system-generated message
    (e.g., from the 'Joker' bot) if author_user is null.
    """

    # Если user_id пустой (null), значит это системное
    # сообщение (например, от бота "Шутник")
    author_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    author_name = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for the ChatMessage model."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return a string representation of the chat message."""
        return f"{self.author_name}: {self.text[:30]}"
