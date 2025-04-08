from django.contrib.auth.models import AbstractUser
from django.db import models

class AuthUser(AbstractUser):
    USER_TYPES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')

    def __str__(self):
        return self.username
