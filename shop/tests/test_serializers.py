import pytest
from django.contrib.auth import get_user_model
from shop.serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, ProductSerializer,
    OrderSerializer, CartItemSerializer, DeliveryAddressSerializer
)
from .factories import (
    UserFactory, SupplierFactory, CategoryFactory, ProductFactory,
    DeliveryAddressFactory, OrderFactory, OrderItemFactory, CartItemFactory
)

User = get_user_model()

@pytest.mark.django_db
class TestRegisterSerializer:
    def test_validate_passwords_match(self):
        # Проверяем, что пароли совпадают
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!'
        }
        serializer = RegisterSerializer(data=data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
        assert serializer.is_valid()
        
        # Проверяем, что пароли не совпадают
        data['password2'] = 'differentpassword'
        serializer = RegisterSerializer(data=data)
        is_invalid = not serializer.is_valid()
        if not is_invalid:
            print("Expected validation to fail but it passed")
        assert is_invalid

    def test_create_user(self):
        # Создаем пользователя через сериализатор
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+79001234567',
            'address': 'Test Address',
            'user_type': 'customer'
        }
        serializer = RegisterSerializer(data=data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == data['username']
        assert user.email == data['email']
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.phone == data['phone']
        assert user.address == data['address']
        assert user.user_type == data['user_type']
        assert user.check_password('TestPassword123!')

    def test_create_supplier(self):
        # Создаем поставщика через сериализатор
        data = {
            'username': 'supplier_test',
            'email': 'supplier_test@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'first_name': 'Supplier',
            'last_name': 'User',
            'phone': '+79009876543',
            'address': 'Supplier Address',
            'user_type': 'supplier',
            'company_name': 'Test Company'
        }
        serializer = RegisterSerializer(data=data)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.username == data['username']
        assert user.email == data['email']
        assert user.user_type == data['user_type']
        assert user.company_name == data['company_name']
        assert hasattr(user, 'supplier_profile')

@pytest.mark.django_db
class TestLoginSerializer:
    def test_validate(self):
        # Создаем пользователя
        user = UserFactory(email='test@example.com')
        user.set_password('password123')
        user.save()
        
        # Проверяем валидацию с правильными данными
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        
        # Проверяем валидацию с неправильным паролем
        data['password'] = 'wrongpassword'
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()  # Валидация проходит, но аутентификация будет неуспешной

@pytest.mark.django_db
class TestProductSerializer:
    def test_serialization(self):
        # Создаем продукт
        product = ProductFactory(
            name='Test Product',
            price=99.99,
            stock=10,
            characteristics={'color': 'red', 'size': 'M'}
        )
        
        # Сериализуем продукт
        serializer = ProductSerializer(product)
        data = serializer.data
        
        # Проверяем данные
        assert data['id'] == product.id
        assert data['name'] == product.name
        assert data['price'] == '99.99'
        assert data['stock'] == product.stock
        assert data['characteristics'] == product.characteristics
        assert 'supplier' in data
        assert 'category' in data

    def test_deserialization(self):
        # Создаем категорию и поставщика
        category = CategoryFactory()
        supplier = SupplierFactory()
        
        # Данные для создания продукта
        data = {
            'name': 'New Product',
            'description': 'Product Description',
            'price': '199.99',
            'category': category.id,
            'stock': 50,
            'is_active': True,
            'characteristics': {
                'color': 'blue',
                'size': 'L',
                'weight': '2kg'
            }
        }
        
        # Десериализуем данные
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid()
        
        # Сохраняем продукт
        product = serializer.save(supplier=supplier)
        
        # Проверяем данные
        assert product.name == data['name']
        assert product.description == data['description']
        assert str(product.price) == data['price']
        assert product.category.id == data['category']
        assert product.stock == data['stock']
        assert product.is_active == data['is_active']
        assert product.characteristics == data['characteristics']
        assert product.supplier == supplier

@pytest.mark.django_db
class TestOrderSerializer:
    def test_serialization(self):
        # Создаем заказ с товарами
        order = OrderFactory(status='pending')
        product1 = ProductFactory(price=99.99)
        product2 = ProductFactory(price=199.99)
        item1 = OrderItemFactory(order=order, product=product1, quantity=2, price=99.99)
        item2 = OrderItemFactory(order=order, product=product2, quantity=1, price=199.99)
        
        # Сериализуем заказ
        serializer = OrderSerializer(order)
        data = serializer.data
        
        # Проверяем данные
        assert data['id'] == order.id
        assert data['status'] == order.status
        assert 'items' in data
        assert len(data['items']) == 2
        assert data['items'][0]['product'] == product1.id
        assert data['items'][0]['quantity'] == 2
        assert data['items'][0]['price'] == '99.99'
        assert data['items'][1]['product'] == product2.id
        assert data['items'][1]['quantity'] == 1
        assert data['items'][1]['price'] == '199.99'
        assert data['total_amount'] == '399.97'  # 2*99.99 + 1*199.99

@pytest.mark.django_db
class TestCartItemSerializer:
    def test_serialization(self):
        # Создаем элемент корзины
        product = ProductFactory(name='Test Product', price=99.99)
        cart_item = CartItemFactory(product=product, quantity=3)
        
        # Сериализуем элемент корзины
        serializer = CartItemSerializer(cart_item)
        data = serializer.data
        
        # Проверяем данные
        assert data['id'] == cart_item.id
        assert data['product'] == product.id
        assert data['quantity'] == cart_item.quantity
        assert 'product_details' in data
        assert data['product_details']['name'] == product.name
        assert data['product_details']['price'] == '99.99'
        assert data['total_price'] == '299.97'  # 3*99.99

@pytest.mark.django_db
class TestDeliveryAddressSerializer:
    def test_serialization(self):
        # Создаем адрес доставки
        address = DeliveryAddressFactory(
            name='Home',
            city='Moscow',
            street='Main Street',
            house='10',
            is_default=True
        )
        
        # Сериализуем адрес
        serializer = DeliveryAddressSerializer(address)
        data = serializer.data
        
        # Проверяем данные
        assert data['id'] == address.id
        assert data['name'] == address.name
        assert data['city'] == address.city
        assert data['street'] == address.street
        assert data['house'] == address.house
        assert data['is_default'] == address.is_default
        assert 'address' in data  # Полный адрес

    def test_deserialization(self):
        # Создаем пользователя
        user = UserFactory()
        
        # Данные для создания адреса
        data = {
            'name': 'Work',
            'last_name': 'Doe',
            'first_name': 'John',
            'middle_name': 'Smith',
            'recipient_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+79001234567',
            'city': 'Moscow',
            'street': 'Main Street',
            'house': '10',
            'building': '1',
            'apartment': '101',
            'postal_code': '123456',
            'is_default': True
        }
        
        # Десериализуем данные
        serializer = DeliveryAddressSerializer(data=data)
        assert serializer.is_valid()
        
        # Сохраняем адрес
        address = serializer.save(user=user)
        
        # Проверяем данные
        assert address.name == data['name']
        assert address.last_name == data['last_name']
        assert address.first_name == data['first_name']
        assert address.city == data['city']
        assert address.street == data['street']
        assert address.house == data['house']
        assert address.is_default == data['is_default']
        assert address.user == user