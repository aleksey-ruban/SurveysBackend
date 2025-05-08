from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    class Roles(models.TextChoices):
        CREATOR = 'creator', 'Creator'
        RESPONDENT = 'respondent', 'Respondent'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=Roles.choices)
    last_uploaded_image = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role', 'name']

    def __str__(self):
        return f"{self.name} ({self.email}, {self.role})"


class PasswordResetCode(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)