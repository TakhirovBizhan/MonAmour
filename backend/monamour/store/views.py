# store/views.py

from django.db.models import Count, Avg, Q
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
    # Изменено: Разрешаем просмотр всем, но создание/изменение/удаление только аутентифицированным пользователям (или админам)
    # Если только чтение для всех, а запись для аутентифицированных
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # Если создание/обновление/удаление только для админов
    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]  # Только админы могут создавать, обновлять, удалять
        return [AllowAny()]  # Всем разрешено читать

    def get_queryset(self):
        # Переопределяем, чтобы гарантировать аннотацию в любых условиях
        qs = Artist.objects.all().annotate(
            average_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        )
        return qs

    @action(detail=True, methods=['get'], url_path='reviews')
    def reviews(self, request, pk=None):
        """
        GET /api/artists/{id}/reviews/
        Возвращает отзывы для данного автора, с пагинацией.
        """
        artist = self.get_object()
        reviews_qs = ArtistReview.objects.filter(artist=artist).order_by('-created_at')
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
    # Изменено: Только админы могут создавать, обновлять, удалять галереи. Всем разрешено читать.
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
    # Изменено: Только админы могут создавать, обновлять, удалять категории. Всем разрешено читать.
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
    # Изменено: Только админы могут создавать, обновлять, удалять картины. Всем разрешено читать.
    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        qs = Painting.objects.in_stock().select_related('gallery').prefetch_related('images')
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
        # Если FK Cart.painting без related_name, то default related_name 'cart_set'
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
    # Изменено: Только админы могут создавать, обновлять, удалять баннеры. Всем разрешено читать.
    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminUser()]
        return [AllowAny()]
    

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Изменено: Только администраторы могут просматривать, создавать, обновлять и удалять пользователей.
    # Пользователи могут просматривать свой собственный профиль.
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'):
            # Разрешаем просмотр своего профиля аутентифицированному пользователю,
            # но только админы могут просматривать и управлять всеми пользователями.
            if self.action == 'retrieve' and self.request.user.is_authenticated and str(self.request.user.id) == self.kwargs.get('pk'):
                return [IsAuthenticated()]
            return [IsAdminUser()]
        return [AllowAny()] # Можно оставить AllowAny для регистрации, если она обрабатывается отдельно.


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
    # Изменено: Только аутентифицированные пользователи могут создавать изображения. Всем разрешено читать.
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaintingImageUploadSerializer
        return PaintingImageSerializer


class ArtistReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ArtistReviewSerializer
    # Изменено: По умолчанию, только аутентифицированные пользователи могут создавать отзывы,
    # и только владелец отзыва или staff может изменять/удалять его.
    # Просмотр отзывов разрешен всем.
    permission_classes = [IsAuthenticatedOrReadOnly] # Для чтения всем, для записи - аутентифицированным
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['artist', 'user', 'rating']

    def get_queryset(self):
        # Возвращаем все отзывы
        return ArtistReview.objects.all().select_related('artist', 'user')

    def perform_create(self, serializer):
        # Убедимся, что user из токена автоматически связывается с отзывом,
        # если пользователь не является админом и не передал user_id.
        # Если админ передает user_id, то он может создать отзыв от имени другого пользователя.
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            serializer.save(user=self.request.user)
        else:
            serializer.save() # Для админа или если user_id указан в validated_data

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            # Для обновления и удаления - аутентифицированному пользователю, который является владельцем или staff.
            return [IsAuthenticated(), IsReviewOwnerOrReadOnly()]
        if self.action == 'create':
            # Для создания - только аутентифицированным пользователям.
            return [IsAuthenticated()]
        # Для остальных действий (например, list, retrieve) - всем.
        return [AllowAny()]
