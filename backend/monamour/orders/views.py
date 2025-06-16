from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Count, Prefetch
from store.models import Painting

class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзины:
    - Только авторизованные пользователи могут добавлять/просматривать/удалять свои записи.
    - Админ может видеть/удалять любые записи.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = []  # убрано, т.к. get_queryset ограничивает видимость

    def get_queryset(self):
        user = self.request.user
        # Предварительно подготавливаем queryset для Painting, чтобы подтянуть artist, gallery, images
        painting_qs = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
        # Предполагается, что related_name у Cart.painting = 'cart'
        annotate_name = 'painting__cart'

        if user.is_staff:
            return Cart.objects.select_related('user', 'painting') \
                .prefetch_related(Prefetch('painting', queryset=painting_qs)) \
                .annotate(painting_add_count=Count(annotate_name))
        # Обычный пользователь — только свои записи
        return Cart.objects.filter(user=user).select_related('user', 'painting') \
            .prefetch_related(Prefetch('painting', queryset=painting_qs)) \
            .annotate(painting_add_count=Count(annotate_name))

    def perform_create(self, serializer):
        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов:
    - Только авторизованный пользователь может создавать заказ.
    - Обычный пользователь видит/меняет только свои заказы; админ видит/меняет все.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']  # фильтрация по user доступна админу

    def get_queryset(self):
        user = self.request.user
        # Подготовка prefetch для связанных OrderItem и вложенных Painting
        painting_qs = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
        orderitem_prefetch = Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('painting').prefetch_related(
                Prefetch('painting', queryset=painting_qs)
            )
        )
        if user.is_staff:
            return Order.objects.select_related('user').prefetch_related(orderitem_prefetch).all()
        return Order.objects.select_related('user').filter(user=user).prefetch_related(orderitem_prefetch)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для элементов заказа:
    - Обычные пользователи видят только элементы своих заказов; админ видит все.
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['order', 'painting']

    def get_queryset(self):
        user = self.request.user
        painting_qs = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
        if user.is_staff:
            return OrderItem.objects.select_related('order', 'painting').prefetch_related(
                Prefetch('painting', queryset=painting_qs)
            ).all()
        return OrderItem.objects.select_related('order', 'painting').prefetch_related(
            Prefetch('painting', queryset=painting_qs)
        ).filter(order__user=user)

    def perform_create(self, serializer):
        order = serializer.validated_data.get('order')
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя добавлять элементы в чужой заказ.")
        serializer.save()

    def perform_update(self, serializer):
        order = serializer.instance.order
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя изменять элементы чужого заказа.")
        serializer.save()

    def perform_destroy(self, instance):
        order = instance.order
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя удалять элементы чужого заказа.")
        instance.delete()