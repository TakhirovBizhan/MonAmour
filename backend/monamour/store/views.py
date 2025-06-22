from __future__ import annotations
from typing import Any, Dict, List, Optional, Type
from django.db.models import Count, Avg, Q, Prefetch, QuerySet
from django.utils import timezone
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.pagination import LimitOffsetPagination

from django.contrib.auth import get_user_model

from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage, ArtistReview
from orders.models import Cart
from .serializers import (
    ArtistSerializer,
    GallerySerializer,
    CategorySerializer,
    PaintingImageSerializer,
    PaintingSerializer,
    BannerSerializer,
    UserSerializer,
    PaintingImageUploadSerializer,
    ArtistReviewSerializer
)

UUIDFilter = filters.UUIDFilter
User = get_user_model()


class PaintingFilter(FilterSet):
    """
    Фильтрация для списка картин по статусу, заголовку, диапазону цен,
    категории, галерее и дате добавления.
    """
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.UUIDFilter(field_name='category', lookup_expr='exact')
    gallery = filters.UUIDFilter(field_name='gallery', lookup_expr='exact')
    added_before = filters.DateTimeFilter(field_name='added_at', lookup_expr='lte')
    added_after = filters.DateTimeFilter(field_name='added_at', lookup_expr='gte')

    class Meta:
        model = Painting
        fields = [
            'status', 'title', 'category', 'gallery',
            'min_price', 'max_price', 'added_before', 'added_after'
        ]


class ArtistFilter(FilterSet):
    """
    Фильтрация для списка артистов по имени.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Artist
        fields = ['name']


class PaintingPagination(LimitOffsetPagination):
    """
    Пагинация для списка картин с возможностью указания limit и offset.
    """
    max_limit = 100
    offset_query_param = 'offset'
    limit_query_param = 'limit'


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактировать/удалять отзыв только его владельцу или staff.
    """
    def has_object_permission(self, request: Request, view: Any, obj: ArtistReview) -> bool:
        # SAFE_METHODS разрешены всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Только владелец отзыва или staff может изменять/удалять
        return obj.user == request.user or request.user.is_staff


class ArtistViewSet(viewsets.ModelViewSet):
    """
    CRUD для артистов.
    - Список/retrieve: доступно всем.
    - create/update/delete: только админ.
    Дополнительно:
    - Аннотация среднего рейтинга и числа отзывов в queryset.
    - Action 'reviews' для получения отзывов конкретного артиста с select_related.
    """
    queryset: QuerySet[Artist] = Artist.objects.all().annotate(
        average_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )
    serializer_class = ArtistSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']
    filterset_class = ArtistFilter

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Возвращает список прав доступа в зависимости от action.
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self) -> QuerySet[Artist]:
        """
        Возвращает queryset артистов с аннотациями среднего рейтинга и числа отзывов.
        """
        return Artist.objects.all().annotate(
            average_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        )

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request: Request, pk: Optional[str] = None) -> Response:
        """
        GET /api/artists/{id}/reviews/
        Возвращает отзывы для данного артиста, с пагинацией.
        Использует select_related для подтягивания связей user и artist.
        """
        artist: Artist = self.get_object()
        reviews_qs: QuerySet[ArtistReview] = (
            ArtistReview.objects
            .filter(artist=artist)
            .select_related('user', 'artist')
            .order_by('-created_at')
        )
        page = self.paginate_queryset(reviews_qs)
        if page is not None:
            serializer = ArtistReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ArtistReviewSerializer(reviews_qs, many=True, context={'request': request})
        return Response(serializer.data)


