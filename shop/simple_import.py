import yaml
import os
from django.conf import settings
from .models import Product, Category, Supplier


def simple_import_from_yaml(supplier_user):
    """
    Простая функция для импорта товаров из YAML файла
    """
    # Получаем профиль поставщика
    try:
        supplier = Supplier.objects.get(user=supplier_user)
    except Supplier.DoesNotExist:
        return {"error": "Профиль поставщика не найден"}

    # Путь к файлу shop1.yaml
    yaml_file = os.path.join(settings.BASE_DIR, 'shop1.yaml')

    if not os.path.exists(yaml_file):
        return {"error": f"Файл {yaml_file} не найден"}

    # Чтение файла
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
    except Exception as e:
        return {"error": f"Ошибка чтения файла: {str(e)}"}

    # Парсинг YAML
    try:
        data = yaml.safe_load(yaml_content)
    except Exception as e:
        return {"error": f"Ошибка парсинга YAML: {str(e)}"}

    # Проверка структуры данных
    if not isinstance(data, dict) or 'goods' not in data:
        return {"error": "Неверный формат YAML файла"}

    # Создание категорий
    categories = {}
    if 'categories' in data:
        for cat_data in data['categories']:
            try:
                cat_name = cat_data.get('name', 'Без категории')
                cat_id = cat_data.get('id')
                if cat_id is not None and cat_name:
                    category, _ = Category.objects.get_or_create(name=cat_name)
                    categories[cat_id] = category
            except Exception as e:
                print(f"Ошибка при создании категории: {str(e)}")

    # Импорт товаров
    created_count = 0
    updated_count = 0
    errors = []

    for item in data['goods']:
        try:
            # Получаем основные данные
            name = item.get('name')
            if not name:
                continue

            # Цена
            price = item.get('price', 0)
            if not isinstance(price, (int, float)):
                price = 0

            # Категория
            category = None
            cat_id = item.get('category')
            if cat_id is not None and cat_id in categories:
                category = categories[cat_id]

            # Описание
            description = ""
            if 'parameters' in item and isinstance(item['parameters'], dict):
                description = str(item['parameters'])

            # Количество
            quantity = item.get('quantity', 0)
            if not isinstance(quantity, int):
                quantity = 0

            # Создаем товар
            product = Product(
                name=name,
                description=description,
                price=price,
                supplier=supplier,
                category=category,
                stock=quantity,
                is_active=True
            )

            # Устанавливаем SKU, если есть
            if 'id' in item:
                product.sku = str(item['id'])

            product.save()
            created_count += 1

        except Exception as e:
            errors.append(f"Ошибка при импорте товара {item.get('name', 'Unknown')}: {str(e)}")

    result = {
        "created": created_count,
        "updated": updated_count,
        "message": (
            f"Импортировано товаров: {created_count} создано, "
            f"{updated_count} обновлено"
        )
    }

    if errors:
        result["errors"] = errors

    return result
