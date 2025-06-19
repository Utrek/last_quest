from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Supplier, Category, Product, Order, OrderItem, 
    CartItem, DeliveryAddress
)
from .admin_views import get_admin_urls

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'description')
    search_fields = ('user__username', 'user__company_name')
    
    def company_name(self, obj):
        return obj.user.company_name

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier_name', 'category', 'price', 'stock', 'is_active', 'image_preview')
    list_filter = ('is_active', 'category', 'supplier')
    search_fields = ('name', 'description', 'sku')
    readonly_fields = ('image_preview',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'sku')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Связи', {
            'fields': ('supplier', 'category')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview')
        }),
        ('Характеристики', {
            'fields': ('characteristics',)
        }),
    )
    
    # Добавляем кнопку импорта в админку
    change_list_template = 'admin/shop/product_change_list.html'
    
    # Переопределяем get_urls для добавления URL-шаблонов
    def get_urls(self):
        urls = super().get_urls()
        return get_admin_urls(urls)()
    
    def supplier_name(self, obj):
        return obj.supplier.user.company_name or obj.supplier.user.username
    supplier_name.short_description = 'Поставщик'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Предпросмотр изображения'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Адрес доставки', {
            'fields': ('delivery_address',)
        }),
    )

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')

class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'recipient_name', 'city', 'is_default')
    list_filter = ('is_default', 'city')
    search_fields = ('user__username', 'recipient_name', 'address', 'city')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        ('Личная информация', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'address')
        }),
        ('Тип пользователя', {
            'fields': ('user_type', 'company_name', 'is_accepting_orders')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )

# Регистрация моделей в админке
admin.site.register(User, UserAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)