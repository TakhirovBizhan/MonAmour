from __future__ import annotations
from decimal import Decimal
from typing import Any, Dict, Optional, List
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Count

from .models import Artist, ArtistReview, Gallery, Category, Painting, Banner, PaintingImage
from drf_extra_fields.fields import Base64ImageField

User = get_user_model()


class ArtistSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Artist.
    Включает вычисляемые поля:
    - average_rating: средний рейтинг автора
    - reviews_count: число отзывов об авторе
    """
    resume = serializers.FileField(required=False)
    average_rating = serializers.SerializerMethodField(read_only=True)
    reviews_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'image', 'biography', 'resume', 'website',
            'average_rating', 'reviews_count'
        ]

    def get_average_rating(self, obj: Artist) -> Optional[float]:
        """
        Вычисляет средний рейтинг автора.
        Если нет отзывов, возвращает None.
        """
        agg = obj.reviews.aggregate(avg=Avg('rating'))
        avg = agg.get('avg')
        if avg is None:
            return None
        return round(avg, 2)

    def get_reviews_count(self, obj: Artist) -> int:
        """
        Возвращает число отзывов об авторе.
        """
        cnt = obj.reviews.aggregate(count=Count('id')).get('count', 0)
        return cnt


class ArtistReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов об авторах (ArtistReview).
    Логика:
    - user: отображается через StringRelatedField (readonly)
    - user_id: для записи (write_only), при создании привязывает request.user, если это не админ
    - artist: отображается вложенно (readonly)
    - artist_id: для записи (write_only)
    Валидация:
    - рейтинг от 1 до 5
    - уникальность пары (artist, user) при создании
    - нельзя менять artist/user при обновлении
    """
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist',
        write_only=True
    )

    class Meta:
        model = ArtistReview
        fields = [
            'id',
            'artist', 'artist_id',
            'user', 'user_id',
            'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'artist', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value: int) -> int:
        """
        Проверяет, что рейтинг в диапазоне 1–5.
        """
        if not (1 <= value <= 5):
            raise serializers.ValidationError(_("Оценка должна быть от 1 до 5."))
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Общая валидация:
        - Определяет пользователя (request.user или user_id для админа).
        - При создании проверяет, что отзыв от того же user для данного artist не дублируется.
        - При обновлении запрещает менять artist или user.
        """
        request = self.context.get('request')
        user_from_payload = attrs.get('user', None)
        artist_from_payload = attrs.get('artist', None)

        if request and request.user and request.user.is_authenticated:
            if user_from_payload:
                # Если передан user_id, разрешено только админу
                if not request.user.is_staff:
                    raise serializers.ValidationError({
                        'user_id': _("Вы не можете указывать другого пользователя.")
                    })
                user_to_set = user_from_payload
            else:
                user_to_set = request.user
            # Гарантируем, что attrs['user'] установлен корректно
            attrs['user'] = user_to_set
        else:
            raise serializers.ValidationError(_("Необходима аутентификация для оставления/изменения отзыва."))

        # При создании проверяем уникальность
        if self.instance is None:
            artist_obj = attrs.get('artist')
            if artist_obj:
                exists = ArtistReview.objects.filter(artist=artist_obj, user=user_to_set).exists()
                if exists:
                    raise serializers.ValidationError(_("Вы уже оставили отзыв об этом авторе."))
        else:
            # При обновлении запрещаем менять artist/user
            if artist_from_payload is not None:
                raise serializers.ValidationError({
                    'artist_id': _("Нельзя менять автора отзыва при обновлении.")
                })
            # Любые попытки сменить user будут удалены в update()
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> ArtistReview:
        """
        Создаёт отзыв; поля 'artist' и 'user' уже установлены в validate().
        """
        return super().create(validated_data)

    def update(self, instance: ArtistReview, validated_data: Dict[str, Any]) -> ArtistReview:
        """
        Обновляет отзыв, запрещая менять user и artist.
        """
        validated_data.pop('user', None)
        validated_data.pop('artist', None)
        return super().update(instance, validated_data)


class GallerySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Gallery.
    """
    class Meta:
        model = Gallery
        fields = ['id', 'name', 'description', 'gallery_image']


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class PaintingImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели PaintingImage.
    Возвращает поле image_url, указывающее URL изображения.
    """
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = PaintingImage
        fields = ['id', 'image_url']


class PaintingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Painting.
    - Вложенные read-only поля: artist, gallery, category
    - Вычисляемое поле discounted_price через SerializerMethodField
    - times_added_to_cart: аннотированное поле из ViewSet
    - При записи: artist_id, gallery_id, category_id, image_ids
    """
    artist = ArtistSerializer(read_only=True)
    gallery = GallerySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    times_added_to_cart = serializers.IntegerField(read_only=True)

    artist_id = serializers.PrimaryKeyRelatedField(
        source='artist', queryset=Artist.objects.all(), write_only=True
    )
    gallery_id = serializers.PrimaryKeyRelatedField(
        source='gallery', queryset=Gallery.objects.all(), write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(),
        write_only=True, allow_null=True, required=False
    )
    images = PaintingImageSerializer(many=True, read_only=True)
    image_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
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
            'images', 'image_ids',
            'times_added_to_cart'
        ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Поддержка sparse fieldsets: если context['fields'] задан, в GET/DELETE
        оставляем только указанные поля + id + write-only поля для валидации.
        """
        super().__init__(*args, **kwargs)
        context = self.context or {}
        fields_param: Optional[List[str]] = context.get('fields')
        request = context.get('request', None)
        if fields_param is not None and request and request.method in ('GET', 'DELETE'):
            allowed = set(fields_param)
            allowed.add('id')
            write_fields = {'artist_id', 'gallery_id', 'category_id', 'image_ids'}
            allowed |= write_fields
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

    def validate_title(self, value: str) -> str:
        """
        Проверяет уникальность названия картины (игнорируя текущую при обновлении).
        """
        qs = Painting.objects.filter(title__iexact=value.strip())
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(_("Картина с таким названием уже существует."))
        return value

    def get_discounted_price(self, obj: Painting) -> Decimal:
        """
        Возвращает цену с учётом скидки, вычисляемую в модели.
        """
        return obj.discounted_price()

    def create(self, validated_data: Dict[str, Any]) -> Painting:
        """
        Создаёт объект Painting и связывает изображения по image_ids.
        """
        image_ids = validated_data.pop('image_ids', [])
        painting = super().create(validated_data)
        if image_ids:
            PaintingImage.objects.filter(id__in=image_ids).update(painting=painting)
        return painting

    def update(self, instance: Painting, validated_data: Dict[str, Any]) -> Painting:
        """
        Обновляет Painting и обновляет связи изображений по image_ids.
        """
        image_ids = validated_data.pop('image_ids', None)
        painting = super().update(instance, validated_data)
        if image_ids is not None:
            # отвязываем старые
            PaintingImage.objects.filter(painting=painting).update(painting=None)
            PaintingImage.objects.filter(id__in=image_ids).update(painting=painting)
        return painting


class BannerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Banner.
    """
    image_url = serializers.ImageField(source='banner_image', read_only=True)

    class Meta:
        model = Banner
        fields = ['id', 'headline', 'subheadline', 'link', 'image_url']


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CustomUser.
    Позволяет редактировать только основные поля пользователя.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'role',
            'date_joined',
            'is_staff',
            'is_active',
            'last_login',
            'groups',
            'user_permissions',
        ]


class PaintingImageUploadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для загрузки изображения картины через Base64.
    """
    image = Base64ImageField()

    class Meta:
        model = PaintingImage
        fields = ['id', 'image']
        read_only_fields = ['id']