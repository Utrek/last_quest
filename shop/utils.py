import yaml
from .models import Product, Supplier, Category

def export_products_to_yaml(supplier, filename=None):
    """
    Экспортирует товары поставщика в YAML файл
    
    Args:
        supplier: объект Supplier
        filename: путь к файлу для сохранения (если None, возвращает строку)
    
    Returns:
        str: YAML строка, если filename=None
    """
    products = Product.objects.filter(supplier=supplier)
    
    # Создаем структуру данных для экспорта
    data = {
        'shop': supplier.user.company_name or supplier.user.username,
        'categories': [],
        'goods': []
    }
    
    # Добавляем категории
    categories = {}
    for product in products:
        if product.category and product.category.id not in categories:
            categories[product.category.id] = product.category.name
    
    for cat_id, cat_name in categories.items():
        data['categories'].append({
            'id': cat_id,
            'name': cat_name
        })
    
    # Добавляем товары
    for product in products:
        product_data = {
            'id': product.sku or str(product.id),
            'category': product.category.id if product.category else None,
            'name': product.name,
            'price': float(product.price),
            'quantity': product.stock,
            'parameters': {
                'description': product.description
            }
        }
        data['goods'].append(product_data)
    
    yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False)
    
    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yaml_data)
        return f"Экспортировано {len(data['goods'])} товаров в {filename}"
    else:
        return yaml_data

def import_products_from_yaml(supplier, yaml_data=None, filename=None):
    """
    Импортирует товары из YAML файла или строки
    
    Args:
        supplier: объект Supplier
        yaml_data: строка с YAML данными (если None, читает из filename)
        filename: путь к файлу для чтения (если yaml_data=None)
    
    Returns:
        tuple: (количество созданных товаров, количество обновленных товаров)
    """
    if yaml_data is None and filename:
        with open(filename, 'r', encoding='utf-8') as f:
            yaml_data = f.read()
    
    if not yaml_data:
        raise ValueError("Необходимо указать yaml_data или filename")
    
    data = yaml.safe_load(yaml_data)
    
    created_count = 0
    updated_count = 0
    
    # Создаем словарь категорий
    categories_dict = {}
    if 'categories' in data:
        for cat_data in data['categories']:
            cat_name = cat_data.get('name', 'Без категории')
            cat_id = cat_data.get('id')
            if cat_id and cat_name:
                category, _ = Category.objects.get_or_create(name=cat_name)
                categories_dict[cat_id] = category
    
    # Импортируем товары
    if 'goods' in data:
        for item in data['goods']:
            try:
                # Получаем основные данные
                name = item.get('name')
                price = item.get('price')
                
                if not name or not price:
                    continue
                
                # Получаем категорию
                category = None
                cat_id = item.get('category')
                if cat_id and cat_id in categories_dict:
                    category = categories_dict[cat_id]
                
                # Получаем описание
                description = ""
                if 'parameters' in item and isinstance(item['parameters'], dict):
                    params = []
                    for key, value in item['parameters'].items():
                        params.append(f"{key}: {value}")
                    description = "\n".join(params)
                
                # Получаем или создаем SKU
                sku = str(item.get('id', ''))
                
                # Проверяем, существует ли товар с таким SKU
                if sku:
                    product, created = Product.objects.update_or_create(
                        sku=sku,
                        defaults={
                            'name': name,
                            'description': description,
                            'price': price,
                            'supplier': supplier,
                            'category': category,
                            'stock': item.get('quantity', 0),
                            'is_active': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                else:
                    # Создаем новый товар без SKU
                    Product.objects.create(
                        name=name,
                        description=description,
                        price=price,
                        supplier=supplier,
                        category=category,
                        stock=item.get('quantity', 0),
                        is_active=True
                    )
                    created_count += 1
            except Exception as e:
                print(f"Ошибка при импорте товара: {e}")
                continue
    
    return created_count, updated_count