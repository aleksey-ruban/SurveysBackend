from django.urls import path
from .views import ImageUploadView, SurveyCreateView, SurveyResultsView, ToggleSurveyStatusView, SurveyDeleteView

urlpatterns = [
    path('upload', ImageUploadView.as_view(), name='upload'),
    path('create-survey', SurveyCreateView.as_view(), name='create'),
    path('survey-result/<int:pk>', SurveyResultsView.as_view(), name='result'),
    path('toggle-survey/<int:pk>', ToggleSurveyStatusView.as_view(), name='toggle-survey'),
    path('delete-survey/<int:pk>', SurveyDeleteView.as_view(), name='delete-survey'),
]