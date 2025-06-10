from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'supplier/products', views.SupplierViewSet, basename='supplier-products')

urlpatterns = [
    path('api/', include(router.urls)),
]
