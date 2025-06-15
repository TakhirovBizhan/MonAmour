from rest_framework.routers import DefaultRouter
from django.urls import path, include
from store.views import (
    ArtistViewSet,
    GalleryViewSet,
    CategoryViewSet,
    PaintingImageViewSet,
    PaintingViewSet,
    BannerViewSet,
    UserViewSet,
    ArtistReviewViewSet,
)
from orders.views import CartViewSet, OrderViewSet, OrderItemViewSet
from accounts.views import RegisterView, MyTokenObtainPairView, UserMeView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'painting-images', PaintingImageViewSet, basename='paintingimage')
router.register(r'artists', ArtistViewSet, basename='artist')
router.register(r'galleries', GalleryViewSet, basename='gallery')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'paintings', PaintingViewSet, basename='painting')
router.register(r'banners', BannerViewSet, basename='banner')
router.register(r'artist-reviews', ArtistReviewViewSet, basename='artistreview')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # Аутентификация
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserMeView.as_view(), name='user_me'),
]