from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from .models import Product, Order, OrderItem, Supplier, Category, CartItem, DeliveryAddress

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone', 'address', 'user_type', 'company_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # Если пользователь - поставщик, создаем профиль поставщика
        if user.user_type == 'supplier':
            Supplier.objects.get_or_create(user=user)
        
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'address', 'user_type', 'company_name')
        extra_kwargs = {'password': {'write_only': True}}

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'user', 'description', 'logo')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'supplier', 'category', 'stock', 'image', 'is_active', 'characteristics')
        read_only_fields = ('supplier',)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = (
            'id', 'name', 'last_name', 'first_name', 'middle_name', 
            'recipient_name', 'email', 'phone', 'city', 'street', 
            'house', 'building', 'structure', 'apartment', 
            'postal_code', 'address', 'is_default'
        )
        read_only_fields = ('user', 'address')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    delivery_address = DeliveryAddressSerializer(read_only=True)
    delivery_address_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryAddress.objects.all(), 
        source='delivery_address',
        write_only=True,
        required=False
    )
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'delivery_address', 'delivery_address_id', 'created_at', 'updated_at', 'status', 'status_display', 'total_amount', 'items')
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def get_status_display(self, obj):
        status_map = {
            'pending': 'Ожидание',
            'processing': 'В обработке',
            'shipped': 'Отправлен',
            'delivered': 'Доставлен',
            'cancelled': 'Отменен'
        }
        return status_map.get(obj.status, obj.status)
    
    def get_total_amount(self, obj):
        total = sum(item.quantity * item.price for item in obj.items.all())
        return str(total)
        
    def validate_delivery_address_id(self, value):
        """
        Проверяем, что адрес доставки принадлежит пользователю
        """
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Этот адрес доставки не принадлежит вам")
        return value

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    product_image = serializers.ImageField(source='product.image', read_only=True)
    product_details = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'product_image', 'product_details', 'quantity', 'total_price')
    
    def get_product_details(self, obj):
        return {
            'name': obj.product.name,
            'price': str(obj.product.price)
        }
    
    def get_total_price(self, obj):
        from decimal import Decimal
        total = Decimal(str(obj.quantity)) * Decimal(str(obj.product.price))
        return f"{total:.2f}"
        
    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity', instance.quantity)
        instance.quantity = int(quantity) if quantity else instance.quantity
        instance.save()
        return instance

