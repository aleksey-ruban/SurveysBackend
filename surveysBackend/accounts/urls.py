from django.urls import path
from .views import DeleteAccountView, RegisterView, LoginView, LogoutView, ProfileView, RequestPasswordResetView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me', ProfileView.as_view(), name='profile'),
    path('delete-account', DeleteAccountView.as_view(), name='delete-account'),
    path('request-password-reset', RequestPasswordResetView.as_view()),
]