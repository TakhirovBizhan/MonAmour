# orders/serializers.py
from rest_framework import serializers
from .models import Cart, Order, OrderItem
from store.serializers import PaintingSerializer
from store.models import Painting
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

class CartSerializer(serializers.ModelSerializer):
    painting = PaintingSerializer(read_only=True)
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=PaintingSerializer.Meta.model.objects.all(),
        source='painting', write_only=True
    )
    painting_add_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'painting', 'painting_id', 'added_at', 'painting_add_count']

User = get_user_model()

class OrderItemSerializer(serializers.ModelSerializer):
    painting = serializers.PrimaryKeyRelatedField(read_only=True)
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=Painting.objects.all(),
        source='painting',
        write_only=True
    )
    price_at_purchase = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    purchased_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'painting', 'painting_id', 'price_at_purchase', 'purchased_at']
        read_only_fields = ['id', 'painting', 'price_at_purchase', 'purchased_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    painting_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text='Список ID картин для заказа'
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    # Поля адреса:
    street = serializers.CharField()
    house_number = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    address_comment = serializers.CharField(allow_blank=True, required=False)
    # Способ оплаты: автоматом берётся из модели, но явно можно:
    payment_method = serializers.ChoiceField(choices=Order._meta.get_field('payment_method').choices, default='card')
    # Телефон:
    phone_validator = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message='Номер телефона должен содержать только цифры и может начинаться с +, длина 7-15 символов.'
    )
    phone_number = serializers.CharField(validators=[phone_validator])

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_id', 'order_date', 'status',
            'street', 'house_number', 'city', 'postal_code', 'address_comment',
            'payment_method', 'phone_number',
            'painting_ids', 'items'
        ]
        read_only_fields = ['id', 'order_date', 'user', 'items']

    def validate(self, attrs):
        errors = {}
        # Обязательные адресные поля
        for field in ['street', 'house_number', 'city', 'postal_code']:
            val = attrs.get(field)
            if val is None or not str(val).strip():
                errors[field] = 'Это поле обязательно.'
        # painting_ids
        painting_ids = attrs.get('painting_ids')
        if painting_ids is None or not isinstance(painting_ids, list) or not painting_ids:
            errors['painting_ids'] = 'Список картин не может быть пуст.'
        # user уже проверяется через required=True в user_id
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data):
        import logging
        painting_ids = validated_data.pop('painting_ids', [])
        user = validated_data.get('user', None)
        if user is None:
            raise serializers.ValidationError({'user_id': 'Поле user_id обязательно.'})
        # Попытка создания Order
        try:
            order = Order.objects.create(**validated_data)
        except Exception as e:
            logging.exception("Ошибка при создании Order")
            raise serializers.ValidationError({'non_field_errors': f"Ошибка создания заказа: {e}"})
        # Создаём OrderItem-ы
        try:
            paintings = Painting.objects.filter(id__in=painting_ids)
            if paintings.count() != len(painting_ids):
                # удаляем созданный заказ, чтобы не оставить мусор
                order.delete()
                raise serializers.ValidationError({'painting_ids': 'Некоторые переданные ID картин некорректны.'})
            for painting in paintings:
                OrderItem.objects.create(order=order, painting=painting, price_at_purchase=painting.price)
        except serializers.ValidationError:
            # если мы сами бросили ValidationError, просто пробросим вверх
            raise
        except Exception as e:
            logging.exception("Ошибка при создании OrderItem")
            order.delete()
            raise serializers.ValidationError({'non_field_errors': f"Ошибка при добавлении картин в заказ: {e}"})
        return order

    def update(self, instance, validated_data):
        # не меняем user и items
        validated_data.pop('user', None)
        validated_data.pop('painting_ids', None)
        return super().update(instance, validated_data)