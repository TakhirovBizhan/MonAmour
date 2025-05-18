# store/views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, filters
from .models import Artist, Gallery, Category, Painting, Banner
from .serializers import (
    ArtistSerializer,
    GallerySerializer,
    CategorySerializer,
    PaintingSerializer,
    BannerSerializer,
)

# Фильтрация для картин
class PaintingFilter(FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    artist = filters.CharFilter(field_name='artist__name', lookup_expr='icontains')
    gallery = filters.CharFilter(field_name='gallery__name', lookup_expr='icontains')
    added_before = filters.DateTimeFilter(field_name='added_at', lookup_expr='lte')
    added_after = filters.DateTimeFilter(field_name='added_at', lookup_expr='gte')

    class Meta:
        model = Painting
        fields = ['status', 'category', 'artist', 'gallery', 'min_price', 'max_price', 'added_before', 'added_after']

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']  # базовая фильтрация по имени

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

class PaintingViewSet(viewsets.ModelViewSet):
    queryset = Painting.objects.select_related('artist', 'gallery').prefetch_related('images')
    serializer_class = PaintingSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PaintingFilter

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['headline']
