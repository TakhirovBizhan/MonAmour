# store/serializers.py
from rest_framework import serializers
from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage
from django.contrib.auth import get_user_model

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'image', 'biography']

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'name', 'description', 'gallery_image']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class PaintingImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    class Meta:
        model = PaintingImage
        fields = ['id', 'image_url']

class PaintingSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    gallery = GallerySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = PaintingImageSerializer(many=True, read_only=True)
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Painting
        fields = [
            'id', 'title', 'description', 'artist', 'gallery', 'category',
            'technique', 'dimensions', 'price', 'discounted_price',
            'status', 'added_at', 'images'
        ]

    def get_discounted_price(self, obj):
        return obj.discounted_price()

class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='banner_image', read_only=True)
    class Meta:
        model = Banner
        fields = ['id', 'headline', 'subheadline', 'link', 'image_url']
        

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']