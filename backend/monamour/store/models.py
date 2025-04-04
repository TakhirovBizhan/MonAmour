import uuid
from django.db import models

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    biography = models.TextField()
    portfolio = models.TextField(blank=True)
    social_links = models.TextField(blank=True)

    def __str__(self):
        return f"Artist {self.id}"

class Gallery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Painting(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('sold', 'Продано'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='paintings')
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='paintings')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='paintings')
    technique = models.CharField(max_length=255, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    city_created = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Banner(models.Model):
    image_url = models.URLField()
    headline = models.CharField(max_length=255)
    subheadline = models.CharField(max_length=255, blank=True)
    link = models.URLField(blank=True)

    def __str__(self):
        return self.headline