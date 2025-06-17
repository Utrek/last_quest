from django.db import models
from django.contrib.auth.models import AbstractUser
from typing import Dict, Any, Optional, Union, List, Tuple, cast
from decimal import Decimal

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Клиент'),
        ('supplier', 'Поставщик'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Поля для поставщика
    company_name = models.CharField(max_length=100, blank=True, null=True)
    is_accepting_orders = models.BooleanField(default=True)
    
    def is_supplier(self) -> bool:
        return self.user_type == 'supplier'


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile', verbose_name="Пользователь")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    logo = models.ImageField(upload_to='suppliers/', blank=True, null=True, verbose_name="Логотип")
    
    def __str__(self):
        return self.user.company_name or self.user.username
        
    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ['user__company_name', 'user__username']


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True, verbose_name="Цена")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products', verbose_name="Поставщик")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', db_index=True, verbose_name="Категория")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Активен")
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Уникальный идентификатор товара", db_index=True, verbose_name="Артикул")
    characteristics = models.JSONField(blank=True, null=True, default=dict, verbose_name="Характеристики")
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['name']
    
    def __str__(self):
        return self.name
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект товара в словарь для экспорта"""
        return {
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'category': self.category.name if self.category else None,
            'stock': self.stock,
            'is_active': self.is_active,
            'supplier': self.supplier.user.username
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], supplier: 'Supplier') -> 'Product':
        """Создает или обновляет товар из словаря"""
        category, _ = Category.objects.get_or_create(name=data.get('category', 'Без категории'))
        
        # Ищем товар по SKU или создаем новый
        if data.get('sku'):
            product, created = cls.objects.update_or_create(
                sku=data['sku'],
                defaults={
                    'name': data['name'],
                    'description': data.get('description', ''),
                    'price': data['price'],
                    'supplier': supplier,
                    'category': category,
                    'stock': data.get('stock', 0),
                    'is_active': data.get('is_active', True)
                }
            )
        else:
            product = cls.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                supplier=supplier,
                category=category,
                stock=data.get('stock', 0),
                is_active=data.get('is_active', True)
            )
        
        return product


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses', verbose_name="Пользователь")
    name = models.CharField(max_length=100, help_text="Название адреса (например, 'Дом', 'Работа')", verbose_name="Название")
    
    # Контактная информация
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    recipient_name = models.CharField(max_length=100, verbose_name="Имя получателя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=15, verbose_name="Телефон")
    
    # Адрес
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house = models.CharField(max_length=20, verbose_name="Дом")
    building = models.CharField(max_length=20, blank=True, null=True, verbose_name="Корпус")
    structure = models.CharField(max_length=20, blank=True, null=True, verbose_name="Строение")
    apartment = models.CharField(max_length=20, blank=True, null=True, verbose_name="Квартира")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    
    address = models.TextField(verbose_name="Полный адрес")
    is_default = models.BooleanField(default=False, verbose_name="Адрес по умолчанию")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def save(self, *args, **kwargs):
        # Формируем полный адрес
        address_parts = [
            f"г. {self.city}",
            f"ул. {self.street}",
            f"д. {self.house}"
        ]
        
        if self.building:
            address_parts.append(f"корп. {self.building}")
        if self.structure:
            address_parts.append(f"стр. {self.structure}")
        if self.apartment:
            address_parts.append(f"кв. {self.apartment}")
            
        self.address = ", ".join(address_parts)
        
        # Если этот адрес установлен как адрес по умолчанию, сбрасываем флаг у других адресов
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # Если это первый адрес пользователя, устанавливаем его как адрес по умолчанию
        elif not self.pk and not DeliveryAddress.objects.filter(user=self.user).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name}: {self.address}, {self.city}"
        
    class Meta:
        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"
    
    def __str__(self):
        return f"{self.name}: {self.address}, {self.city}"
    
    def save(self, *args, **kwargs):
        # Если этот адрес установлен как адрес по умолчанию, сбрасываем флаг у других адресов
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        # Если это первый адрес пользователя, устанавливаем его как адрес по умолчанию
        elif not self.pk and not DeliveryAddress.objects.filter(user=self.user).exists():
            self.is_default = True
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Общая сумма")
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"
        
    def get_status_display(self):
        """Возвращает отображаемое значение статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"
        
    def get_status_display(self):
        """Возвращает отображаемое значение статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")  # Цена на момент заказа
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Сохраняем цену товара на момент заказа
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        
    @property
    def total_price(self):
        return self.quantity * self.price
        
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items', verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} в корзине {self.user.username}"
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
    
    @property
    def shop_name(self):
        return self.product.supplier.user.company_name or self.product.supplier.user.username
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['user', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} в корзине {self.user.username}"