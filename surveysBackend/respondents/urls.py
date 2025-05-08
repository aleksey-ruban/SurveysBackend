from django.urls import path
from .views import SurveyDetailWithCompletionView, SubmitSurveyResponseView, SurveysForUser

urlpatterns = [
    path('survey/<int:pk>', SurveyDetailWithCompletionView.as_view(), name='survey-detail'),
    path('survey/submit-response', SubmitSurveyResponseView.as_view(), name='survey-submit-response'),
    path('surveys', SurveysForUser.as_view(), name='user-surveys'),
]