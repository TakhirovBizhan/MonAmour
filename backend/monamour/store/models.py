import uuid
from django.db import models

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Имя художника')
    image = models.ImageField(upload_to='Artists/', blank=True, verbose_name='Изображение')
    biography = models.TextField(verbose_name='Биография')
    
    def __str__(self):
        return f"Artist {self.id}"
    
    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    gallery_image = models.ImageField(upload_to='gallery/', blank=True, verbose_name='Изображение')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Галлерея'
        verbose_name_plural = 'Галлереи'

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано в')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено в')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        

class Painting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, verbose_name='Художник')
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE, verbose_name='Галерея')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    technique = models.CharField(max_length=255, blank=True, verbose_name='Техника')
    dimensions = models.CharField(max_length=100, blank=True, verbose_name='Размеры')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    status = models.CharField(max_length=10, choices=[('available', 'В наличии'), ('sold', 'Продано')], default='available', verbose_name='Наличие')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Картина'
        verbose_name_plural = 'Картины'


class PaintingImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='images', verbose_name='Картина')
    image = models.ImageField(upload_to='paintings/', verbose_name='Изображение')

    def __str__(self):
        return f'Изображение для {self.painting.title}'

    class Meta:
        verbose_name = 'Изображение картины'
        verbose_name_plural = 'Изображения картин'

class Banner(models.Model):
    banner_image = models.ImageField(upload_to='Banners/', verbose_name='Изображение')
    headline = models.CharField(max_length=255, blank=True, verbose_name='Заголовок')
    subheadline = models.CharField(max_length=255, blank=True, verbose_name='Подзаголовок')
    link = models.URLField(blank=True, verbose_name='Ссылка')

    def __str__(self):
        return self.headline

    class Meta:
        verbose_name = 'Рекламный баннер'
        verbose_name_plural = 'Рекламные баннеры'