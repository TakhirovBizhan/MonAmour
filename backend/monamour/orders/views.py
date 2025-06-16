from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Count

class CartViewSet(viewsets.ModelViewSet):
    """
    CRUD для корзины:
    - Только авторизованные пользователи могут добавлять/просматривать/удалять свои записи.
    - Админ может видеть/удалять любые записи (по вашему решению).
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    # Удаляем фильтрацию по 'user' из query params, т.к. get_queryset ограничивает видимость.
    filterset_fields = []

    def get_queryset(self):
        user = self.request.user
        # Если админ, можно вернуть все записи корзины; иначе — только свои
        if user.is_staff:
            # Для каждой записи аннотируем, сколько раз эта же картина в любых корзинах:
            return Cart.objects.select_related('user', 'painting') \
                .annotate(painting_add_count=Count('painting__cart')).all()
        return Cart.objects.filter(user=user).select_related('user', 'painting') \
            .annotate(painting_add_count=Count('painting__cart'))

    def perform_create(self, serializer):
        # serializer.create привяжет к request.user внутри CartSerializer.create
        serializer.save()

    # Обновление записи корзины обычно не нужно (человек не меняет картину), но если нужно:
    # def perform_update(self, serializer):
    #     serializer.save()

    # Удаление: DRF возьмёт объект из get_queryset; обычный пользователь не сможет удалить чужой, т.к. он не в get_queryset.
    # Если нужно дополнительная проверка, можно override perform_destroy:
    # def perform_destroy(self, instance):
    #     if instance.user != self.request.user and not self.request.user.is_staff:
    #         raise permissions.PermissionDenied("Нельзя удалять чужую запись корзины.")
    #     instance.delete()


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD для заказов:
    - Только авторизованный пользователь может создавать заказ.
    - Обычный пользователь видит/меняет только свои заказы; админ видит/меняет все.
    - Статус заказа менять, возможно, только админом (но здесь для простоты разрешаем владельцу менять адрес и телефон).
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    # Разрешаем фильтрацию по user только для админа; у обычного get_queryset ограничит видимые.
    filterset_fields = ['user']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.select_related('user').all()
        return Order.objects.select_related('user').filter(user=user)

    def perform_create(self, serializer):
        # Привязка к request.user происходит внутри OrderSerializer.create
        serializer.save()

    def perform_update(self, serializer):
        # Здесь можно добавить логику: например, только админ может менять status:
        # order = serializer.instance
        # if 'status' in serializer.validated_data and not self.request.user.is_staff:
        #     raise permissions.PermissionDenied("Только админ может менять статус заказа.")
        serializer.save()

    # Если хотите запретить удаление заказов после создания:
    # def perform_destroy(self, instance):
    #     raise permissions.PermissionDenied("Нельзя удалять заказы.")
    # Иначе:
    # def perform_destroy(self, instance):
    #     instance.delete()


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    CRUD для элементов заказа:
    - Обычно создание/удаление OrderItem делается в OrderSerializer.create, 
      прямое создание OrderItem через API не требуется или ограничено.
    - Здесь: только авторизованные пользователи. 
    - Обычные пользователи видят только элементы своих заказов; админ видит все.
    """
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['order', 'painting']  # admin может фильтровать; обычный get_queryset ограничит

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return OrderItem.objects.select_related('order', 'painting').all()
        # Только элементы, относящиеся к заказам текущего пользователя
        return OrderItem.objects.select_related('order', 'painting').filter(order__user=user)

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