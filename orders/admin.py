from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity', 'get_cost')
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipping_name', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('shipping_name', 'shipping_dni', 'id')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Información de Venta', {'fields': ('user', 'status', 'total_amount')}),
        ('Datos de Envío', {'fields': ('shipping_name', 'shipping_dni', 'shipping_phone', 'shipping_address', 'shipping_city', 'shipping_district', 'shipping_reference')}),
        ('Datos de Facturación', {'fields': ('billing_name', 'billing_id_number', 'billing_address')}),
    )

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at', 'get_total_items')
    inlines = [CartItemInline]

    def get_total_items(self, obj):
        return obj.items.count()
    get_total_items.short_description = 'Productos en Carrito'