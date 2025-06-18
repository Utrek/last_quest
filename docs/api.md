# API Документация

## Аутентификация

### Регистрация

**Endpoint:** `POST /api/register/`

**Описание:** Регистрация нового пользователя (клиента или поставщика).

**Параметры запроса:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password2": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "address": "string",
  "user_type": "string",
  "company_name": "string"
}
```

**Ответ:**
```json
{
  "token": "string",
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "user_type": "string"
  }
}
```

### Вход

**Endpoint:** `POST /api/login/`

**Описание:** Аутентификация пользователя по email и паролю.

**Параметры запроса:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Ответ:**
```json
{
  "token": "string",
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "user_type": "string"
  }
}
```

## Товары

### Получение списка товаров

**Endpoint:** `GET /api/products/`

**Описание:** Получение списка всех товаров с возможностью фильтрации и поиска.

**Параметры запроса:**
- `category` (query): ID категории для фильтрации
- `search` (query): Поисковый запрос
- `ordering` (query): Поле для сортировки (например, `price`, `-price`, `name`)
- `page` (query): Номер страницы
- `page_size` (query): Количество элементов на странице

**Ответ:**
```json
{
  "count": "integer",
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "integer",
      "name": "string",
      "description": "string",
      "price": "string",
      "category": {
        "id": "integer",
        "name": "string"
      },
      "supplier": {
        "id": "integer",
        "name": "string"
      },
      "stock": "integer",
      "image": "string",
      "is_active": "boolean",
      "characteristics": "object"
    }
  ]
}
```

### Получение информации о товаре

**Endpoint:** `GET /api/products/{id}/`

**Описание:** Получение детальной информации о товаре.

**Параметры запроса:**
- `id` (path): ID товара

**Ответ:**
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "price": "string",
  "category": {
    "id": "integer",
    "name": "string"
  },
  "supplier": {
    "id": "integer",
    "name": "string"
  },
  "stock": "integer",
  "image": "string",
  "is_active": "boolean",
  "characteristics": "object"
}
```

## Корзина

### Получение корзины

**Endpoint:** `GET /api/cart/`

**Описание:** Получение содержимого корзины пользователя.

**Требуется аутентификация:** Да

**Ответ:**
```json
{
  "id": "integer",
  "items": [
    {
      "id": "integer",
      "product": "integer",
      "product_details": {
        "id": "integer",
        "name": "string",
        "price": "string",
        "image": "string"
      },
      "quantity": "integer",
      "total_price": "string"
    }
  ],
  "total_items": "integer",
  "total_amount": "string"
}
```

### Добавление товара в корзину

**Endpoint:** `POST /api/cart/`

**Описание:** Добавление товара в корзину пользователя.

**Требуется аутентификация:** Да

**Параметры запроса:**
```json
{
  "product": "integer",
  "quantity": "integer"
}
```

**Ответ:**
```json
{
  "id": "integer",
  "product": "integer",
  "product_details": {
    "id": "integer",
    "name": "string",
    "price": "string",
    "image": "string"
  },
  "quantity": "integer",
  "total_price": "string"
}
```

### Изменение количества товара в корзине

**Endpoint:** `POST /api/cart/update_quantity/`

**Описание:** Изменение количества товара в корзине пользователя.

**Требуется аутентификация:** Да

**Параметры запроса:**
```json
{
  "product": "integer",
  "quantity": "integer"
}
```

**Ответ:**
```json
{
  "id": "integer",
  "product": "integer",
  "product_details": {
    "id": "integer",
    "name": "string",
    "price": "string",
    "image": "string"
  },
  "quantity": "integer",
  "total_price": "string"
}
```

### Удаление товара из корзины

**Endpoint:** `POST /api/cart/remove_product/`

**Описание:** Удаление товара из корзины пользователя.

**Требуется аутентификация:** Да

**Параметры запроса:**
```json
{
  "product": "integer"
}
```

**Ответ:**
```json
{
  "success": "boolean",
  "message": "string"
}
```

## Заказы

### Оформление заказа

**Endpoint:** `POST /api/order-confirmation/confirm/`

**Описание:** Оформление заказа на основе содержимого корзины.

**Требуется аутентификация:** Да

**Параметры запроса:**
```json
{
  "delivery_address_id": "integer",
  "cart_id": "integer"
}
```

