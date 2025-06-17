from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeliveryAddress
from .serializers import DeliveryAddressSerializer

class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """
    API для управления адресами доставки
    """
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Установить адрес как адрес по умолчанию
        """
        address = self.get_object()
        
        # Сбрасываем флаг у всех адресов пользователя
        DeliveryAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Устанавливаем флаг у текущего адреса
        address.is_default = True
        address.save()
        
        return Response({"success": True, "message": "Адрес установлен как адрес по умолчанию"})