# orders/serializers.py
from rest_framework import serializers
from .models import Cart, Order, OrderItem
from store.serializers import PaintingSerializer

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

class OrderItemSerializer(serializers.ModelSerializer):
    painting = PaintingSerializer(read_only=True)
    painting_id = serializers.PrimaryKeyRelatedField(
        queryset=PaintingSerializer.Meta.model.objects.all(),
        source='painting', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'painting', 'painting_id', 'price_at_purchase', 'purchased_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    phone_number = serializers.CharField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_date', 'status',
            'street', 'house_number', 'city', 'postal_code', 'address_comment',
            'payment_method', 'phone_number',
            'items'
        ]
        read_only_fields = ['id', 'order_date', 'user']

    def validate(self, attrs):
        # проверяем, что обязательные адресные поля заполнены
        required_address_fields = ['street', 'house_number', 'city', 'postal_code']
        for field in required_address_fields:
            if not attrs.get(field) or not attrs.get(field).strip():
                raise serializers.ValidationError({field: 'Это поле обязательно.'})
        # payment_method проверяется через choices
        return super().validate(attrs)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # user из context
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError('Необходима аутентификация')
        order = Order.objects.create(**validated_data)
        # Создать OrderItem: price_at_purchase берем из painting.price
        for item in items_data:
            painting = item['painting']
            OrderItem.objects.create(
                order=order,
                painting=painting,
                price_at_purchase=painting.price
            )
        return order

    def update(self, instance, validated_data):
        # Обновление: не трогаем user и items через этот эндпоинт
        validated_data.pop('user', None)
        items_data = validated_data.pop('items', None)
        order = super().update(instance, validated_data)
        # Если нужно обновить items: можно реализовать логику, но обычно не меняем
        return order