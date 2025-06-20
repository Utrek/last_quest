import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from shop.models import User, Supplier, DeliveryAddress, Order, CartItem
from .factories import (
    UserFactory, ProductFactory,
    DeliveryAddressFactory, CartItemFactory
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestRegisterView:
    def test_register_customer(self, api_client):
        url = reverse('register')
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

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']

        # Проверяем, что пользователь создан
        user = User.objects.get(email=data['email'])
        assert user.username == data['username']
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.user_type == 'customer'
        assert user.is_supplier() is False

    def test_register_supplier(self, api_client):
        url = reverse('register')
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

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']

        # Проверяем, что пользователь создан
        user = User.objects.get(email=data['email'])
        assert user.username == data['username']
        assert user.first_name == data['first_name']
        assert user.last_name == data['last_name']
        assert user.user_type == 'supplier'
        assert user.company_name == data['company_name']
        assert user.is_supplier() is True

        # Проверяем, что профиль поставщика создан
        supplier = Supplier.objects.get(user=user)
        assert supplier is not None


@pytest.mark.django_db
class TestLoginView:
    def test_login_with_email(self, api_client):
        # Создаем пользователя
        user = UserFactory(email='test@example.com')
        user.set_password('password123')
        user.save()

        # Входим в систему
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = api_client.post(url, data, format='json')

        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == user.email

    def test_login_with_invalid_credentials(self, api_client):
        # Создаем пользователя
        user = UserFactory(email='test@example.com')
        user.set_password('password123')
        user.save()

        # Пытаемся войти с неверным паролем
        url = reverse('login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post(url, data, format='json')

        # Проверяем ответ
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data


@pytest.mark.django_db
class TestDeliveryAddressView:
    def test_create_address(self):
        # Создаем пользователя и аутентифицируем его
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Создаем адрес доставки
        url = reverse('addresses-list')
        data = {
            'name': 'Home',
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

        response = client.post(url, data, format='json')

        # Проверяем ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['city'] == data['city']
        assert response.data['is_default'] is True

        # Проверяем, что адрес создан
        address = DeliveryAddress.objects.get(id=response.data['id'])
        assert address.user == user
        assert address.name == data['name']
        assert address.city == data['city']
        assert address.is_default is True

        # Создаем второй адрес
        data['name'] = 'Work'
        data['is_default'] = True
        response = client.post(url, data, format='json')

        # Проверяем, что второй адрес стал адресом по умолчанию
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_default'] is True

        # Проверяем, что первый адрес больше не является адресом по умолчанию
        address.refresh_from_db()
        assert address.is_default is False


@pytest.mark.django_db
class TestOrderConfirmationView:
    def test_confirm_order(self):
        # Создаем пользователя и аутентифицируем его
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)

        # Создаем адрес доставки
        address = DeliveryAddressFactory(user=user)

        # Создаем товары и добавляем их в корзину
        product1 = ProductFactory(stock=10)
        product2 = ProductFactory(stock=20)

        cart_item1 = CartItemFactory(user=user, product=product1, quantity=2)
        cart_item2 = CartItemFactory(user=user, product=product2, quantity=3)

        # Подтверждаем заказ
        url = reverse('order-confirmation-confirm')
        data = {
            'delivery_address_id': address.id
        }

        response = client.post(url, data, format='json')

        # Проверяем ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order' in response.data

        # Проверяем, что заказ создан
        order_id = response.data['order']['id']
        order = Order.objects.get(id=order_id)
        assert order.user == user
        assert order.delivery_address == address
        assert order.status == 'pending'

        # Проверяем, что товары добавлены в заказ
        assert order.items.count() == 2

        # Проверяем, что количество товаров уменьшилось
        product1.refresh_from_db()
        product2.refresh_from_db()
        assert product1.stock == 8
        assert product2.stock == 17

        # Проверяем, что корзина очищена
        assert not CartItem.objects.filter(user=user).exists()
