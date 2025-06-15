# orders/views.py

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Count

class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзины.
    Только авторизованные пользователи могут добавлять/удалять свои записи.
    Пользователь видит только свои записи в корзине.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']

    def get_queryset(self):
        # Возвращаем только записи корзины текущего пользователя
        user = self.request.user
        # Если есть админ, можно вернуть все или по-другому; здесь считаем, что админ тоже видит все
        if user.is_staff:
            # аннотируем painting_add_count: сколько раз каждая картина добавлена во все корзины
            return Cart.objects.select_related('user', 'painting') \
                .annotate(painting_add_count=Count('painting__cart')).all()
        # Обычный пользователь видит только свои записи
        return Cart.objects.filter(user=user).select_related('user', 'painting') \
            .annotate(painting_add_count=Count('painting__cart'))

    def perform_create(self, serializer):
        # create в сериализаторе уже привязывает к request.user
        serializer.save()

    def perform_update(self, serializer):
        # Если хотите запретить изменение записи корзины (например, менять painting), 
        # можно не реализовывать update, либо запретить. Здесь оставляем дефолт.
        serializer.save()

    # При удалении: permission_classes обеспечивает, что только владелец/авторизованный может удалять
    # Если нужна дополнительная проверка, можно override perform_destroy.


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов.
    - Только авторизованный пользователь может создавать заказ.
    - При GET пользователь видит только свои заказы; admin видит все.
    - При обновлении/удалении: можно разрешить только владельцу или админу.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['user']  # admin может фильтровать по пользователю

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # admin видит все
            return Order.objects.select_related('user').all()
        # обычный пользователь видит только свои
        return Order.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer):
        # сериализатор create сам привяжет user=request.user
        serializer.save()

    # Чтобы запретить update чужих заказов, достаточно permission_classes=[IsAuthenticated]
    # и get_queryset ограничивает видимые. Для дополнительной проверки в update/destroy:
    def perform_update(self, serializer):
        # Здесь можно добавить логику: например, позволить менять статус только admin.
        # Для простоты: разрешаем владельцу менять только адрес/телефон (из сериализатора).
        serializer.save()

    def perform_destroy(self, instance):
        # Можно запретить удаление заказов после создания, если нужно:
        # instance.delete()
        instance.delete()


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для элементов заказа.
    Как правило, создание/удаление OrderItem происходит внутри OrderSerializer.create.
    Поэтому отдельно создавать OrderItem через API часто не нужно или можно запретить обычным пользователям.
    Здесь ставим разрешения IsAuthenticatedOrReadOnly, но можно детализировать.
    """
    queryset = OrderItem.objects.select_related('order', 'painting')
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    # Можно фильтровать по order, если нужно:
    filterset_fields = ['order', 'painting']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderItem.objects.select_related('order', 'painting').all()
        # Обычный пользователь видит элементы только своих заказов
        return OrderItem.objects.select_related('order', 'painting')\
            .filter(order__user=user)

    def perform_create(self, serializer):
        # Обычно не создают OrderItem напрямую; но если нужно:
        order = serializer.validated_data.get('order')
        # Проверяем, что order принадлежит request.user или пользователь — админ
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