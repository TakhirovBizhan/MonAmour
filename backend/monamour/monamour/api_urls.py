# backend/monamour/api_urls.py

from rest_framework.routers import DefaultRouter
from store.views import (
    ArtistViewSet,
    GalleryViewSet,
    CategoryViewSet,
    PaintingImageViewSet,
    PaintingViewSet,
    BannerViewSet,
    UserViewSet,
    ArtistReviewViewSet,  # добавляем импорт
)
from orders.views import CartViewSet, OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'painting-images', PaintingImageViewSet, basename='paintingimage')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'galleries', GalleryViewSet, basename='gallery')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'paintings', PaintingViewSet, basename='painting')
router.register(r'banners', BannerViewSet, basename='banner')

# Добавляем маршрут для отзывов об авторах:
router.register(r'artist-reviews', ArtistReviewViewSet, basename='artistreview')

router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls