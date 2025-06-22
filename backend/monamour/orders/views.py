from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Count, Prefetch
from django.db.models.query import QuerySet
from store.models import Painting
from typing import Any


class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзины:
    - POST: добавить свою картину в корзину (user из request.user).
    - GET: обычный пользователь видит только свои записи, staff видит все.
    - DELETE: удаляет свою запись (staff может удалить любую).
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = []

    def get_queryset(self) -> QuerySet[Cart]:
        """
        Возвращает queryset для Cart:
        - Для staff: все записи, с select_related/prefetch связанных Painting.
        - Для обычного пользователя: только свои записи.
        Используется select_related('user','painting') и prefetch_related для подгрузки artist, gallery, images у Painting.
        """
        user = self.request.user
        # Подготавливаем Painting queryset с select_related/prefetch
        painting_qs = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
        annotate_name = 'painting__cart'
        base_qs = Cart.objects.select_related('user', 'painting').prefetch_related(
            Prefetch('painting', queryset=painting_qs)
        ).annotate(painting_add_count=Count(annotate_name))
        if user.is_staff:
            return base_qs
        return base_qs.filter(user=user)

    def perform_create(self, serializer: CartSerializer) -> None:
        """
        Создаёт Cart: user привязывается внутри CartSerializer.create.
        """
        serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов:
    - POST: создаёт заказ для request.user.
    - GET: обычный пользователь видит только свои заказы, staff видит все.
    - PUT/PATCH: обновление адреса/телефона (статус менять можно выбрать дополнительной логикой).
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']  # фильтрация по user доступна админу

    def get_queryset(self) -> QuerySet[Order]:
        """
        Возвращает queryset заказов:
        - Для staff: все заказы.
        - Иначе: только заказы текущего пользователя.
        Используется select_related('user') и prefetch_related для items -> painting -> artist/gallery/images.
        """
        user = self.request.user
        # Подготавливаем prefetch для OrderItem и вложенных Painting
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

    def perform_create(self, serializer: OrderSerializer) -> None:
        """
        Создаёт Order через OrderSerializer.create.
        """
        serializer.save()

    def perform_update(self, serializer: OrderSerializer) -> None:
        """
        Обновляет Order.
        """
        serializer.save()


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для элементов заказа:
    - Для staff: все элементы.
    - Обычный пользователь: элементы только своих заказов.
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['order', 'painting']

    def get_queryset(self) -> QuerySet[OrderItem]:
        """
        Возвращает queryset OrderItem:
        - Для staff: все записи, с подгрузкой painting->artist/gallery/images.
        - Иначе: только те, у которых order.user == request.user.
        """
        user = self.request.user
        painting_qs = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
        base_qs = OrderItem.objects.select_related('order', 'painting').prefetch_related(
            Prefetch('painting', queryset=painting_qs)
        )
        if user.is_staff:
            return base_qs.all()
        return base_qs.filter(order__user=user)

    def perform_create(self, serializer: OrderItemSerializer) -> None:
        """
        Создаёт OrderItem, проверяя, что заказ принадлежит request.user или user.is_staff.
        """
        order = serializer.validated_data.get('order')
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя добавлять элементы в чужой заказ.")
        serializer.save()

    def perform_update(self, serializer: OrderItemSerializer) -> None:
        """
        Обновляет OrderItem, проверяя права.
        """
        order = serializer.instance.order
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя изменять элементы чужого заказа.")
        serializer.save()

    def perform_destroy(self, instance: OrderItem) -> None:
        """
        Удаляет OrderItem, проверяя права.
        """
        order = instance.order
        if order.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Нельзя удалять элементы чужого заказа.")
        instance.delete()