from django.contrib import admin
from .models import Cart, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('purchased_at', 'price_at_purchase')
    raw_id_fields = ('painting',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'total_amount', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'id')
    date_hierarchy = 'order_date'
    raw_id_fields = ('user',)
    inlines = [OrderItemInline]
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
