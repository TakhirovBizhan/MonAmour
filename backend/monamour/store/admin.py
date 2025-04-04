from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_biography')
    list_filter = ('biography',)  # при необходимости замените на другое поле
    search_fields = ('biography',)
    list_display_links = ('id', 'short_biography')

    @admin.display(description='Краткая биография')
    def short_biography(self, obj):
        return obj.biography[:50] if obj.biography else ''

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    list_display_links = ('id', 'name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    search_fields = ('name', 'description')
    list_display_links = ('id', 'name')

class PaintingImageInline(admin.TabularInline):
    model = PaintingImage
    extra = 1
    readonly_fields = ('image_preview',)

    @admin.display(description='Превью изображения')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return 'Нет изображения'

@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'artist', 'gallery', 'price', 'status', 'added_at', 'price_in_rub')
    list_filter = ('artist', 'gallery', 'status', 'added_at')
    date_hierarchy = 'added_at'
    search_fields = ('title', 'description')
    raw_id_fields = ('artist', 'gallery')
    readonly_fields = ('added_at',)
    list_display_links = ('id', 'title')
    inlines = [PaintingImageInline]

    @admin.display(description='Цена в рублях')
    def price_in_rub(self, obj):
        return f'{obj.price} ₽'

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'headline', 'subheadline', 'image_preview')
    list_filter = ('headline',)
    search_fields = ('headline', 'subheadline')
    list_display_links = ('id', 'headline')

    @admin.display(description='Превью изображения')
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return 'Нет изображения'