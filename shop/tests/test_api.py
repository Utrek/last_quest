import pytest
import json
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from shop.models import Product, Category, Supplier, CartItem, Order, DeliveryAddress
from .factories import (
    UserFactory, SupplierFactory, CategoryFactory, ProductFactory,
    DeliveryAddressFactory, OrderFactory, OrderItemFactory, CartItemFactory
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user

@pytest.fixture
def supplier_client(api_client):
    supplier_user = UserFactory(user_type='supplier')
    supplier = SupplierFactory(user=supplier_user)
    api_client.force_authenticate(user=supplier_user)
    return api_client, supplier_user, supplier

@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, api_client):
        # Создаем несколько продуктов
        products = [ProductFactory() for _ in range(3)]
        
        # Получаем список продуктов через API
        url = reverse('products-list')
        response = api_client.get(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
        
        # Проверяем, что все созданные продукты присутствуют в ответе
        product_ids = [product.id for product in products]
        response_ids = [product['id'] for product in response.data['results']]
        assert set(product_ids) == set(response_ids)

    def test_filter_products_by_category(self, api_client):
        # Создаем категории и продукты
        category1 = CategoryFactory()
        category2 = CategoryFactory()
        
        product1 = ProductFactory(category=category1)
        product2 = ProductFactory(category=category1)
        product3 = ProductFactory(category=category2)
        
        # Фильтруем продукты по категории через API
        url = f"{reverse('products-list')}?category={category1.id}"
        response = api_client.get(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Проверяем, что в ответе только продукты из нужной категории
        response_ids = [product['id'] for product in response.data['results']]
        assert product1.id in response_ids
        assert product2.id in response_ids
        assert product3.id not in response_ids

    def test_search_products(self, api_client):
        # Создаем продукты с разными названиями
        product1 = ProductFactory(name="Apple iPhone")
        product2 = ProductFactory(name="Samsung Galaxy")
        product3 = ProductFactory(name="Apple MacBook")
        
        # Ищем продукты по названию через API
        url = f"{reverse('products-list')}?search=Apple"
        response = api_client.get(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Проверяем, что в ответе только продукты с "Apple" в названии
        response_ids = [product['id'] for product in response.data['results']]
        assert product1.id in response_ids
        assert product3.id in response_ids
        assert product2.id not in response_ids

@pytest.mark.django_db
class TestCartAPI:
    def test_add_to_cart(self, authenticated_client):
        client, user = authenticated_client
        product = ProductFactory()
        
        # Добавляем товар в корзину
        url = reverse('cart-list')
        data = {
            'product': product.id,
            'quantity': 2
        }
        response = client.post(url, data)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['product'] == product.id
        assert response.data['quantity'] == 2
        
        # Проверяем, что товар действительно добавлен в корзину
        cart_item = CartItem.objects.get(user=user, product=product)
        assert cart_item.quantity == 2

    def test_update_cart_quantity(self, authenticated_client):
        client, user = authenticated_client
        product = ProductFactory()
        cart_item = CartItemFactory(user=user, product=product, quantity=1)
        
        # Обновляем количество товара в корзине
        url = reverse('cart-update-quantity')
        data = {
            'product': product.id,
            'quantity': 3
        }
        response = client.post(url, data)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == 3
        
        # Проверяем, что количество товара действительно обновлено
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3

    def test_remove_from_cart(self, authenticated_client):
        client, user = authenticated_client
        product = ProductFactory()
        cart_item = CartItemFactory(user=user, product=product)
        
        # Удаляем товар из корзины
        url = reverse('cart-remove-product')
        data = {
            'product': product.id
        }
        response = client.post(url, data)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert 'success' in response.data
        
        # Проверяем, что товар действительно удален из корзины
        assert not CartItem.objects.filter(user=user, product=product).exists()

@pytest.mark.django_db
class TestOrderAPI:
    def test_create_order(self, authenticated_client):
        client, user = authenticated_client
        product = ProductFactory(stock=10)
        cart_item = CartItemFactory(user=user, product=product, quantity=2)
        address = DeliveryAddressFactory(user=user)
        
        # Создаем заказ
        url = reverse('cart-checkout')
        data = {
            'delivery_address_id': address.id
        }
        response = client.post(url, data)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert 'order' in response.data
        
        # Проверяем, что заказ создан
        order_id = response.data['order']['id']
        order = Order.objects.get(id=order_id)
        assert order.user == user
        assert order.delivery_address == address
        assert order.status == 'pending'
        
        # Проверяем, что товар добавлен в заказ
        assert order.items.count() == 1
        order_item = order.items.first()
        assert order_item.product == product
        assert order_item.quantity == 2
        
        # Проверяем, что количество товара уменьшилось
        product.refresh_from_db()
        assert product.stock == 8
        
        # Проверяем, что корзина очищена
        assert not CartItem.objects.filter(user=user).exists()

    def test_list_orders(self, authenticated_client):
        client, user = authenticated_client
        orders = [OrderFactory(user=user) for _ in range(3)]
        
        # Получаем список заказов
        url = reverse('orders-list')
        response = client.get(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        
        # Проверяем, что все созданные заказы присутствуют в ответе
        order_ids = [order.id for order in orders]
        response_ids = [order['id'] for order in response.data]
        assert set(order_ids) == set(response_ids)

    def test_cancel_order(self, authenticated_client):
        client, user = authenticated_client
        product = ProductFactory(stock=5)
        order = OrderFactory(user=user, status='pending')
        order_item = OrderItemFactory(order=order, product=product, quantity=2)
        
        initial_stock = product.stock
        
        # Отменяем заказ
        url = reverse('orders-cancel', args=[order.id])
        response = client.post(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert response.data['order']['status'] == 'cancelled'
        
        # Проверяем, что статус заказа изменился
        order.refresh_from_db()
        assert order.status == 'cancelled'
        
        # Проверяем, что товар вернулся на склад
        product.refresh_from_db()
        assert product.stock == initial_stock + order_item.quantity

@pytest.mark.django_db
class TestSupplierAPI:
    def test_supplier_products(self, supplier_client):
        client, user, supplier = supplier_client
        products = [ProductFactory(supplier=supplier) for _ in range(3)]
        
        # Получаем список товаров поставщика
        url = reverse('supplier-products-list')
        response = client.get(url)
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        
        # Проверяем, что все созданные товары присутствуют в ответе
        product_ids = [product.id for product in products]
        response_ids = [product['id'] for product in response.data]
        assert set(product_ids) == set(response_ids)

    def test_create_product(self, supplier_client):
        client, user, supplier = supplier_client
        category = CategoryFactory()
        
        # Создаем товар
        url = reverse('supplier-products-list')
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
        response = client.post(url, data, format='json')
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
        assert response.data['price'] == data['price']
        
        # Проверяем, что товар создан
        product_id = response.data['id']
        product = Product.objects.get(id=product_id)
        assert product.name == data['name']
        assert product.supplier == supplier
        assert product.characteristics == data['characteristics']

    def test_update_product(self, supplier_client):
        client, user, supplier = supplier_client
        product = ProductFactory(supplier=supplier)
        
        # Обновляем товар
        url = reverse('supplier-products-detail', args=[product.id])
        data = {
            'name': 'Updated Product',
            'price': '299.99'
        }
        response = client.patch(url, data, format='json')
        
        # Проверяем ответ
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == data['name']
        assert response.data['price'] == data['price']
        
        # Проверяем, что товар обновлен
        product.refresh_from_db()
        assert product.name == data['name']
        assert product.price == Decimal('299.99')