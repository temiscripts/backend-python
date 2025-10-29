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