**Ответ:**
```json
{
  "order": {
    "id": "integer",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "total_amount": "string",
    "items": [
      {
        "id": "integer",
        "product": "integer",
        "product_details": {
          "name": "string",
          "price": "string"
        },
        "quantity": "integer",
        "price": "string"
      }
    ]
  }
}
```

### Получение списка заказов

**Endpoint:** `GET /api/orders/`

**Описание:** Получение списка заказов пользователя.

**Требуется аутентификация:** Да

**Ответ:**
```json
[
  {
    "id": "integer",
    "status": "string",
    "created_at": "string",
    "updated_at": "string",
    "total_amount": "string",
    "items": [
      {
        "id": "integer",
        "product": "integer",
        "product_details": {
          "name": "string",
          "price": "string"
        },
        "quantity": "integer",
        "price": "string"
      }
    ]
  }
]
```

### Получение информации о заказе

**Endpoint:** `GET /api/orders/{id}/`

**Описание:** Получение детальной информации о заказе.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `id` (path): ID заказа

**Ответ:**
```json
{
  "id": "integer",
  "status": "string",
  "created_at": "string",
  "updated_at": "string",
  "total_amount": "string",
  "delivery_address": {
    "id": "integer",
    "name": "string",
    "address": "string"
  },
  "items": [
    {
      "id": "integer",
      "product": "integer",
      "product_details": {
        "name": "string",
        "price": "string"
      },
      "quantity": "integer",
      "price": "string"
    }
  ]
}
```

### Отмена заказа

**Endpoint:** `POST /api/orders/{id}/cancel/`

**Описание:** Отмена заказа.

**Требуется аутентификация:** Да

**Параметры запроса:**
- `id` (path): ID заказа

**Ответ:**
```json
{
  "detail": "string",
  "order": {
    "id": "integer",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}
```

## API для поставщиков

### Получение списка своих товаров

**Endpoint:** `GET /api/supplier/products/`

**Описание:** Получение списка товаров поставщика.

**Требуется аутентификация:** Да (поставщик)

**Ответ:**
```json
[
  {
    "id": "integer",
    "name": "string",
    "description": "string",
    "price": "string",
    "category": "integer",
    "stock": "integer",
    "image": "string",
    "is_active": "boolean",
    "characteristics": "object"
  }
]
```

### Добавление нового товара

**Endpoint:** `POST /api/supplier/products/`

**Описание:** Добавление нового товара поставщиком.

**Требуется аутентификация:** Да (поставщик)

**Параметры запроса:**
```json
{
  "name": "string",
  "description": "string",
  "price": "string",
  "category": "integer",
  "stock": "integer",
  "is_active": "boolean",
  "characteristics": "object"
}
```

**Ответ:**
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "price": "string",
  "category": "integer",
  "stock": "integer",
  "image": "string",
  "is_active": "boolean",
  "characteristics": "object"
}
```

### Обновление товара

**Endpoint:** `PUT /api/supplier/products/{id}/`

**Описание:** Обновление информации о товаре.

**Требуется аутентификация:** Да (поставщик)

**Параметры запроса:**
- `id` (path): ID товара
```json
{
  "name": "string",
  "description": "string",
  "price": "string",
  "category": "integer",
  "stock": "integer",
  "is_active": "boolean",
  "characteristics": "object"
}
```

**Ответ:**
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "price": "string",
  "category": "integer",
  "stock": "integer",
  "image": "string",
  "is_active": "boolean",
  "characteristics": "object"
}
```

### Удаление товара

**Endpoint:** `DELETE /api/supplier/products/{id}/`

**Описание:** Удаление товара.

**Требуется аутентификация:** Да (поставщик)

**Параметры запроса:**
- `id` (path): ID товара

**Ответ:** 204 No Content

### Экспорт товаров

**Endpoint:** `GET /api/supplier/products/export_products/`

**Описание:** Экспорт товаров поставщика в YAML формате.

**Требуется аутентификация:** Да (поставщик)

**Ответ:** YAML файл

### Импорт товаров

**Endpoint:** `POST /api/supplier/products/import_products/`

**Описание:** Импорт товаров из YAML файла.

**Требуется аутентификация:** Да (поставщик)

**Параметры запроса:** YAML файл

**Ответ:**
```json
{
  "created": "integer",
  "updated": "integer",
  "total": "integer"
}
```