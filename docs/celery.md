# Документация Celery задач

## Настройка Celery

Celery используется для асинхронной обработки задач, таких как отправка email и импорт товаров.

### Конфигурация

Конфигурация Celery находится в файле `myproject/celery.py`:

```python
import os
from celery import Celery

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Создание экземпляра приложения Celery
app = Celery('myproject')

# Загрузка настроек из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из всех приложений Django
app.autodiscover_tasks()
```

### Настройки в settings.py

```python
# Настройки Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
```

## Задачи

### send_email

**Описание:** Отправляет email асинхронно через Celery.

**Параметры:**
- `subject` (str): Тема письма
- `text_content` (str): Текстовое содержимое письма
- `from_email` (str): Email отправителя
- `recipient_list` (List[str]): Список получателей
- `html_content` (Optional[str]): HTML содержимое письма (опционально)

**Возвращает:**
- `bool`: True если email отправлен успешно, иначе False

**Пример использования:**
```python
from shop.tasks import send_email

send_email.delay(
    subject='Тема письма',
    text_content='Текст письма',
    from_email='from@example.com',
    recipient_list=['to@example.com'],
    html_content='<p>HTML содержимое</p>'
)
```

### send_order_confirmation_email

**Описание:** Отправляет email с подтверждением заказа.

**Параметры:**
- `order_id` (int): ID заказа

**Возвращает:**
- `bool`: True если email отправлен успешно, иначе False

**Пример использования:**
```python
from shop.tasks import send_order_confirmation_email

send_order_confirmation_email.delay(order_id=123)
```

### send_supplier_order_notification

**Описание:** Отправляет уведомление поставщикам о новом заказе.

**Параметры:**
- `order_id` (int): ID заказа

**Возвращает:**
- `bool`: True если email отправлен успешно, иначе False

**Пример использования:**
```python
from shop.tasks import send_supplier_order_notification

send_supplier_order_notification.delay(order_id=123)
```

### do_import

**Описание:** Импортирует товары из YAML файла или строки.

**Параметры:**
- `supplier_id` (int): ID поставщика
- `yaml_data` (Optional[str]): строка с YAML данными (если None, читает из filename)
- `filename` (Optional[str]): путь к файлу для чтения (если yaml_data=None)

**Возвращает:**
- `dict`: Результат импорта с количеством созданных и обновленных товаров

**Пример использования:**
```python
from shop.tasks import do_import

# Импорт из строки
yaml_data = """
shop: Test Shop
categories:
  - id: 1
    name: Electronics
goods:
  - id: SKU-001
    name: Test Product
    price: 99.99
    category: 1
    quantity: 10
"""
result = do_import.delay(supplier_id=123, yaml_data=yaml_data)

# Импорт из файла
result = do_import.delay(supplier_id=123, filename='/path/to/file.yaml')
```

## Запуск Celery

### Запуск Celery worker

```bash
celery -A myproject worker -l info
```

### Запуск Celery в Docker

```bash
docker-compose up celery
```