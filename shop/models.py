from django.db import models
from django.contrib.auth.models import AbstractUser

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
    
    def is_supplier(self):
        return self.user_type == 'supplier'


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='suppliers/', blank=True, null=True)
    
    def __str__(self):
        return self.user.company_name or self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', db_index=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Уникальный идентификатор товара", db_index=True)
    
    def __str__(self):
        return self.name
        
    def to_dict(self):
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
    def from_dict(cls, data, supplier):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses')
    name = models.CharField(max_length=100, help_text="Название адреса (например, 'Дом', 'Работа')")
    recipient_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"
        
    def get_status_display(self):
        """Возвращает отображаемое значение статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена на момент заказа
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Сохраняем цену товара на момент заказа
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['user', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} в корзине {self.user.username}"