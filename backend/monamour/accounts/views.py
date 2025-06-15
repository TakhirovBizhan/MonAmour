# accounts/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except serializers.ValidationError as ve:
            # DRF уже вернёт 400 с JSON ошибок
            raise
        except Exception as e:
            # Любая другая ошибка — возвращаем JSON с сообщением
            return Response(
                {"detail": f"Unexpected error during registration: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # Если всё ок:
        user_data = UserSerializer(user, context={'request': request}).data
        return Response(user_data, status=status.HTTP_201_CREATED)
class UserMeView(generics.RetrieveAPIView):
    """
    GET /auth/me/ — возвращает данные текущего аутентифицированного пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class MyTokenObtainPairView(TokenObtainPairView):
    """
    POST /auth/token/ — получает токены и возвращает вместе с данными пользователя.
    """
    serializer_class = MyTokenObtainPairSerializer

# Для обновления токена используется стандартный TokenRefreshView:
# POST /auth/token/refresh/ {"refresh": "..."}
# возвращает новый access token. Не нужно переопределять.