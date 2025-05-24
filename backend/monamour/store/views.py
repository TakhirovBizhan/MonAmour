# store/views.py
from django.db.models import Count
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from django.utils import timezone
from django.db import models
from .models import Artist, Gallery, Category, Painting, Banner
from .serializers import (
    ArtistSerializer,
    GallerySerializer,
    CategorySerializer,
    PaintingSerializer,
    BannerSerializer,
    UserSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters import rest_framework as df_filters
UUIDFilter = df_filters.UUIDFilter


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
        model  = Painting
        fields = [
            'status', 'title', 'category', 'gallery',
            'min_price', 'max_price', 'added_before', 'added_after'
        ]

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_queryset(self):
        # 1) Количество картин в каждой категории
        # 2) Средняя цена картин в категории
        from django.db.models import Count, Avg
        return Category.objects.annotate(
            num_paintings=Count('painting'),
            avg_price=Avg('painting__price')
        )

class PaintingViewSet(viewsets.ModelViewSet):
    serializer_class = PaintingSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaintingFilter

    def get_queryset(self):
        # пример использования собственного менеджера
        qs = Painting.objects.in_stock() # .expensive(50000)
        qs = qs.select_related('artist', 'gallery').prefetch_related('images')

        # lookup-выражения
        params = self.request.query_params
        if params.get('min_price'):
            qs = qs.filter(price__gt=params['min_price'])

        # сортировка
        sort = params.get('sort')
        if sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'price_asc':
            qs = qs.order_by('price')
        else:
            qs = qs.order_by('-added_at')

        # 3) Количество активных акций (аннотация с фильтром)
        now = timezone.now()
        qs = qs.annotate(
            active_promotions_count= Count(
                'promotions',
                filter=models.Q(promotions__start__lte=now, promotions__end__gte=now)
            )
        )
        return qs

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['headline']


User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Позволяет:
      - администратору: CRUD по любому пользователю
      - аутентифицированному юзеру: получать и править свой профиль
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # авторизованные могут читать и править только себя
        if self.action in ('retrieve', 'update', 'partial_update'):
            return [IsAuthenticated()]
        # на список, создание и удаление — только админ
        return [IsAdminUser()]
    
    def get_queryset(self):
        # если это обычный пользователь — пусть видит только себя
        user = self.request.user
        if not user.is_staff:
            return User.objects.filter(pk=user.pk)
        return super().get_queryset()
