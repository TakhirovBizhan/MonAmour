from django.contrib import admin

from .models import Cart, Order, OrderItem
from store.models import Painting

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

# Импортируем ReportLab-модули для регистратуры TTF-шрифтов:
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse


FONT_PATH = 'monamour/Roboto/roboto.ttf'  # скорректируйте, если путь другой

# 1) Зарегистрируем шрифт под именем 'DejaVuSans'
pdfmetrics.registerFont(TTFont('Roboto', FONT_PATH))


def generate_orders_pdf(modeladmin, request, queryset):
    if not queryset.exists():
        return
    order = queryset.first()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # 2) Создаём canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 3) Указываем зарегистрированный шрифт «DejaVuSans»
    # вместо стандартного Helvetica
    p.setFont("Roboto", 16)
    p.drawString(50, height - 50, f"Счёт-фактура для заказа #{order.id}")

    p.setFont("Roboto", 11)
    p.drawString(50, height - 80, f"Покупатель: {order.user.get_full_name() or order.user.username}")
    p.drawString(50, height - 100, f"Email: {order.user.email}")
    p.drawString(50, height - 120, f"Адрес доставки: {order.delivery_address}")
    p.drawString(50, height - 150, f"Дата заказа: {order.order_date.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(350, height - 150, f"Статус: {order.get_status_display()}")

    y = height - 180
    p.setFont("Roboto", 12)
    p.drawString(50, y, "Товары в заказе:")
    y -= 20
    p.setFont("Roboto", 10)

    items = OrderItem.objects.filter(order=order).select_related('painting')
    for item in items:
        if y < 100:
            p.showPage()
            p.setFont("Roboto", 10)
            y = height - 100

        painting_title = item.painting.title
        price = f"{item.price_at_purchase:.2f} ₽"
        purchased_at = item.purchased_at.strftime('%Y-%m-%d %H:%M')
        p.drawString(50, y, painting_title)
        p.drawString(250, y, price)
        p.drawString(400, y, purchased_at)
        y -= 50

    if y < 80:
        p.showPage()
        y = height - 50
    p.setFont("Roboto", 12)
    p.drawString(50, y, f"Общая сумма товаров: {order.total_amount:.2f}")

    p.showPage()
    p.save()
    return response

generate_orders_pdf.short_description = "Скачать PDF для первого выбранного заказа"

# 1. Определяем форму для Order с кастомным M2M-полем
class OrderForm(forms.ModelForm):
    paintings = forms.ModelMultipleChoiceField(
        queryset=Painting.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Картины в заказе', is_stacked=False),
        label='Картины в заказе'
    )

    class Meta:
        model = Order
        fields = ['user', 'total_amount', 'status', 'delivery_address', 'paintings']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # при редактировании подставляем уже связанные картины
            self.fields['paintings'].initial = self.instance.paintings.all()

    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            order.save()
        selected = self.cleaned_data['paintings']
        # удалить лишние элементы OrderItem
        OrderItem.objects.filter(order=order).exclude(painting__in=selected).delete()
        # добавить новые
        existing = set(order.paintings.values_list('pk', flat=True))
        for painting in selected:
            if painting.pk not in existing:
                OrderItem.objects.create(
                    order=order,
                    painting=painting,
                    price_at_purchase=painting.price
                )
        return order

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('purchased_at', 'price_at_purchase')
    raw_id_fields = ('painting',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ('id', 'user', 'order_date', 'total_amount', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'id')
    date_hierarchy = 'order_date'
    raw_id_fields = ('user',)
    inlines = []
    actions = ['mark_shipped', generate_orders_pdf]

    @admin.action(description='Отметить как отправленные')
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"Отмечено как отправленные: {updated}")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'painting', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'painting__title')
    date_hierarchy = 'added_at'
    raw_id_fields = ('user', 'painting')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'painting', 'price_at_purchase', 'purchased_at')
    list_filter = ('purchased_at',)
    search_fields = ('order__id', 'painting__title')
    date_hierarchy = 'purchased_at'
    raw_id_fields = ('order', 'painting')
    readonly_fields = ('purchased_at', 'price_at_purchase')
