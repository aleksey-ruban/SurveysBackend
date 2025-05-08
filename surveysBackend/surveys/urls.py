from django.urls import path
from .views import SurveyListView


urlpatterns = [
    path('surveys', SurveyListView.as_view(), name='register'),
]