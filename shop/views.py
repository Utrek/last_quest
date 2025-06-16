from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Product, Order, OrderItem, Supplier, CartItem
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, ProductSerializer, OrderSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, CartItemSerializer
)

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is None:
                return Response({"error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({"error": "Пользователь деактивирован"}, status=status.HTTP_401_UNAUTHORIZED)
                
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                
                # Отправка email с ссылкой для сброса пароля
                send_mail(
                    'Сброс пароля',
                    f'Для сброса пароля перейдите по ссылке: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({"detail": "Инструкции по сбросу пароля отправлены на вашу почту."})
            except User.DoesNotExist:
                return Response({"detail": "Пользователь с таким email не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token_parts = serializer.validated_data['token'].split('/')
                if len(token_parts) != 2:
                    return Response({"detail": "Неверный формат токена."}, status=status.HTTP_400_BAD_REQUEST)
                    
                uid, token = token_parts
                uid = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=uid)
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['password'])
                    user.save()
                    return Response({"detail": "Пароль успешно изменен."})
                else:
                    return Response({"detail": "Недействительный токен."}, status=status.HTTP_400_BAD_REQUEST)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"detail": "Недействительная ссылка для сброса пароля."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'is_supplier') and request.user.is_supplier()

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API для просмотра продуктов всеми пользователями
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Фильтрация по категории
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Поиск по названию или описанию
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
            
        # Сортировка
        ordering = self.request.query_params.get('ordering', None)
        if ordering:
            if ordering == 'price':
                queryset = queryset.order_by('price')
            elif ordering == '-price':
                queryset = queryset.order_by('-price')
            elif ordering == 'name':
                queryset = queryset.order_by('name')
                
        return queryset

class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        try:
            supplier = Supplier.objects.get(user=self.request.user)
            return Product.objects.filter(supplier=supplier)
        except Supplier.DoesNotExist:
            return Product.objects.none()
            
    def perform_create(self, serializer):
        try:
            supplier = Supplier.objects.get(user=self.request.user)
            serializer.save(supplier=supplier)
        except Supplier.DoesNotExist:
            raise permissions.exceptions.PermissionDenied("Только поставщики могут добавлять товары")
    
    @action(detail=False, methods=['post'])
    def toggle_accepting_orders(self, request):
        user = request.user
        user.is_accepting_orders = not user.is_accepting_orders
        user.save()
        return Response({'is_accepting_orders': user.is_accepting_orders})
    
    @action(detail=False, methods=['get'])
    def orders(self, request):
        try:
            supplier = Supplier.objects.get(user=self.request.user)
            # Получаем заказы, содержащие товары этого поставщика
            supplier_products = Product.objects.filter(supplier=supplier)
            order_items = OrderItem.objects.filter(product__in=supplier_products)
            orders = Order.objects.filter(id__in=order_items.values_list('order', flat=True)).distinct()
            
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def update_prices(self, request):
        products_data = request.data.get('products', [])
        updated_products = []
        
        try:
            supplier = Supplier.objects.get(user=self.request.user)
            
            for product_data in products_data:
                product_id = product_data.get('id')
                new_price = product_data.get('price')
                
                try:
                    product = Product.objects.get(id=product_id, supplier=supplier)
                    product.price = new_price
                    product.save()
                    updated_products.append(product.id)
                except Product.DoesNotExist:
                    pass
            
            return Response({'updated_products': updated_products})
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier profile not found"}, status=status.HTTP_404_NOT_FOUND)

class CartViewSet(viewsets.ModelViewSet):
    """
    API для работы с корзиной пользователя
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """
        Обновление количества товара в корзине
        """
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        
        if not product_id or not quantity:
            return Response(
                {"error": "Необходимо указать product и quantity"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            serializer = self.get_serializer(cart_item)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response(
                {"error": f"Товар с ID {product_id} не найден в корзине"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Проверяем наличие товаров на складе
        insufficient_items = []
        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                insufficient_items.append({
                    'product_id': cart_item.product.id,
                    'product_name': cart_item.product.name,
                    'requested': cart_item.quantity,
                    'available': cart_item.product.stock
                })
        
        # Если есть товары с недостаточным количеством, предлагаем вариант
        if insufficient_items:
            return Response({
                "warning": "Недостаточно товаров на складе",
                "insufficient_items": insufficient_items,
                "options": [
                    "Уменьшите количество товаров в корзине",
                    "Используйте параметр 'partial=true' для оформления заказа с доступным количеством"
                ]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Параметр для частичного оформления заказа
        partial = request.data.get('partial', False)
        
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=0
        )
        
        total = 0
        for cart_item in cart_items:
            # Определяем количество для заказа
            quantity = min(cart_item.quantity, cart_item.product.stock) if partial else cart_item.quantity
            
            # Если не частичный заказ и недостаточно товара, отменяем
            if not partial and cart_item.product.stock < cart_item.quantity:
                order.delete()
                return Response(
                    {"error": f"Недостаточно товара {cart_item.product.name} на складе. Доступно: {cart_item.product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Если товара нет в наличии, пропускаем
            if quantity == 0:
                continue
                
            # Создаем элемент заказа
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=quantity,
                price=cart_item.product.price
            )
            
            # Обновляем остаток товара
            cart_item.product.stock -= quantity
            cart_item.product.save()
            
            # Считаем общую сумму
            total += quantity * cart_item.product.price
            
            # Если частичный заказ и взяли меньше, чем было в корзине
            if partial and quantity < cart_item.quantity:
                cart_item.quantity -= quantity
                cart_item.save()
            else:
                cart_item.delete()
        
        # Если не добавили ни одного товара, отменяем заказ
        if not order.items.exists():
            order.delete()
            return Response(
                {"error": "Не удалось оформить заказ, все товары отсутствуют на складе"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Обновляем общую сумму заказа
        order.total_amount = total
        order.save()
        
        return Response({
            "message": "Заказ успешно оформлен" + (" (частично)" if partial else ""),
            "order": OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)
class OrderViewSet(viewsets.ModelViewSet):
    """
    API для работы с заказами пользователя
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'cancelled':
            return Response(
                {"error": "Невозможно изменить отмененный заказ"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
        
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'cancelled':
            return Response(
                {"error": "Невозможно изменить отмененный заказ"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        if order.status == 'pending' or order.status == 'processing':
            # Возвращаем товары на склад
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
            
            order.status = 'cancelled'
            order.save()
            
            # Возвращаем полную информацию о заказе с обновленным статусом
            serializer = self.get_serializer(order)
            return Response({
                "detail": "Заказ успешно отменен",
                "order": serializer.data
            })
        else:
            return Response(
                {"error": "Невозможно отменить заказ в текущем статусе"},
                status=status.HTTP_400_BAD_REQUEST
            )