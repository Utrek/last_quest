from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import Dict, Any, List, Optional, Union
import yaml
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email(subject: str, text_content: str, from_email: str, 
               recipient_list: List[str], html_content: Optional[str] = None) -> bool:
    """
    Отправляет email асинхронно через Celery
    
    Args:
        subject: Тема письма
        text_content: Текстовое содержимое письма
        from_email: Email отправителя
        recipient_list: Список получателей
        html_content: HTML содержимое письма (опционально)
        
    Returns:
        bool: True если email отправлен успешно, иначе False
    """
    try:
        msg = EmailMultiAlternatives(
            subject, text_content, from_email, recipient_list
        )
        if html_content:
            msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Email sent to {', '.join(recipient_list)}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

@shared_task
def send_order_confirmation_email(order_id: int) -> bool:
    """
    Отправляет email с подтверждением заказа
    
    Args:
        order_id: ID заказа
        
    Returns:
        bool: True если email отправлен успешно, иначе False
    """
    from .models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Проверяем, что у пользователя есть email
        if not order.user.email:
            return False
        
        # Подготавливаем контекст для шаблона
        context = {
            'order': order
        }
        
        # Рендерим HTML и текстовую версии письма
        html_content = render_to_string('email/order_confirmation.html', context)
        text_content = render_to_string('email/order_confirmation.txt', context)
        
        # Создаем email
        subject = f'Подтверждение заказа #{order.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = order.user.email
        
        # Отправляем асинхронно
        return send_email.delay(subject, text_content, from_email, [to_email], html_content).get()
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {str(e)}")
        return False

@shared_task
def send_supplier_order_notification(order_id: int) -> bool:
    """
    Отправляет уведомление поставщикам о новом заказе
    
    Args:
        order_id: ID заказа
        
    Returns:
        bool: True если email отправлен успешно, иначе False
    """
    from .models import Order, Supplier
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Получаем все элементы заказа
        order_items = order.items.all().select_related('product', 'product__supplier', 'product__supplier__user')
        
        # Группируем товары по поставщикам
        suppliers_items = {}
        for item in order_items:
            supplier = item.product.supplier
            if supplier not in suppliers_items:
                suppliers_items[supplier] = []
            
            # Добавляем свойство total_price для шаблона
            item.total_price = item.quantity * item.price
            suppliers_items[supplier].append(item)
        
        # Отправляем уведомление каждому поставщику
        for supplier, items in suppliers_items.items():
            # Проверяем, что у поставщика есть email
            if not supplier.user.email:
                continue
            
            # Считаем общую сумму товаров этого поставщика
            total_amount = sum(item.total_price for item in items)
            
            # Подготавливаем контекст для шаблона
            context = {
                'order': order,
                'supplier': supplier,
                'supplier_items': items,
                'total_amount': total_amount
            }
            
            # Рендерим HTML и текстовую версии письма
            html_content = render_to_string('email/supplier_order_notification.html', context)
            text_content = render_to_string('email/supplier_order_notification.txt', context)
            
            # Создаем email
            subject = f'Новый заказ #{order.id} для исполнения'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = supplier.user.email
            
            # Отправляем асинхронно
            send_email.delay(subject, text_content, from_email, [to_email], html_content)
        
        return True
    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending supplier order notification: {str(e)}")
        return False

@shared_task
def do_import(supplier_id: int, yaml_data: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Импортирует товары из YAML файла или строки
    
    Args:
        supplier_id: ID поставщика
        yaml_data: строка с YAML данными (если None, читает из filename)
        filename: путь к файлу для чтения (если yaml_data=None)
    
    Returns:
        dict: Результат импорта с количеством созданных и обновленных товаров
    """
    from .models import Supplier, Product, Category
    
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        
        # Получаем данные YAML
        if yaml_data is None and filename:
            with open(filename, 'r', encoding='utf-8') as f:
                yaml_data = f.read()
        
        if not yaml_data:
            return {"error": "Необходимо указать yaml_data или filename"}
        
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
                            # Если нет отдельного описания, создаем его из параметров
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
                    logger.error(f"Error importing product: {str(e)}")
                    continue
        
        return {
            "success": True,
            "created": created_count,
            "updated": updated_count,
            "total": created_count + updated_count
        }
    except Supplier.DoesNotExist:
        logger.error(f"Supplier with ID {supplier_id} not found")
        return {"error": "Supplier not found"}
    except Exception as e:
        logger.error(f"Error importing products: {str(e)}")
        return {"error": str(e)}