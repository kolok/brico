from core.models.mixin import TimestampedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Conversation(TimestampedModel, models.Model):
    """Représente une conversation avec Claude."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        default="Nouvelle conversation",
        help_text="Titre de la conversation",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Message(TimestampedModel, models.Model):
    """Représente un message dans une conversation."""

    ROLE_CHOICES = [
        ("user", "Utilisateur"),
        ("assistant", "Assistant"),
    ]

    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
