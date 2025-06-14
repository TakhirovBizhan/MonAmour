# store/serializers.py
from rest_framework import serializers
from .models import Artist, ArtistReview, Gallery, Category, Painting, Banner, PaintingImage
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from django.db.models import Avg, Count

User = get_user_model()


class ArtistSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(required=False)

    # Добавляем поля среднего рейтинга и числа отзывов:
    average_rating = serializers.SerializerMethodField(read_only=True)
    reviews_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Artist
        fields = [
            'id', 'name', 'image', 'biography', 'resume', 'website',
            'average_rating', 'reviews_count'
        ]

    def get_average_rating(self, obj):
        """
        Возвращает среднюю оценку автора, округлённую, например, до 2 знаков после запятой.
        """
        # Если в context передали аннотацию, можно использовать: obj.average_rating
        # Но для простоты делаем запрос:
        agg = obj.reviews.aggregate(avg=Avg('rating'))
        avg = agg.get('avg')
        if avg is None:
            return None
        # Округляем до 2 знаков:
        return round(avg, 2)

    def get_reviews_count(self, obj):
        """
        Возвращает число отзывов для автора.
        """
        # Аналогично: можно использовать аннотацию, или считать:
        cnt = obj.reviews.aggregate(count=Count('id')).get('count', 0)
        return cnt

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Artist, ArtistReview
from .serializers import ArtistSerializer  # или скорректированный импорт
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ArtistReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор отзывов об авторах.
    - Обычный пользователь: отзыв создаётся за request.user, поле user_id игнорируется.
    - Администратор (is_staff): может указать user_id, чтобы создать отзыв от имени другого пользователя.
    При обновлении (PATCH/PUT) нельзя менять author или user, независимо от прав.
    """
    # Отображаем текущего пользователя как строку (username или __str__)
    user = serializers.StringRelatedField(read_only=True)
    # Поле для установки пользователя: только для записи, необязательное
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    # Отображаем автора вложенно
    artist = ArtistSerializer(read_only=True)
    # Поле для установки автора: только для записи, обязательное при создании
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

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError(_("Оценка должна быть от 1 до 5."))
        return value

    def validate(self, attrs):
        """
        Общая валидация:
        - Определяем, под каким пользователем будет создаётся/обновляться отзыв:
          * Если админ и в attrs есть 'user', используем указанный user.
          * Иначе (не админ или user не указан) — ставим user = request.user.
        - Проверяем уникальность пары (artist, user) при создании: 
          нельзя создать второй отзыв тем же user на того же artist.
        - При обновлении (self.instance существует) не даём менять artist или user.
        """
        request = self.context.get('request')
        user_from_payload = attrs.get('user', None)  # может быть None или User instance
        artist_from_payload = attrs.get('artist', None)  # может быть None при обновлении

        # Определяем user_to_set: если админ и передал user_id, то ставим этот user; иначе request.user
        if request and request.user and request.user.is_authenticated:
            if user_from_payload:
                # Передано user_id в запросе
                if not request.user.is_staff:
                    raise serializers.ValidationError({
                        'user_id': _("Вы не можете указывать другого пользователя.")
                    })
                # Если админ, оставляем attrs['user'] как есть
                user_to_set = user_from_payload
            else:
                # user_from_payload не передан: ставим request.user
                user_to_set = request.user
            # Для безопасности: убираем attrs['user'] на случай, если non-staff пытался передать user_id
            attrs['user'] = user_to_set
        else:
            raise serializers.ValidationError(_("Необходима аутентификация для оставления/изменения отзыва."))

        # Проверяем уникальность при создании
        if self.instance is None:
            # Создание
            artist = attrs.get('artist')  # из artist_id через source
            if artist is None:
                # Обычно artist_id обязателен при создании, DRF сам проверит отсутствие
                pass
            else:
                # Проверяем, есть ли уже отзыв тем же user_to_set об этом artist
                exists = ArtistReview.objects.filter(artist=artist, user=user_to_set).exists()
                if exists:
                    raise serializers.ValidationError(_("Вы уже оставили отзыв об этом авторе."))
        else:
            # Обновление: запрещаем менять artist или user
            # Если в attrs есть artist (т.е. клиент передал artist_id), отклоним
            if artist_from_payload is not None:
                raise serializers.ValidationError({
                    'artist_id': _("Нельзя менять автора отзыва при обновлении.")
                })
            # Если в attrs есть user и request.user.is_staff и админ пытался изменить user, запрещаем
            # attrs['user'] уже установлен выше, но для обновления мы его удалим ниже
            # Поэтому здесь можно просто игнорировать any user in payload
            # Не нужно дополнительная проверка, т.к. ниже в update мы уберём user
            pass

        return attrs

    def create(self, validated_data):
        """
        Создаём отзыв. validated_data уже содержит 'artist' и 'user' после validate().
        """
        # validated_data['user'] и ['artist'] уже установлены корректно
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Обновляем отзыв: запрещаем менять user и artist.
        Просто обновляем rating и comment.
        """
        # Убираем любые попытки изменить user или artist:
        validated_data.pop('user', None)
        validated_data.pop('artist', None)
        return super().update(instance, validated_data)

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
        source='category', queryset=Category.objects.all(),
        write_only=True, allow_null=True, required=False
    )
    images = PaintingImageSerializer(many=True, read_only=True)
    image_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True, required=False,
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

    def __init__(self, *args, **kwargs):
        """
        Поддержка sparse fieldsets: если context['fields'] задан непустым списком и запрос GET/DELETE,
        оставляем только указанные поля + id + write-only поля для валидации POST/PUT.
        При обычном GET без ?fields все поля остаются.
        """
        super().__init__(*args, **kwargs)
        context = self.context or {}
        fields = context.get('fields')
        request = context.get('request', None)
        # Применяем pruning только если явно указан fields и метод GET или DELETE:
        if fields is not None and request and request.method in ('GET', 'DELETE'):
            allowed = set(fields)
            # Всегда оставляем id (ключевой PK)
            allowed.add('id')
            # Оставляем поля для записи, чтобы сериализатор мог валидировать POST/PUT,
            # хотя при GET они не видны (write_only=True)
            write_fields = {'artist_id', 'gallery_id', 'category_id', 'image_ids'}
            allowed |= write_fields
            for field_name in list(self.fields):
                if field_name not in allowed:
                    self.fields.pop(field_name)

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
            # Вместо painting.images.clear() корректно отвязываем:
            PaintingImage.objects.filter(painting=painting).update(painting=None)
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

class PaintingImageUploadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    class Meta:
        model = PaintingImage
        fields = ['id', 'image']
        read_only_fields = ['id']