import factory
import uuid
from django.contrib.auth import get_user_model
from shop.models import (
    Supplier, Category, Product, DeliveryAddress, Order, OrderItem, CartItem
)
from decimal import Decimal

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.LazyFunction(lambda: f'user{uuid.uuid4().hex[:8]}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    user_type = 'customer'


class SupplierUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.LazyFunction(lambda: f'supplier{uuid.uuid4().hex[:8]}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    user_type = 'supplier'
    company_name = factory.Faker('company')


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    user = factory.SubFactory(SupplierUserFactory)
    description = factory.Faker('paragraph')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Проверяем, существует ли уже Supplier для данного пользователя
        user = kwargs.get('user')
        if user and hasattr(user, 'supplier_profile'):
            return user.supplier_profile
        return super()._create(model_class, *args, **kwargs)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    description = factory.Faker('paragraph')
    price = factory.LazyFunction(lambda: Decimal('99.99'))
    supplier = factory.SubFactory(SupplierFactory)
    category = factory.SubFactory(CategoryFactory)
    stock = 100
    is_active = True
    sku = factory.LazyFunction(lambda: f'SKU-{uuid.uuid4().hex[:8]}')
    characteristics = {'color': 'red', 'size': 'M', 'weight': '1kg'}


class DeliveryAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryAddress

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Address {n}')
    last_name = factory.Faker('last_name')
    first_name = factory.Faker('first_name')
    middle_name = factory.Faker('first_name')
    recipient_name = factory.LazyAttribute(lambda obj: f'{obj.first_name} {obj.last_name}')
    email = factory.Faker('email')
    phone = '+79001234567'  # Фиксированный номер телефона
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    house = factory.Faker('building_number')
    postal_code = factory.Faker('postcode')
    is_default = False


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    delivery_address = factory.SubFactory(DeliveryAddressFactory)
    status = 'pending'


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price = factory.SelfAttribute('product.price')


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
