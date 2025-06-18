import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from shop.models import (
    Supplier, Category, Product, DeliveryAddress, Order, OrderItem, CartItem
)
from .factories import (
    UserFactory, SupplierFactory, CategoryFactory, ProductFactory,
    DeliveryAddressFactory, OrderFactory, OrderItemFactory, CartItemFactory
)

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = UserFactory()
        assert user.pk is not None
        assert user.user_type == 'customer'
        assert user.is_supplier() is False

    def test_create_supplier_user(self):
        user = UserFactory(user_type='supplier')
        assert user.pk is not None
        assert user.user_type == 'supplier'
        assert user.is_supplier() is True

@pytest.mark.django_db
class TestSupplierModel:
    def test_create_supplier(self):
        supplier = SupplierFactory()
        assert supplier.pk is not None
        assert supplier.user.user_type == 'supplier'
        assert supplier.user.is_supplier() is True
        assert str(supplier) == supplier.user.company_name or supplier.user.username

@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        category = CategoryFactory()
        assert category.pk is not None
        assert str(category) == category.name

@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self):
        product = ProductFactory()
        assert product.pk is not None
        assert str(product) == product.name
        assert product.price == Decimal('99.99')
        assert product.stock == 100
        assert product.is_active is True

    def test_product_to_dict(self):
        product = ProductFactory()
        product_dict = product.to_dict()
        assert product_dict['name'] == product.name
        assert product_dict['description'] == product.description
        assert product_dict['price'] == float(product.price)
        assert product_dict['category'] == product.category.name
        assert product_dict['stock'] == product.stock
        assert product_dict['is_active'] == product.is_active
        assert product_dict['supplier'] == product.supplier.user.username

    def test_product_from_dict(self):
        supplier = SupplierFactory()
        category = CategoryFactory()
        
        product_data = {
            'name': 'Test Product',
            'description': 'Test Description',
            'price': 199.99,
            'category': category.name,
            'stock': 50,
            'is_active': True,
            'sku': 'TEST-SKU-123'
        }
        
        product = Product.from_dict(product_data, supplier)
        assert product.pk is not None
        assert product.name == product_data['name']
        assert product.description == product_data['description']
        assert product.price == Decimal('199.99')
        assert product.category.name == category.name
        assert product.stock == product_data['stock']
        assert product.is_active == product_data['is_active']
        assert product.sku == product_data['sku']
        assert product.supplier == supplier

@pytest.mark.django_db
class TestDeliveryAddressModel:
    def test_create_delivery_address(self):
        address = DeliveryAddressFactory()
        assert address.pk is not None
        assert address.address is not None  # Проверяем, что адрес был сформирован
        assert str(address) == f"{address.name}: {address.address}, {address.city}"

    def test_default_address(self):
        user = UserFactory()
        # Создаем первый адрес - он должен стать адресом по умолчанию
        address1 = DeliveryAddressFactory(user=user)
        assert address1.is_default is True
        
        # Создаем второй адрес - он не должен быть адресом по умолчанию
        address2 = DeliveryAddressFactory(user=user)
        assert address2.is_default is False
        
        # Устанавливаем второй адрес как адрес по умолчанию
        address2.is_default = True
        address2.save()
        
        # Перезагружаем первый адрес из базы данных
        address1.refresh_from_db()
        
        # Проверяем, что первый адрес больше не является адресом по умолчанию
        assert address1.is_default is False
        assert address2.is_default is True

@pytest.mark.django_db
class TestOrderModel:
    def test_create_order(self):
        order = OrderFactory()
        assert order.pk is not None
        assert order.status == 'pending'
        assert order.user is not None
        assert order.delivery_address is not None

    def test_order_with_items(self):
        order = OrderFactory()
        item1 = OrderItemFactory(order=order)
        item2 = OrderItemFactory(order=order)
        
        assert order.items.count() == 2
        assert item1.order == order
        assert item2.order == order

@pytest.mark.django_db
class TestCartItemModel:
    def test_create_cart_item(self):
        cart_item = CartItemFactory()
        assert cart_item.pk is not None
        assert cart_item.user is not None
        assert cart_item.product is not None
        assert cart_item.quantity == 1