# orders/views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.select_related('user', 'painting')
    serializer_class = CartSerializer
    # Фильтрация корзины по пользователю (UUID)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').prefetch_related('items__painting')
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'painting')
    serializer_class = OrderItemSerializer
