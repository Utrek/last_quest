from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'supplier/products', views.SupplierViewSet, basename='supplier-products')
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='orders')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('api/password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

