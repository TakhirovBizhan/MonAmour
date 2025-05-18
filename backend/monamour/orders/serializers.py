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

    class Meta:
        model = Cart
        fields = ['id', 'user', 'painting', 'painting_id', 'added_at']

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

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'total_amount', 'status', 'delivery_address', 'paintings', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            painting = item_data['painting']
            price = painting.price
            total += price
            OrderItem.objects.create(order=order, painting=painting, price_at_purchase=price)
        order.total_amount = total
        order.save()
        return order

    def update(self, instance, validated_data):
        # обновление полей заказа без изменения items
        return super().update(instance, validated_data)
