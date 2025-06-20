import yaml
import os
import re
from django.conf import settings
from typing import Optional, Tuple
from .models import Product, Supplier, Category

def export_products_to_yaml(supplier: Supplier, filename: Optional[str] = None) -> str:
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
        # Добавляем характеристики, если они есть
        parameters = {'description': product.description}
        if hasattr(product, 'characteristics') and product.characteristics:
            parameters.update(product.characteristics)
            
        product_data = {
            'id': product.sku or str(product.id),
            'category': product.category.id if product.category else None,
            'name': product.name,
            'price': float(product.price),
            'quantity': product.stock,
            'parameters': parameters
        }
        data['goods'].append(product_data)
    
    yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False)
    
    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yaml_data)
        return f"Экспортировано {len(data['goods'])} товаров в {filename}"
    else:
        return yaml_data

def export_products_to_file(supplier: Supplier) -> str:
    """
    Экспортирует товары поставщика в YAML файл в директории media/exports
    
    Args:
        supplier: объект Supplier
    
    Returns:
        str: путь к созданному файлу
    """
    # Используем директорию media, которая должна быть доступна для записи
    export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
    
    try:
        # Создаем директорию для экспорта, если ее нет
        os.makedirs(export_dir, exist_ok=True)
        
        # Создаем безопасное имя файла из названия компании 
    # или имени пользователя
        company_name = supplier.user.company_name or supplier.user.username
        safe_filename = re.sub(r'[^\w\-_\.]', '_', company_name)
        filename = os.path.join(export_dir, f"{safe_filename}_products.yaml")
        
        # Получаем данные для экспорта
        yaml_data = export_products_to_yaml(supplier)
        
        # Записываем данные в файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yaml_data)
        
        return filename
    except Exception as e:
        # В случае ошибки используем временную директорию
        import tempfile
        export_dir = tempfile.gettempdir()
        safe_filename = re.sub(r'[^\w\-_\.]', '_', supplier.user.username)
        filename = os.path.join(export_dir, f"{safe_filename}_products.yaml")
        
        # Получаем данные для экспорта
        yaml_data = export_products_to_yaml(supplier)
        
        # Записываем данные в файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(yaml_data)
        
        return filename

def import_products_from_yaml(supplier: Supplier, yaml_data: Optional[str] = None,
                             filename: Optional[str] = None) -> Tuple[int, int]:
    """
    Импортирует товары из YAML файла или строки
    
    Args:
        supplier: объект Supplier
        yaml_data: строка с YAML данными (если None, читает из filename)
        filename: путь к файлу для чтения (если yaml_data=None)
    
    Returns:
        tuple: (количество созданных товаров, 
                количество обновленных товаров)
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
                
                # Получаем описание и характеристики
                description = ""
                characteristics = {}
                if 'parameters' in item and isinstance(item['parameters'], dict):
                    # Сохраняем описание отдельно
                    if 'description' in item['parameters']:
                        description = item['parameters']['description']
                        # Удаляем описание из характеристик
                        parameters = item['parameters'].copy()
                        parameters.pop('description', None)
                        characteristics = parameters
                    else:
                        # Если нет отдельного описания, 
                        # создаем его из параметров
                        params = []
                        for key, value in item['parameters'].items():
                            params.append(f"{key}: {value}")
                        description = "\n".join(params)
                        characteristics = item['parameters']
                
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
                            'is_active': True,
                            'characteristics': characteristics
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
                        is_active=True,
                        characteristics=characteristics
                    )
                    created_count += 1
            except Exception as e:
                print(f"Ошибка при импорте товара: {e}")
                continue
    
    return created_count, updated_count