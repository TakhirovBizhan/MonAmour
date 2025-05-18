from django.contrib import admin
from django.utils.html import format_html
from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage
from django.utils import timezone


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_biography')
    search_fields = ('biography', 'name',)
    list_display_links = ('id', 'name')

    @admin.display(description='Краткая биография')
    def short_biography(self, obj):
        return obj.biography[:50] if obj.biography else ''

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )
    search_fields = ('name', 'description')
    list_display_links = ('id', 'name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'updated_at')
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
    list_display = ('title', 'artist', 'gallery', 'status', 'added_at', 'price')
    list_filter = ('gallery', 'status', 'added_at')
    date_hierarchy = 'added_at'
    search_fields = ('title', 'description')
    raw_id_fields = ('artist', 'gallery')
    readonly_fields = ('added_at',)
    list_display_links = ('title', 'artist', 'gallery')
    inlines = [PaintingImageInline]
    
    @admin.display(boolean=True, description='Активна сейчас')
    def is_active(self) -> bool:
        now = timezone.now()
        return self.start <= now <= self.end

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('headline', 'subheadline', 'image_preview')
    list_filter = ('headline',)
    search_fields = ('headline', 'subheadline')
    list_display_links = ('subheadline', 'headline')

    @admin.display(description='Превью изображения')
    def image_preview(self, obj):
        if obj.banner_image:
            return format_html('<img src="{}" width="100" />', obj.banner_image.url)
        return 'Нет изображения'