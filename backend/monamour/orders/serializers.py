# orders/serializers.py

from rest_framework import serializers
from .models import Cart, Order, OrderItem
from store.serializers import PaintingSerializer
from store.models import Painting
from django.contrib.auth import get_user_model

User = get_user_model()

class CartSerializer(serializers.ModelSerializer):
    painting = PaintingSerializer(read_only=True)
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=Painting.objects.all(),
        source='painting',
        write_only=True
    )
    # Убираем painting_add_count из полей, если не нужна в клиенте; 
    # если нужна, то её можно аннотировать в ViewSet и вернуть read_only поле:
    painting_add_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        # user оставляем read_only, т.к. привязываем по request.user
        fields = ['id', 'user', 'painting', 'painting_id', 'added_at', 'painting_add_count']
        read_only_fields = ['id', 'user', 'added_at', 'painting', 'painting_add_count']

    def create(self, validated_data):
        """
        При создании корзины-привязываем к request.user.
        """
        request = self.context.get('request')
        user = None
        if request and request.user and request.user.is_authenticated:
            user = request.user
        else:
            raise serializers.ValidationError("Необходима аутентификация для добавления в корзину.")
        # painting уже в validated_data['painting']
        cart_obj = Cart.objects.create(user=user, painting=validated_data['painting'])
        return cart_obj


class OrderItemSerializer(serializers.ModelSerializer):
    # Возвращаем вложенный объект Painting при чтении
    painting = PaintingSerializer(read_only=True)
    # Для записи при создании заказа:
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
    # Поля адреса:
    street = serializers.CharField()
    house_number = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    address_comment = serializers.CharField(allow_blank=True, required=False)
    # Способ оплаты:
    # Предполагается, что в модели Order поле payment_method определено с choices
    payment_method = serializers.ChoiceField(
        choices=Order._meta.get_field('payment_method').choices,
        default='card'
    )
    # Телефон:
    phone_number = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_date', 'status',
            'street', 'house_number', 'city', 'postal_code', 'address_comment',
            'payment_method', 'phone_number',
            'painting_ids', 'items'
        ]
        # user, order_date, status и items — read_only
        read_only_fields = ['id', 'user', 'order_date', 'status', 'items']

    def validate(self, attrs):
        errors = {}
        # Проверяем обязательные адресные поля
        for field in ['street', 'house_number', 'city', 'postal_code']:
            val = attrs.get(field)
            if val is None or not str(val).strip():
                errors[field] = 'Это поле обязательно.'
        # Проверяем painting_ids
        painting_ids = attrs.get('painting_ids')
        if painting_ids is None or not isinstance(painting_ids, list) or not painting_ids:
            errors['painting_ids'] = 'Список картин не может быть пуст.'
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Создаём заказ, привязывая к request.user, создаём OrderItem-ы.
        """
        request = self.context.get('request')
        if not (request and request.user and request.user.is_authenticated):
            raise serializers.ValidationError('Необходима аутентификация для создания заказа.')

        painting_ids = validated_data.pop('painting_ids', [])
        # Забираем пользователя из request.user
        user = request.user

        # Создаём Order
        try:
            order = Order.objects.create(user=user,
                                         street=validated_data.get('street'),
                                         house_number=validated_data.get('house_number'),
                                         city=validated_data.get('city'),
                                         postal_code=validated_data.get('postal_code'),
                                         address_comment=validated_data.get('address_comment', None),
                                         payment_method=validated_data.get('payment_method'),
                                         phone_number=validated_data.get('phone_number'),
                                         # status оставляем дефолтный, возможно 'processing'
                                         )
        except Exception as e:
            raise serializers.ValidationError({'non_field_errors': f"Ошибка создания заказа: {e}"})

        # Создаём OrderItem-ы
        paintings = Painting.objects.filter(id__in=painting_ids)
        if paintings.count() != len(painting_ids):
            # Удаляем заказ, чтобы не оставить мусор
            order.delete()
            raise serializers.ValidationError({'painting_ids': 'Некоторые переданные ID картин некорректны.'})
        try:
            for painting in paintings:
                OrderItem.objects.create(
                    order=order,
                    painting=painting,
                    price_at_purchase=painting.price
                )
        except Exception as e:
            order.delete()
            raise serializers.ValidationError({'non_field_errors': f"Ошибка при добавлении картин в заказ: {e}"})

        return order

    def update(self, instance, validated_data):
        """
        При обновлении заказа запрещаем менять user и items через этот эндпоинт.
        Остальные поля (адрес, статус при admin и т.д.) можно менять по логике.
        """
        # Удаляем потенциальные попытки изменить user или painting_ids
        validated_data.pop('painting_ids', None)
        # user и items уже read_only
        return super().update(instance, validated_data)