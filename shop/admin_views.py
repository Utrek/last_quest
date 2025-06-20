
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Supplier
from .tasks import do_import
import os
from typing import Any, List


@method_decorator(staff_member_required, name='dispatch')
class ImportProductsView(View):
    """
    Представление для импорта товаров из YAML файла через админку
    """
    template_name = 'admin/shop/import_products.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Отображает форму для импорта товаров
        """
        suppliers = Supplier.objects.all()
        return render(request, self.template_name, {'suppliers': suppliers})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Обрабатывает отправку формы импорта товаров
        """
        supplier_id = request.POST.get('supplier')
        yaml_file = request.FILES.get('yaml_file')

        if not supplier_id:
            messages.error(request, "Необходимо выбрать поставщика")
            return redirect('admin:import_products')

        if not yaml_file:
            messages.error(request, "Необходимо выбрать YAML файл")
            return redirect('admin:import_products')

        try:
            # Сохраняем файл во временную директорию
            file_path = os.path.join('media', 'imports', yaml_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb+') as destination:
                for chunk in yaml_file.chunks():
                    destination.write(chunk)

            # Запускаем задачу импорта асинхронно
            task = do_import.delay(supplier_id, filename=file_path)

            messages.success(
                request,
                (
                    f"Задача импорта запущена (ID: {task.id}). "
                    f"Результаты будут доступны после завершения."
                )
            )
        except Exception as e:
            messages.error(request, f"Ошибка при импорте: {str(e)}")

        return redirect('admin:shop_product_changelist')

# Функция для добавления URL-шаблонов в админку


def get_admin_urls(urls: List) -> List:
    """
    Добавляет URL-шаблоны для админки
    """
    def get_urls() -> List:
        my_urls = [
            path('import-products/', ImportProductsView.as_view(), name='import_products'),
        ]
        return my_urls + urls
    return get_urls
