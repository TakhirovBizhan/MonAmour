from django.contrib import admin

from .models import Cart, Order, OrderItem
from store.models import Painting

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

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
    actions = ['mark_shipped']

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
