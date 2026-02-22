from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PickupPoint, Product, Order, OrderItem

admin.site.register(User, UserAdmin)

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ('address',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'price', 'stock', 'discount')
    search_fields = ('sku', 'name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'status', 'client')
    inlines = [OrderItemInline]
