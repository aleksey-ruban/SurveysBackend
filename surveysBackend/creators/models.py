from django.db import models
from django.conf import settings
from accounts.models import User
from django.core.validators import MinValueValidator


class Survey(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='surveys',
        limit_choices_to={'role': User.Roles.CREATOR}
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=True)
    user_contact = models.CharField(max_length=255, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        TEXT = "text", "Text"
        SINGLE_CHOICE = "single_choice", "Single Choice"
        MULTIPLE_CHOICE = "multiple_choice", "Multiple Choice"
        RATING = "rating", "Rating"

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    position = models.IntegerField(validators=[MinValueValidator(0)])
    type = models.CharField(max_length=20, choices=QuestionType.choices)
    question_text = models.TextField()
    required = models.BooleanField(default=True)

    scale = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"[{self.type}] {self.question_text}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
