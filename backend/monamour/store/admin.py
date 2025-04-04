from django.contrib import admin
from .models import Artist, Gallery, Category, Painting, Banner

admin.site.register(Artist)
admin.site.register(Gallery)
admin.site.register(Category)
admin.site.register(Painting)
admin.site.register(Banner)