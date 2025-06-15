import uuid
from django.db import models
from django.conf import settings
from store.models import Painting

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts', verbose_name='Пользователь')
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, verbose_name='Картина')  
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    def __str__(self):
        return f"Корзина {self.user}"
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ['-added_at', 'user']

class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь',
        default=''
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing',
        verbose_name='Статус'
    )
    # Новые поля для адреса доставки:
    street = models.CharField(
        max_length=255,
        verbose_name='Улица',
        default=''
    )
    house_number = models.CharField(
        max_length=20,
        verbose_name='Номер дома',
        default=''
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город',
        default=''
    )
    postal_code = models.CharField(
        max_length=20,
        verbose_name='Почтовый индекс',
        default=''
    )
    address_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий к адресу'
    )
    # ManyToMany через OrderItem:
    paintings = models.ManyToManyField(
        Painting,
        through='OrderItem',
        related_name='orders',
        verbose_name='Картины в заказе'
    )

    def __str__(self):
        return f"Заказ {self.id}, {self.user}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date', 'user']

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    painting = models.ForeignKey(Painting, on_delete=models.CASCADE, verbose_name='Картина')
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата/время покупки')

    def __str__(self):
        return f"{self.painting} — куплено {self.purchased_at}"
    
    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элемент заказов'