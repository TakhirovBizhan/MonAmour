from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Artist, Gallery, Category, Painting, Banner, PaintingImage
from django.utils import timezone


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_biography')
    search_fields = ('biography', 'name',)
    list_display_links = ('id', 'name')
    
    fields = (
        'name',
        'image',
        'biography',
        'resume',
        'website',
    )

    @admin.display(description='Краткая биография')
    def short_biography(self, obj):
        return obj.biography[:50] if obj.biography else ''
    
    @admin.display(description='Есть резюме')
    def has_resume(self, obj):
        return bool(obj.resume)
    

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

class PaintingAdminForm(forms.ModelForm):
    class Meta:
        model = Painting
        fields = '__all__'

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        qs = Painting.objects.filter(title__iexact=title)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Картина с таким названием уже существует.")
        return title

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
    form = PaintingAdminForm  # подключаем форму с проверкой clean_title
    list_display = ('title', 'artist', 'gallery', 'status', 'added_at', 'price')
    list_filter = ('artist', 'gallery', 'status', 'added_at')
    date_hierarchy = 'added_at'
    search_fields = ('title', 'description')
    raw_id_fields = ('artist', 'gallery')
    readonly_fields = ('added_at',)
    list_display_links = ('title', 'artist', 'gallery')
    inlines = [PaintingImageInline]
    
    
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
    
    @admin.display(boolean=True, description='Активна сейчас')
    def is_active(self) -> bool:
        now = timezone.now()
        return self.start <= now <= self.end