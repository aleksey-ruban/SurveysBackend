import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .serializers import RegisterSerializer, LoginSerializer, RequestPasswordResetSerializer, UserSerializer
from accounts.models import User, PasswordResetCode


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.get(user=user)
            if check_password(password, reset_code.code):
                user.set_password(password)
                user.save()
                reset_code.delete()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
        except (PasswordResetCode.DoesNotExist):
            pass
        except (User.DoesNotExist):
            return Response({'error': 'Пользователя не существует'}, status=status.HTTP_400_BAD_REQUEST)    

        return Response({'error': 'Неверные данные для входа'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Аккаунт успешно удалён"}, status=status.HTTP_204_NO_CONTENT)


class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])

        raw_password = secrets.token_urlsafe(10)

        PasswordResetCode.objects.update_or_create(
            user=user,
            defaults={'code': make_password(raw_password)}
        )

        send_mail(
            subject='Временный пароль для входа',
            message=f'''Ваш новый пароль: {raw_password}\n
Он действует первые 15 минут после создания.\n
Если вы не запрашивали смену пароля, проигнорируйте это письмо.
            ''',
            from_email='no-reply@example.com',
            recipient_list=[user.email],
        )

        return Response({'message': 'Временный пароль отправлен на почту'})
