import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from shop.utils import export_products_to_yaml, export_products_to_file, import_products_from_yaml
from .factories import SupplierFactory, ProductFactory, CategoryFactory


@pytest.mark.django_db
class TestExportUtils:
    def test_export_products_to_yaml(self):
        # Создаем поставщика и товары
        supplier = SupplierFactory()
        category = CategoryFactory(name='Test Category')
        product1 = ProductFactory(
            supplier=supplier,
            category=category,
            name='Product 1',
            price=99.99,
            stock=10,
            sku='SKU-001'
        )
        product2 = ProductFactory(
            supplier=supplier,
            category=category,
            name='Product 2',
            price=199.99,
            stock=20,
            sku='SKU-002'
        )

        # Экспортируем товары в YAML
        yaml_data = export_products_to_yaml(supplier)

        # Проверяем, что YAML содержит информацию о товарах
        assert 'shop:' in yaml_data
        assert 'categories:' in yaml_data
        assert 'goods:' in yaml_data
        assert 'Product 1' in yaml_data
        assert 'Product 2' in yaml_data
        assert 'SKU-001' in yaml_data
        assert 'SKU-002' in yaml_data
        assert '99.99' in yaml_data
        assert '199.99' in yaml_data

        # Экспортируем товары в файл
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
            result = export_products_to_yaml(supplier, temp_file.name)

            # Проверяем результат
            assert 'Экспортировано 2 товаров' in result

            # Проверяем, что файл создан и содержит данные
            with open(temp_file.name, 'r') as f:
                file_content = f.read()
                assert 'Product 1' in file_content
                assert 'Product 2' in file_content

        # Удаляем временный файл
        os.unlink(temp_file.name)

    @patch('shop.utils.export_products_to_yaml')
    def test_export_products_to_file(self, mock_export):
        # Настраиваем мок
        mock_export.return_value = 'YAML content'

        # Создаем поставщика
        supplier = SupplierFactory(user__company_name='Test Company')

        # Экспортируем товары в файл
        with patch('shop.utils.open', MagicMock()) as mock_open:
            filename = export_products_to_file(supplier)

            # Проверяем, что функция export_products_to_yaml была вызвана
            mock_export.assert_called_once_with(supplier)

            # Проверяем, что файл был открыт для записи
            mock_open.assert_called_once()

            # Проверяем имя файла
            assert 'Test_Company_products.yaml' in filename


@pytest.mark.django_db
class TestImportUtils:
    def test_import_products_from_yaml(self):
        # Создаем поставщика
        supplier = SupplierFactory()

        # Создаем YAML данные
        yaml_data = """
        shop: Test Shop
        categories:
          - id: 1
            name: Electronics
          - id: 2
            name: Clothing
        goods:
          - id: SKU-001
            name: Test Product 1
            price: 99.99
            category: 1
            quantity: 10
            parameters:
              description: Test Description 1
          - id: SKU-002
            name: Test Product 2
            price: 199.99
            category: 2
            quantity: 20
            parameters:
              description: Test Description 2
        """

        # Импортируем товары из YAML
        created, updated = import_products_from_yaml(supplier, yaml_data=yaml_data)

        # Проверяем результат
        assert created == 2
        assert updated == 0

        # Проверяем, что товары были созданы
        from shop.models import Product, Category
        assert Product.objects.filter(supplier=supplier).count() == 2
        assert Category.objects.count() == 2

        # Проверяем данные первого товара
        product1 = Product.objects.get(sku='SKU-001')
        assert product1.name == 'Test Product 1'
        assert float(product1.price) == 99.99
        assert product1.stock == 10
        assert product1.category.name == 'Electronics'

        # Проверяем данные второго товара
        product2 = Product.objects.get(sku='SKU-002')
        assert product2.name == 'Test Product 2'
        assert float(product2.price) == 199.99
        assert product2.stock == 20
        assert product2.category.name == 'Clothing'

        # Обновляем данные первого товара
        yaml_data_update = """
        shop: Test Shop
        goods:
          - id: SKU-001
            name: Updated Product 1
            price: 149.99
            category: 1
            quantity: 15
            parameters:
              description: Updated Description 1
        """

        # Импортируем обновленные данные
        created, updated = import_products_from_yaml(supplier, yaml_data=yaml_data_update)

        # Проверяем результат
        assert created == 0
        assert updated == 1

        # Проверяем, что товар был обновлен
        product1.refresh_from_db()
        assert product1.name == 'Updated Product 1'
        assert float(product1.price) == 149.99
        assert product1.stock == 15
