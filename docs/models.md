# Документация моделей

## User

Расширенная модель пользователя, наследующаяся от AbstractUser.

### Поля

- `user_type` (CharField): Тип пользователя ('customer' или 'supplier')
- `phone` (CharField): Номер телефона
- `address` (TextField): Адрес
- `company_name` (CharField): Название компании (для поставщиков)
- `is_accepting_orders` (BooleanField): Принимает ли поставщик заказы

### Методы

- `is_supplier()`: Проверяет, является ли пользователь поставщиком

## Supplier

Модель профиля поставщика.

### Поля

- `user` (OneToOneField): Связь с моделью User
- `description` (TextField): Описание поставщика
- `logo` (ImageField): Логотип поставщика

## Category

Модель категории товаров.

### Поля

- `name` (CharField): Название категории

## Product

Модель товара.

### Поля

- `name` (CharField): Название товара
- `description` (TextField): Описание товара
- `price` (DecimalField): Цена товара
- `supplier` (ForeignKey): Связь с моделью Supplier
- `category` (ForeignKey): Связь с моделью Category
- `stock` (PositiveIntegerField): Количество товара на складе
- `image` (ImageField): Изображение товара
- `is_active` (BooleanField): Активен ли товар
- `sku` (CharField): Артикул товара
- `characteristics` (JSONField): Характеристики товара в формате JSON

### Методы

- `to_dict()`: Преобразует объект товара в словарь для экспорта
- `from_dict(data, supplier)`: Создает или обновляет товар из словаря

## DeliveryAddress

Модель адреса доставки.

### Поля

- `user` (ForeignKey): Связь с моделью User
- `name` (CharField): Название адреса (например, 'Дом', 'Работа')
- `last_name` (CharField): Фамилия получателя
- `first_name` (CharField): Имя получателя
- `middle_name` (CharField): Отчество получателя
- `recipient_name` (CharField): Полное имя получателя
- `email` (EmailField): Email получателя
- `phone` (CharField): Телефон получателя
- `city` (CharField): Город
- `street` (CharField): Улица
- `house` (CharField): Дом
- `building` (CharField): Корпус
- `structure` (CharField): Строение
- `apartment` (CharField): Квартира
- `postal_code` (CharField): Почтовый индекс
- `address` (TextField): Полный адрес
- `is_default` (BooleanField): Адрес по умолчанию
- `created_at` (DateTimeField): Дата создания
- `updated_at` (DateTimeField): Дата обновления

### Методы

- `save()`: Переопределенный метод сохранения, формирующий полный адрес и управляющий адресами по умолчанию

## Order

Модель заказа.

### Поля

- `user` (ForeignKey): Связь с моделью User
- `delivery_address` (ForeignKey): Связь с моделью DeliveryAddress
- `created_at` (DateTimeField): Дата создания
- `updated_at` (DateTimeField): Дата обновления
- `status` (CharField): Статус заказа ('pending', 'processing', 'shipped', 'delivered', 'cancelled')
- `total_amount` (DecimalField): Общая сумма заказа

### Методы

- `get_status_display()`: Возвращает отображаемое значение статуса

## OrderItem

Модель элемента заказа.

### Поля

- `order` (ForeignKey): Связь с моделью Order
- `product` (ForeignKey): Связь с моделью Product
- `quantity` (PositiveIntegerField): Количество товара
- `price` (DecimalField): Цена товара на момент заказа

## CartItem

Модель элемента корзины.

### Поля

- `user` (ForeignKey): Связь с моделью User
- `product` (ForeignKey): Связь с моделью Product
- `quantity` (PositiveIntegerField): Количество товара
- `created_at` (DateTimeField): Дата добавления в корзину
- `updated_at` (DateTimeField): Дата обновления