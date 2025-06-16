from rest_framework import serializers
from .models import Cart, Order, OrderItem
from store.serializers import PaintingSerializer
from store.models import Painting
from django.contrib.auth import get_user_model

User = get_user_model()

class CartSerializer(serializers.ModelSerializer):
    # При чтении вложенно отдаём информацию о картине
    painting = PaintingSerializer(read_only=True)
    # При записи указываем только painting_id; user привязывается из request.user
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=Painting.objects.all(),
        source='painting',
        write_only=True
    )
    # Если хотим вернуть в ответе, сколько раз эта же картина в разных корзинах,
    # аннотация задаётся во ViewSet (painting_add_count). Здесь читаем её:
    painting_add_count = serializers.IntegerField(read_only=True)
    # user показываем read-only (id текущего пользователя)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        # user — read_only, painting — read_only, painting_id — write_only, added_at — read_only
        fields = ['id', 'user', 'painting', 'painting_id', 'added_at', 'painting_add_count']
        read_only_fields = ['id', 'user', 'added_at', 'painting', 'painting_add_count']

    def create(self, validated_data):
        """
        При создании Cart объект привязываем к request.user.
        """
        request = self.context.get('request')
        if not (request and request.user and request.user.is_authenticated):
            raise serializers.ValidationError("Необходима аутентификация для добавления в корзину.")
        painting = validated_data.get('painting')
        # Проверка: можно, например, запретить дублирование — если необходимо, раскомментируйте:
        # if Cart.objects.filter(user=request.user, painting=painting).exists():
        #     raise serializers.ValidationError("Эта картина уже в вашей корзине.")
        cart_obj = Cart.objects.create(user=request.user, painting=painting)
        return cart_obj


class OrderItemSerializer(serializers.ModelSerializer):
    # Возвращаем вложенный объект Painting при чтении
    painting = PaintingSerializer(read_only=True)
    # Для создания через OrderSerializer: painting_id
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
    # Адресные поля
    street = serializers.CharField()
    house_number = serializers.CharField()
    city = serializers.CharField()
    postal_code = serializers.CharField()
    address_comment = serializers.CharField(allow_blank=True, required=False)
    # Способ оплаты: в модели Order должно быть поле payment_method с choices
    payment_method = serializers.ChoiceField(
        choices=Order._meta.get_field('payment_method').choices,
        default='card'
    )
    phone_number = serializers.CharField()

    # user и order_date, status, items — read_only
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_date', 'status',
            'street', 'house_number', 'city', 'postal_code', 'address_comment',
            'payment_method', 'phone_number',
            'painting_ids', 'items'
        ]
        read_only_fields = ['id', 'user', 'order_date', 'status', 'items']

    def validate(self, attrs):
        errors = {}
        # Проверяем обязательные адресные поля
        for field in ['street', 'house_number', 'city', 'postal_code']:
            val = attrs.get(field)
            if val is None or not str(val).strip():
                errors[field] = 'Это поле обязательно.'
        # painting_ids не должен быть пустым
        painting_ids = attrs.get('painting_ids')
        if painting_ids is None or not isinstance(painting_ids, list) or not painting_ids:
            errors['painting_ids'] = 'Список картин не может быть пуст.'
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)

    def create(self, validated_data):
        """
        Создаём заказ, привязывая к request.user, затем создаём OrderItem для каждой картины.
        """
        request = self.context.get('request')
        if not (request and request.user and request.user.is_authenticated):
            raise serializers.ValidationError('Необходима аутентификация для создания заказа.')

        painting_ids = validated_data.pop('painting_ids', [])
        user = request.user

        # Создаём Order
        try:
            order = Order.objects.create(
                user=user,
                street=validated_data.get('street'),
                house_number=validated_data.get('house_number'),
                city=validated_data.get('city'),
                postal_code=validated_data.get('postal_code'),
                address_comment=validated_data.get('address_comment', None),
                payment_method=validated_data.get('payment_method'),
                phone_number=validated_data.get('phone_number'),
                # status пусть дефолтно = 'processing' или как задано в модели
            )
        except Exception as e:
            raise serializers.ValidationError({'non_field_errors': f"Ошибка создания заказа: {e}"})

        # Проверяем корректность ID картин
        paintings = Painting.objects.filter(id__in=painting_ids)
        if paintings.count() != len(painting_ids):
            # Удаляем заказ, чтобы не оставлять «пустой» заказ
            order.delete()
            raise serializers.ValidationError({'painting_ids': 'Некоторые переданные ID картин некорректны.'})

        # Создаём OrderItem-ы
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
        При обновлении заказа через этот эндпоинт:
        - user менять нельзя (read_only_fields его исключили)
        - items нельзя менять здесь (через отдельные API или логику)
        Остальные поля (адрес, статус и т.п.) можно изменять согласно логике.
        """
        validated_data.pop('painting_ids', None)
        return super().update(instance, validated_data)