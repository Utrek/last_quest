from django.contrib import admin
from .models import User, Supplier, Category, Product, Order, OrderItem, CartItem

# Регистрация моделей в админке
admin.site.register(User)
admin.site.register(Supplier)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)