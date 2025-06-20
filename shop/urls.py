from django.conf.urls.static import static
from django.conf import settings
from .views_supplier import SupplierExportViewSet
from .views_order import OrderConfirmationView
from .views_address import DeliveryAddressViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from . import views
from .models import Category

# Простой тестовый view для проверки API


@api_view(['GET'])
def api_test(request):
    return Response({"message": "API работает!"})

# Представление для создания категорий


@api_view(['POST'])
def create_category(request):
    name = request.data.get('name')
    if not name:
        return Response({"error": "Имя категории обязательно"}, status=status.HTTP_400_BAD_REQUEST)

    category, created = Category.objects.get_or_create(name=name)
    return Response({
        "id": category.id,
        "name": category.name,
        "created": created
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

# Представление для получения списка категорий


@api_view(['GET'])
def list_categories(request):
    categories = Category.objects.all()
    return Response([{"id": c.id, "name": c.name} for c in categories])


router = DefaultRouter()
router.register(r'supplier/products', views.SupplierViewSet, basename='supplier-products')
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='orders')

# Импортируем ViewSet для адресов доставки
router.register(r'addresses', DeliveryAddressViewSet, basename='addresses')

# Импортируем ViewSet для подтверждения заказа
router.register(r'order-confirmation', OrderConfirmationView, basename='order-confirmation')

# Импортируем ViewSet для экспорта товаров поставщика
router.register(r'supplier/export', SupplierExportViewSet, basename='supplier-export')

urlpatterns = [
    path('api/test/', api_test, name='api-test'),
    path('api/categories/', list_categories, name='list-categories'),
    path('api/categories/create/', create_category, name='create-category'),
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('api/password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

# Добавляем URL для доступа к медиа-файлам в режиме разработки

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
