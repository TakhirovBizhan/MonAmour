from django.db.models import Count, Avg, Q, Prefetch
from django.utils import timezone
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
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


# Фильтры

class PaintingFilter(FilterSet):
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
    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Artist
        fields = ['name']


# Pagination

class PaintingPagination(LimitOffsetPagination):
    max_limit = 100
    offset_query_param = 'offset'
    limit_query_param = 'limit'


# Permission for review owner or staff

class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактировать/удалять отзыв только его владельцу или staff.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS разрешены всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Только владелец отзыва или staff может изменять/удалять
        return obj.user == request.user or request.user.is_staff


# ViewSets

class ArtistViewSet(viewsets.ModelViewSet):
    """
    CRUD для артистов. Дополнительно аннотация среднего рейтинга и числа отзывов,
    а также action для получения отзывов конкретного автора.
    """
    queryset = Artist.objects.all().annotate(
        average_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    )
    serializer_class = ArtistSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']
    filterset_class = ArtistFilter

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]  # Только админы могут создавать, обновлять, удалять
        return [AllowAny()]  # Всем разрешено читать

    def get_queryset(self):
        # Гарантируем аннотацию среднего рейтинга и числа отзывов
        return Artist.objects.all().annotate(
            average_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        )

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, pk=None):
        """
        GET /api/artists/{id}/reviews/
        Возвращает отзывы для данного автора, с пагинацией.
        При этом подтягиваем связанные объекты через select_related.
        """
        artist = self.get_object()
        # выбираем отзывы с select_related('user', 'artist')
        reviews_qs = ArtistReview.objects.filter(artist=artist).select_related('user', 'artist').order_by('-created_at')
        page = self.paginate_queryset(reviews_qs)
        if page is not None:
            serializer = ArtistReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ArtistReviewSerializer(reviews_qs, many=True, context={'request': request})
        return Response(serializer.data)


class GalleryViewSet(viewsets.ModelViewSet):
    """
    CRUD для галерей.
    """
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    @action(detail=False, methods=['get'], url_path='id-name')
    def id_name_list(self, request):
        """
        GET /api/galleries/id-name/
        Возвращает только пары {id, name} для всех галерей.
        """
        data = Gallery.objects.values('id', 'name')
        return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий. Аннотация: количество картин и средняя цена.
    """
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        from django.db.models import Count, Avg
        return Category.objects.annotate(
            num_paintings=Count('painting'),
            avg_price=Avg('painting__price')
        )


class PaintingViewSet(viewsets.ModelViewSet):
    """
    CRUD для картин, с фильтрацией, сортировкой, аннотацией активных акций.
    Поддерживает sparse fieldsets через ?fields=...
    """
    serializer_class = PaintingSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaintingFilter
    pagination_class = PaintingPagination

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        # Подтягиваем gallery через select_related, а изображения через prefetch_related
        qs = Painting.objects.in_stock().select_related('gallery', 'artist').prefetch_related('images')
        params = self.request.query_params
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
        # Добавляем аннотацию: сколько раз картина была добавлена в корзину
        # Предполагается, что в модели Cart FK на Painting имеет related_name='cart' или аналог.
        # Если related_name='cart', то:
        qs = qs.annotate(
            times_added_to_cart=Count('cart')
        )
        return qs

    def get_serializer_context(self):
        """
        Добавляем в context sparse fieldsets: читаем ?fields=field1,field2,...
        Если не задано, context['fields'] будет None, и сериализатор вернёт все поля.
        """
        context = super().get_serializer_context()
        request = self.request

        fields_param = request.query_params.get('fields')
        if fields_param:
            context['fields'] = [f.strip() for f in fields_param.split(',') if f.strip()]
        else:
            context['fields'] = None

        return context


class BannerViewSet(viewsets.ModelViewSet):
    """
    CRUD для баннеров.
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['headline']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ, если пользователь — владелец объекта (User) или is_staff.
    """
    def has_object_permission(self, request, view, obj):
        # obj здесь экземпляр User
        return bool(request.user and (request.user.is_staff or obj == request.user))


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CustomUser.
    - list: только админ может получить список.
    - retrieve: владелец или админ.
    - update/partial_update: владелец или админ.
    - destroy: владелец или админ.
    - create: только админ (регистрация обычно через отдельный endpoint).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['username', 'email']

    def get_permissions(self):
        if self.action == 'create':
            # Регистрация обычно через отдельный RegisterView, поэтому здесь — только админ
            return [permissions.IsAdminUser()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_staff:
            return User.objects.all()
        if user and user.is_authenticated:
            return User.objects.filter(pk=user.pk)
        return User.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class PaintingImageViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet для PaintingImage:
      - POST: загрузка через base64
      - GET list/retrieve: просмотр изображений
    """
    queryset = PaintingImage.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaintingImageUploadSerializer
        return PaintingImageSerializer


class ArtistReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD для отзывов об авторах.
    - Просмотр отзывов разрешён всем.
    - Создание: только аутентифицированные.
    - Изменение/удаление: только владелец или staff.
    """
    serializer_class = ArtistReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['artist', 'user', 'rating']

    def get_queryset(self):
        # Возвращаем все отзывы с подтягиванием связанных artist и user
        return ArtistReview.objects.all().select_related('artist', 'user')

    def perform_create(self, serializer):
        # Если обычный пользователь создает — привязываем к request.user
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            serializer.save(user=self.request.user)
        else:
            # Админ может указать user через payload или просто создать
            serializer.save()

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsReviewOwnerOrReadOnly()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]