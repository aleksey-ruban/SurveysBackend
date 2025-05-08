from django.db import models
from django.conf import settings


class SurveyResponse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_responses',
    )
    survey = models.ForeignKey(
        'creators.Survey',
        on_delete=models.CASCADE,
        related_name='responses'
    )
    user_contact = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'survey')

    def __str__(self):
        return f"Response by {self.user or 'Anonymous'} to '{self.survey.title}'"


class QuestionResponse(models.Model):
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='question_responses'
    )
    question = models.ForeignKey(
        'creators.Question',
        on_delete=models.CASCADE
    )
    answer_text = models.TextField(blank=True, null=True)
    scale = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Answer to '{self.question}'"


class OptionResponse(models.Model):
    question = models.ForeignKey(
        QuestionResponse,
        on_delete=models.CASCADE,
        related_name="options_responses"
    )
    option = models.ForeignKey(
        'creators.Option',
        on_delete=models.CASCADE
    )
