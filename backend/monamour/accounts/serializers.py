# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        # Поля AbstractUser + ваши расширения: username, email, first_name, last_name, phone, role
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone': {'required': False},
            'role': {'required': False},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError({'password2': _("Пароли не совпадают.")})
        # Опционально: проверка сложности пароля
        # from django.contrib.auth.password_validation import validate_password
        # validate_password(password)
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        # Если вы не хотите позволять регистрировать роль отличную от buyer:
        # validated_data['role'] = 'buyer'
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Укажите поля, которые хотите возвращать профилем
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'role']  # роль можно менять отдельно, если нужно

# Расширенный serializer для токена: возвращает токен + данные пользователя
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # При необходимости добавьте кастомные claims, например:
        # token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Добавим данные о пользователе в ответ
        data.update({
            'user': UserSerializer(self.user, context=self.context).data
        })
        return data