class GalleryViewSet(viewsets.ModelViewSet):
    """
    CRUD для галерей.
    - create/update/delete: только админ.
    - list/retrieve: всем.
    Action:
    - id_name_list: возвращает пары {id, name}.
    """
    queryset: QuerySet[Gallery] = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'], url_path='id-name')
    def id_name_list(self, request: Request) -> Response:
        """
        GET /api/galleries/id-name/
        Возвращает список галерей в виде словарей {id, name}.
        """
        data = Gallery.objects.values('id', 'name')
        return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий.
    - create/update/delete: только админ.
    - list/retrieve: всем.
    В queryset аннотируется num_paintings и avg_price.
    """
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self) -> QuerySet[Category]:
        """
        Возвращает категории с аннотациями:
        - num_paintings: число картин в категории
        - avg_price: средняя цена картин в категории
        """
        from django.db.models import Count, Avg as DjangoAvg
        return Category.objects.annotate(
            num_paintings=Count('painting'),
            avg_price=DjangoAvg('painting__price')
        )


class PaintingViewSet(viewsets.ModelViewSet):
    """
    CRUD для картин.
    - list/retrieve: всем
    - create/update/delete: только админ
    Поддерживает фильтрацию через PaintingFilter и пагинацию PaintingPagination.
    В get_queryset:
    - select_related для родственных моделей gallery, artist
    - prefetch_related для изображений
    - аннотация active_promotions_count и times_added_to_cart
    """
    serializer_class = PaintingSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaintingFilter
    pagination_class = PaintingPagination

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self) -> QuerySet[Painting]:
        """
        Возвращает queryset доступных картин:
        - Только статус 'available' (in_stock())
        - select_related: gallery и artist
        - prefetch_related: images
        - Аннотация active_promotions_count: число активных акций
        - Аннотация times_added_to_cart: сколько раз добавлено в корзины
        - Сортировка по query_params: price или added_at
        """
        qs: QuerySet[Painting] = (
            Painting.objects
            .in_stock()
            .select_related('gallery', 'artist')
            .prefetch_related('images')
        )
        params: Dict[str, Any] = self.request.query_params  # type: ignore
        if params.get('min_price'):
            qs = qs.filter(price__gt=params['min_price'])
        sort = params.get('sort')
        if sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        else:
            qs = qs.order_by('-added_at')

        now = timezone.now()
        qs = qs.annotate(
            active_promotions_count=Count(
                'promotions',
                filter=Q(promotions__start__lte=now, promotions__end__gte=now)
            )
        )
        # times_added_to_cart: предполагается related_name='cart' или аналог на Cart.painting
        qs = qs.annotate(times_added_to_cart=Count('cart'))
        return qs

    def get_serializer_context(self) -> Dict[str, Any]:
        """
        Добавляет context['fields'] для sparse fieldsets.
        Если в query_params передан fields=field1,field2,...,
        сериализатор оставит только эти поля + id + write-only поля.
        """
        context: Dict[str, Any] = super().get_serializer_context()
        request = self.request
        fields_param: Optional[str] = request.query_params.get('fields')
        if fields_param:
            context['fields'] = [f.strip() for f in fields_param.split(',') if f.strip()]
        else:
            context['fields'] = None
        return context


class BannerViewSet(viewsets.ModelViewSet):
    """
    CRUD для баннеров.
    - create/update/delete: только админ.
    - list/retrieve: всем.
    """
    queryset: QuerySet[Banner] = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['headline']

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ, если пользователь — владелец объекта (User) или is_staff.
    """
    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        # obj здесь экземпляр User
        return bool(request.user and (request.user.is_staff or obj == request.user))


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CustomUser.
    - list: только админ может получить список.
    - retrieve/update/destroy: владелец или админ.
    - create: только админ (регистрация обычно через отдельный endpoint).
    """
    queryset: QuerySet[User] = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['username', 'email']

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action == 'create':
            return [permissions.IsAdminUser()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self) -> QuerySet[User]:
        """
        Если admin: возвращает всех пользователей.
        Иначе возвращает только свой объект.
        """
        user = self.request.user
        if user and user.is_staff:
            return User.objects.all()
        if user and user.is_authenticated:
            return User.objects.filter(pk=user.pk)
        return User.objects.none()

    def perform_create(self, serializer: serializers.ModelSerializer) -> None:
        """
        Сохраняет нового пользователя (используется админом).
        """
        serializer.save()


class PaintingImageViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet для PaintingImage:
    - POST: загрузка через Base64 (только аутентифицированные).
    - GET list/retrieve: просмотр (всем).
    """
    queryset: QuerySet[PaintingImage] = PaintingImage.objects.all()

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self) -> Type[serializers.ModelSerializer]:
        """
        Возвращает соответствующий сериализатор:
        - PaintingImageUploadSerializer для создания
        - PaintingImageSerializer для просмотра
        """
        if self.action == 'create':
            return PaintingImageUploadSerializer
        return PaintingImageSerializer


class ArtistReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD для отзывов об авторах.
    - list/retrieve: всем.
    - create: только аутентифицированные.
    - update/delete: только владелец или staff.
    """
    serializer_class = ArtistReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['artist', 'user', 'rating']

    def get_queryset(self) -> QuerySet[ArtistReview]:
        """
        Возвращает все отзывы, используя select_related для artist и user.
        """
        return ArtistReview.objects.all().select_related('artist', 'user')

    def perform_create(self, serializer: ArtistReviewSerializer) -> None:
        """
        При создании отзыва:
        - Если обычный пользователь: привязывает к request.user.
        - Если админ: может указать user через payload или оставить как есть.
        """
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def get_permissions(self) -> List[permissions.BasePermission]:
        """
        Разрешения:
        - create: аутентифицированные
        - update/delete: IsAuthenticated + IsReviewOwnerOrReadOnly
        - list/retrieve: AllowAny
        """
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsReviewOwnerOrReadOnly()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]