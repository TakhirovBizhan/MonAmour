from rest_framework import serializers
from .models import Cart, Order, OrderItem
from store.serializers import PaintingSerializer
from store.models import Painting
from django.contrib.auth import get_user_model
from typing import Any, Dict

User = get_user_model()


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор Cart:
    - При чтении: возвращает вложенную информацию о картине.
    - При создании: принимает painting_id, привязывает к request.user.
    """
    painting = PaintingSerializer(read_only=True)
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=Painting.objects.all(),
        source='painting',
        write_only=True
    )
    painting_add_count = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'painting', 'painting_id', 'added_at', 'painting_add_count']
        read_only_fields = ['id', 'user', 'added_at', 'painting', 'painting_add_count']

    def create(self, validated_data: Dict[str, Any]) -> Cart:
        """
        Создаёт Cart, привязывая к request.user.
        Args:
            validated_data: {'painting': Painting}
        Returns:
            Cart: новый объект корзины.
        Raises:
            serializers.ValidationError: если пользователь не аутентифицирован.
        """
        request = self.context.get('request')
        if not (request and hasattr(request, 'user') and request.user and request.user.is_authenticated):
            raise serializers.ValidationError("Необходима аутентификация для добавления в корзину.")
        painting_obj = validated_data.get('painting')
        # Если нужно запретить дублирование, можно проверить здесь.
        cart_obj = Cart.objects.create(user=request.user, painting=painting_obj)
        return cart_obj


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор OrderItem:
    - Чтение: вложенный PaintingSerializer.
    - Создание через OrderSerializer: painting_id.
    """
    painting = PaintingSerializer(read_only=True)
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
    """
    Сериализатор Order:
    - Чтение: отдаёт поля заказа и вложенные items.
    - Создание: принимает painting_ids, адрес, payment_method, phone_number.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    painting_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text='Список ID картин для заказа'
    )
    street = serializers.CharField()
    house_number = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    address_comment = serializers.CharField(allow_blank=True, required=False)
    payment_method = serializers.ChoiceField(
        choices=Order._meta.get_field('payment_method').choices,
        default='card'
    )
    phone_number = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_date', 'status',
            'street', 'house_number', 'city', 'postal_code', 'address_comment',
            'payment_method', 'phone_number',
            'painting_ids', 'items'
        ]
        read_only_fields = ['id', 'user', 'order_date', 'status', 'items']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Общая валидация адресных полей и painting_ids.
        Args:
            attrs: входящие данные.
        Returns:
            attrs, если всё ок.
        Raises:
            serializers.ValidationError: если обязательные поля пусты или painting_ids некорректен.
        """
        errors: Dict[str, str] = {}
        # Проверяем обязательные адресные поля
        for field in ['street', 'house_number', 'city', 'postal_code']:
            val = attrs.get(field)
            if val is None or not str(val).strip():
                errors[field] = 'Это поле обязательно.'
        painting_ids = attrs.get('painting_ids')
        if painting_ids is None or not isinstance(painting_ids, list) or not painting_ids:
            errors['painting_ids'] = 'Список картин не может быть пуст.'
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data: Dict[str, Any]) -> Order:
        """
        Создаёт Order и связанные OrderItem.
        Args:
            validated_data: включает painting_ids и адресные поля.
        Returns:
            Order: созданный заказ.
        Raises:
            serializers.ValidationError: если не аутентифицирован пользователь или некорректны painting_ids.
        """
        request = self.context.get('request')
        if not (request and hasattr(request, 'user') and request.user and request.user.is_authenticated):
            raise serializers.ValidationError('Необходима аутентификация для создания заказа.')

        painting_ids = validated_data.pop('painting_ids', [])
        user = request.user

        # Создаём Order
        try:
            order = Order.objects.create(
                user=user,
                street=validated_data.get('street', ''),
                house_number=validated_data.get('house_number', ''),
                city=validated_data.get('city', ''),
                postal_code=validated_data.get('postal_code', ''),
                address_comment=validated_data.get('address_comment', None),
                payment_method=validated_data.get('payment_method'),
                phone_number=validated_data.get('phone_number', ''),
            )
        except Exception as e:
            raise serializers.ValidationError({'non_field_errors': f"Ошибка создания заказа: {e}"})

        # Проверяем корректность ID картин
        paintings_qs = Painting.objects.filter(id__in=painting_ids)
        if paintings_qs.count() != len(painting_ids):
            order.delete()
            raise serializers.ValidationError({'painting_ids': 'Некоторые переданные ID картин некорректны.'})

        # Создаём OrderItem-ы
        try:
            for painting in paintings_qs:
                OrderItem.objects.create(
                    order=order,
                    painting=painting,
                    price_at_purchase=painting.price
                )
        except Exception as e:
            order.delete()
            raise serializers.ValidationError({'non_field_errors': f"Ошибка при добавлении картин в заказ: {e}"})

        return order

    def update(self, instance: Order, validated_data: Dict[str, Any]) -> Order:
        """
        Обновление Order: запрещаем менять painting_ids (уже удалено из incoming), user и items.
        Остальные поля (адрес, статус) обновляются дефолтно.
        """
        validated_data.pop('painting_ids', None)
        return super().update(instance, validated_data)