from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, CartItem
from .serializers import OrderSerializer
from .email_utils import send_order_confirmation_email_async

class OrderConfirmationView(viewsets.ViewSet):
    """
    API для подтверждения заказа
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Подтверждение заказа
        """
        # Получаем ID корзины и ID контакта (адреса доставки)
        cart_id = request.data.get('cart_id')  # ID корзины может быть None, тогда используем все товары пользователя
        delivery_address_id = request.data.get('delivery_address_id')
        
        if not delivery_address_id:
            return Response(
                {"error": "Необходимо указать delivery_address_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем наличие товаров в корзине
        if cart_id:
            # Если указан ID корзины, используем только товары из этой корзины
            cart_items = CartItem.objects.filter(user=request.user, id=cart_id)
        else:
            # Иначе используем все товары пользователя
            cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем наличие адреса доставки
        try:
            from .models import DeliveryAddress
            delivery_address = DeliveryAddress.objects.get(id=delivery_address_id, user=request.user)
        except DeliveryAddress.DoesNotExist:
            return Response(
                {"error": "Адрес доставки не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            delivery_address=delivery_address,
            status='pending',
            total_amount=0
        )
        
        # Добавляем товары из корзины в заказ
        total = 0
        for cart_item in cart_items:
            # Проверяем наличие товара
            if cart_item.product.stock < cart_item.quantity:
                order.delete()
                return Response(
                    {"error": f"Недостаточно товара {cart_item.product.name} на складе. Доступно: {cart_item.product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем элемент заказа
            from .models import OrderItem
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Обновляем остаток товара
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
            
            # Считаем общую сумму
            total += cart_item.quantity * cart_item.product.price
        
        # Обновляем общую сумму заказа
        order.total_amount = total
        order.save()
        
        # Очищаем корзину
        cart_items.delete()
        
        # Отправляем email с подтверждением заказа
        email_sent = send_order_confirmation_email_async(order)
        
        # Отправляем уведомление поставщикам
        from .email_utils import send_supplier_order_notification_async
        supplier_email_sent = send_supplier_order_notification_async(order)
        
        return Response({
            "message": "Заказ успешно оформлен",
            "email_sent": email_sent,
            "supplier_email_sent": supplier_email_sent,
            "order": OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)