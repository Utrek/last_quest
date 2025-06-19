from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from .models import Supplier



class SupplierExportViewSet(viewsets.ViewSet):
    """
    API для экспорта товаров поставщика
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def export_to_file(self, request: Request) -> Response:
        """
        Экспорт товаров в YAML файл на сервере
        """
        from .utils import export_products_to_file
        import os
        from django.conf import settings
        
        try:
            supplier = Supplier.objects.get(user=request.user)
            
            # Экспортируем товары
            filename = export_products_to_file(supplier)
            
            # Проверяем, что файл действительно создан
            if not os.path.exists(filename):
                return Response({
                    "error": f"Файл не был создан по пути {filename}",
                    "details": "Проверьте права доступа к директории"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Получаем размер файла
            file_size = os.path.getsize(filename)
            
            # Получаем количество товаров
            products_count = supplier.products.count()
            
            # Создаем URL для доступа к файлу, если он в директории media
            file_url = None
            if filename.startswith(settings.MEDIA_ROOT):
                relative_path = os.path.relpath(filename, settings.MEDIA_ROOT)
                file_url = request.build_absolute_uri(settings.MEDIA_URL + relative_path)
            
            return Response({
                "success": True,
                "message": f"Товары успешно экспортированы в файл",
                "filename": os.path.basename(filename),
                "file_path": filename,
                "file_url": file_url,
                "file_size": file_size,
                "products_count": products_count,
                "supplier": supplier.user.company_name or supplier.user.username
            })
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            return Response({
                "error": str(e),
                "traceback": traceback.format_exc()
            }, status=status.HTTP_400_BAD_REQUEST)