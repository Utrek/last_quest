import pytest
from unittest.mock import patch, MagicMock

from shop.tasks import (
    send_email, send_order_confirmation_email,
    send_supplier_order_notification, do_import
)
from .factories import (
    UserFactory, SupplierFactory, ProductFactory,
    OrderFactory, OrderItemFactory
)

@pytest.mark.django_db
class TestEmailTasks:
    @patch('shop.tasks.EmailMultiAlternatives')
    def test_send_email(self, mock_email):
        # Настраиваем мок
        mock_instance = MagicMock()
        mock_email.return_value = mock_instance
        
        # Вызываем задачу
        result = send_email(
            subject='Test Subject',
            text_content='Test Content',
            from_email='from@example.com',
            recipient_list=['to@example.com'],
            html_content='<p>Test HTML Content</p>'
        )
        
        # Проверяем, что email был отправлен
        mock_email.assert_called_once_with(
            'Test Subject', 'Test Content', 'from@example.com', ['to@example.com']
        )
        mock_instance.attach_alternative.assert_called_once_with(
            '<p>Test HTML Content</p>', 'text/html'
        )
        mock_instance.send.assert_called_once()
        assert result is True

    @patch('shop.tasks.send_email')
    def test_send_order_confirmation_email(self, mock_send_email):
        # Настраиваем мок
        mock_send_email.delay.return_value.get.return_value = True
        
        # Создаем заказ
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user)
        
        # Вызываем задачу
        result = send_order_confirmation_email(order.id)
        
        # Проверяем, что задача send_email была вызвана
        mock_send_email.delay.assert_called_once()
        args, kwargs = mock_send_email.delay.call_args
        assert f'Подтверждение заказа #{order.id}' in args[0]  # subject - первый аргумент
        assert user.email in args[3]  # recipient_list - четвертый аргумент
        assert result is True

    @patch('shop.tasks.send_email')
    def test_send_supplier_order_notification(self, mock_send_email):
        # Настраиваем мок
        mock_send_email.delay.return_value = MagicMock()
        
        # Создаем заказ с товарами от поставщика
        supplier_user = UserFactory(email='supplier@example.com', user_type='supplier')
        supplier = SupplierFactory(user=supplier_user)
        product = ProductFactory(supplier=supplier)
        order = OrderFactory()
        order_item = OrderItemFactory(order=order, product=product)
        
        # Вызываем задачу
        result = send_supplier_order_notification(order.id)
        
        # Проверяем, что задача send_email была вызвана
        mock_send_email.delay.assert_called_once()
        assert result is True

@pytest.mark.django_db
class TestImportTask:
    def test_do_import(self):
        # Создаем поставщика
        supplier = SupplierFactory()
        
        # Создаем данные для импорта
        yaml_data = """
        shop: Test Shop
        categories:
          - id: 1
            name: Electronics
          - id: 2
            name: Clothing
        goods:
          - id: SKU-001
            name: Test Product
            price: 99.99
            category: 1
            quantity: 10
            parameters:
              description: Test Description
              color: red
              size: M
        """
        
        # Вызываем задачу
        result = do_import(supplier.id, yaml_data=yaml_data)
        
        # Проверяем результат
        assert result['success'] is True
        assert result['created'] == 1
        assert result['updated'] == 0
        assert result['total'] == 1
        
        # Проверяем, что товар был создан
        from shop.models import Product
        product = Product.objects.get(sku='SKU-001')
        assert product.name == 'Test Product'
        assert float(product.price) == 99.99
        assert product.stock == 10
        assert product.supplier == supplier
        assert product.category.name == 'Electronics'
        assert product.characteristics == {'color': 'red', 'size': 'M'}