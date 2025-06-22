import uuid
from django.db import models
from django.conf import settings
from store.models import Painting
from typing import Any


class Cart(models.Model):
    """
    Model Cart: хранит связь пользователя и добавленной в корзину картины.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь'
    )
    painting = models.ForeignKey(
        Painting,
        on_delete=models.CASCADE,
        verbose_name='Картина'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    def __str__(self) -> str:
        """
        Представление объекта Cart в виде строки.
        """
        return f"Корзина {self.user}"

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ['-added_at', 'user']


class Order(models.Model):
    """
    Model Order: хранит информацию о заказе:
    связь с пользователем, адрес доставки, способ оплаты, телефон, статус и связанные картины через OrderItem.
    """
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Картой'),
        ('cash', 'Наличными'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing',
        verbose_name='Статус'
    )
    # Адрес доставки
    street = models.CharField(max_length=255, verbose_name='Улица', default='')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома', default='')
    city = models.CharField(max_length=100, verbose_name='Город', default='')
    postal_code = models.CharField(max_length=20, verbose_name='Почтовый индекс', default='')
    address_comment = models.TextField(blank=True, null=True, verbose_name='Комментарий к адресу')
    # Способ оплаты и телефон
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='card',
        verbose_name='Способ оплаты'
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        default='',
        help_text='Контактный номер телефона клиента'
    )
    paintings = models.ManyToManyField(
        Painting,
        through='OrderItem',
        related_name='orders',
        verbose_name='Картины в заказе'
    )

    def __str__(self) -> str:
        """
        Представление заказа в виде строки.
        """
        return f"Заказ {self.id}, {self.user}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date', 'user']


class OrderItem(models.Model):
    """
    Model OrderItem: элемент заказа, связывает Order и Painting, хранит цену на момент покупки и время.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    painting = models.ForeignKey(
        Painting,
        on_delete=models.CASCADE,
        verbose_name='Картина'
    )
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата/время покупки')

    def __str__(self) -> str:
        """
        Представление элемента заказа в виде строки.
        """
        return f"{self.painting} — куплено {self.purchased_at}"

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элемент заказов'