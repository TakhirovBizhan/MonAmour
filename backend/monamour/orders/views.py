# orders/views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Count

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.select_related('user', 'painting')
    serializer_class = CartSerializer
    # Фильтрация корзины по пользователю (UUID)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']
    
    def get_queryset(self):
        # select_related для ускорения
        qs = Cart.objects.select_related('user', 'painting')
        # Аннотация: общее число добавлений данной painting в корзину
        # Если FK у Cart: painting = ForeignKey(Painting), без related_name,
        # то default related_name на стороне Painting — 'cart_set'.
        # Мы хотим посчитать для каждой записи Cart: сколько записей Cart с тем же painting.
        qs = qs.annotate(
            painting_add_count=Count('painting__cart')
        )
        return qs

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']  # фильтрация по id пользователя

    def get_queryset(self):
        user = self.request.user
        if self.request.user.is_staff:
            return Order.objects.all().select_related('user')
        # обычный пользователь видит только свои заказы
        return Order.objects.filter(user=user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('order', 'painting')
    serializer_class = OrderItemSerializer
