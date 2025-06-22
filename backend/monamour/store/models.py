from __future__ import annotations
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.conf import settings

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class PaintingQuerySet(models.QuerySet["Painting"]):
    """
    Кастомный QuerySet для модели Painting с дополнительными методами-фильтрами.
    """

    def expensive(self, threshold: Decimal) -> PaintingQuerySet:
        """
        Возвращает картины, цена которых больше переданного порога.

        :param threshold: Пороговая стоимость.
        :return: QuerySet картин с ценой > threshold.
        """
        return self.filter(price__gt=threshold)

    def in_stock(self) -> PaintingQuerySet:
        """
        Возвращает только доступные картины (status='available').

        :return: QuerySet доступных картин.
        """
        return self.filter(status='available')

    def with_active_promotions(self) -> PaintingQuerySet:
        """
        Возвращает картины, у которых есть текущие (актуальные) акции.
        Акция считается активной, если start <= now <= end.

        :return: QuerySet картин с активными акциями.
        """
        now = timezone.now()
        return self.filter(promotions__start__lte=now, promotions__end__gte=now).distinct()


class Artist(models.Model):
    """
    Модель художника (Artist).
    Содержит информацию о художнике: имя, изображение, биография, резюме (PDF), сайт.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=255, verbose_name='Имя художника')
    image: models.ImageField = models.ImageField(upload_to='Artists/', blank=True, verbose_name='Изображение')
    biography: str = models.TextField(verbose_name='Биография')
    resume: models.FileField = models.FileField(
        upload_to='artist_resumes/',
        blank=True,
        null=True,
        verbose_name='Резюме (PDF)'
    )
    website: str | None = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Официальный сайт'
    )

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['name']

    def __str__(self) -> str:
        """
        Строковое представление: имя художника.
        """
        return self.name


class Gallery(models.Model):
    """
    Модель галереи (Gallery).
    Содержит название, описание и изображение галереи.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=255, verbose_name='Название галереи')
    description: str = models.TextField(blank=True, verbose_name='Описание')
    gallery_image: models.ImageField = models.ImageField(upload_to='gallery/', blank=True, verbose_name='Изображение')

    class Meta:
        verbose_name = 'Галлерея'
        verbose_name_plural = 'Галлереи'
        ordering = ['name']

    def __str__(self) -> str:
        """
        Строковое представление: название галереи.
        """
        return self.name


class Category(models.Model):
    """
    Модель категории (Category) для картин.
    Содержит название, описание и временные метки создания и обновления.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name: str = models.CharField(max_length=255, verbose_name='Название')
    description: str = models.TextField(blank=True, verbose_name='Описание')
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name='Создано в')
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True, verbose_name='Обновлено в')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['created_at', 'name']

    def __str__(self) -> str:
        """
        Строковое представление: название категории.
        """
        return self.name


class Painting(models.Model):
    """
    Модель картины (Painting).
    Использует кастомный менеджер PaintingQuerySet для фильтров.
    """
    objects: PaintingQuerySet = PaintingQuerySet.as_manager()

    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title: str = models.CharField(max_length=255, verbose_name='Название')
    description: str = models.TextField(blank=True, verbose_name='Описание')
    artist: Artist = models.ForeignKey('Artist', on_delete=models.CASCADE, verbose_name='Художник')
    gallery: Gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE, verbose_name='Галерея')
    category: Category | None = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    technique: str = models.CharField(max_length=255, blank=True, verbose_name='Техника')
    dimensions: str = models.CharField(max_length=100, blank=True, verbose_name='Размеры')
    price: Decimal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    status: str = models.CharField(
        max_length=10,
        choices=[('available', 'В наличии'), ('sold', 'Продано')],
        default='available',
        verbose_name='Наличие'
    )
    added_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Картина'
        verbose_name_plural = 'Картины'
        ordering = ['added_at', 'title']

    def __str__(self) -> str:
        """
        Строковое представление: название картины.
        """
        return self.title

    def days_in_stock(self) -> int:
        """
        Возвращает число полных дней с момента добавления на склад до текущего момента.

        :return: Количество дней нахождения в наличии.
        """
        delta = timezone.now() - self.added_at
        return delta.days

    def discounted_price(self) -> Decimal:
        """
        Вычисляет скидку в зависимости от времени нахождения в наличии:
         - > 60 дней: 10% скидка
         - > 30 дней: 5% скидка
         - иначе: без скидки

        :return: Цена с учётом скидки, округленная до двух знаков после запятой.
        """
        days = self.days_in_stock()
        if days > 60:
            factor = Decimal('0.90')
        elif days > 30:
            factor = Decimal('0.95')
        else:
            factor = Decimal('1.00')
        return (self.price * factor).quantize(Decimal('0.01'))


class Promotion(models.Model):
    """
    Модель акции (Promotion) для картины.
    Содержит процент скидки, дату начала и окончания акции.
    """
    painting: Painting = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='promotions')
    discount_percent: int = models.PositiveSmallIntegerField(verbose_name='Скидка, %')
    start: models.DateTimeField = models.DateTimeField(default=timezone.now, verbose_name='Начало акции')
    end: models.DateTimeField = models.DateTimeField(verbose_name='Окончание акции')

    def __str__(self) -> str:
        """
        Строковое представление: описание акции.
        """
        return f"Акция для {self.painting}: {self.discount_percent}% с {self.start} по {self.end}"


class PaintingImage(models.Model):
    """
    Модель изображения картины (PaintingImage).
    Содержит ссылку на картину и само изображение.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    painting: Painting | None = models.ForeignKey(
        Painting,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Картина',
        null=True,
        blank=True
    )
    image: models.ImageField = models.ImageField(upload_to='paintings/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Изображение картины'
        verbose_name_plural = 'Изображения картин'

    def __str__(self) -> str:
        """
        Строковое представление: указывает, к какой картине относится изображение.
        """
        title = self.painting.title if self.painting else "Без картины"
        return f'Изображение для {title}'


class Banner(models.Model):
    """
    Модель рекламного баннера (Banner).
    Содержит изображение, заголовок, подзаголовок и ссылку.
    """
    banner_image: models.ImageField = models.ImageField(upload_to='Banners/', verbose_name='Изображение')
    headline: str = models.CharField(max_length=255, blank=True, verbose_name='Заголовок')
    subheadline: str = models.CharField(max_length=255, blank=True, verbose_name='Подзаголовок')
    link: str = models.URLField(blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Рекламный баннер'
        verbose_name_plural = 'Рекламные баннеры'

    def __str__(self) -> str:
        """
        Строковое представление: заголовок баннера.
        """
        return self.headline


class ArtistReview(models.Model):
    """
    Модель отзыва об авторе (ArtistReview).
    Один пользователь может оставить только один отзыв на конкретного художника.
    Содержит рейтинг 1–5, комментарий и временные метки.
    """
    id: uuid.UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist: Artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Художник'
    )
    user: settings.AUTH_USER_MODEL = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='artist_reviews',
        verbose_name='Пользователь'
    )
    rating: int = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment: str = models.TextField(verbose_name='Комментарий', blank=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Отзыв об авторе'
        verbose_name_plural = 'Отзывы об авторах'
        ordering = ['-created_at']
        # Для уникальности можно добавить:
        # unique_together = ('artist', 'user')

    def __str__(self) -> str:
        """
        Строковое представление: показывает пользователя, художника и рейтинг.
        """
        return f"Отзыв пользователя {self.user} об авторе {self.artist} ({self.rating})"