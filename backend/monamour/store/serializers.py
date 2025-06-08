# store/serializers.py
from rest_framework import serializers
from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage
from django.contrib.auth import get_user_model

class ArtistSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=False)
    
    class Meta:
        model = Artist
        fields = ['id', 'name', 'image', 'biography', 'resume', 'website']
        

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
    # nested read-only
    artist = ArtistSerializer(read_only=True)
    gallery = GallerySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    # write-only PK fields
    artist_id = serializers.PrimaryKeyRelatedField(
        source='artist', queryset=Artist.objects.all(), write_only=True
    )
    gallery_id = serializers.PrimaryKeyRelatedField(
        source='gallery', queryset=Gallery.objects.all(), write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True, allow_null=True, required=False
    )
    images = PaintingImageSerializer(many=True, read_only=True)
    image_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False,
        help_text='List of existing PaintingImage IDs to associate'
    )
    discounted_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Painting
        fields = [
            'id', 'title', 'description',
            'artist', 'artist_id',
            'gallery', 'gallery_id',
            'category', 'category_id',
            'technique', 'dimensions', 'price',
            'discounted_price', 'status', 'added_at',
            'images', 'image_ids'
        ]

    def get_discounted_price(self, obj):
        return obj.discounted_price()

    def create(self, validated_data):
        image_ids = validated_data.pop('image_ids', [])
        painting = super().create(validated_data)
        if image_ids:
            PaintingImage.objects.filter(id__in=image_ids).update(painting=painting)
        return painting

    def update(self, instance, validated_data):
        image_ids = validated_data.pop('image_ids', None)
        painting = super().update(instance, validated_data)
        if image_ids is not None:
            # detach all then re-attach
            painting.images.clear()
            PaintingImage.objects.filter(id__in=image_ids).update(painting=painting)
        return painting

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