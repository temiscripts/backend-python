from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email  = models.EmailField(unique=True, null=False,blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField (default=timezone.now)
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest',null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return f"{self.email} ({self.role})"

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        participants = ", ".join(user.username for user in self.participants.all()[:3])
        return f"Conversation ({participants})"



class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_sent")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"From {self.sender.username}: {self.message_body[:30]}..."
