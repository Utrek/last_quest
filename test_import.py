#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from shop.models import User, Supplier
from shop.simple_import import simple_import_from_yaml

def main():
    # Получаем пользователя-поставщика
    try:
        user = User.objects.filter(user_type='supplier').first()
        if not user:
            print("Не найден пользователь с типом 'supplier'")
            return
        
        print(f"Импорт товаров для поставщика: {user.username}")
        
        # Импортируем товары
        result = simple_import_from_yaml(user)
        
        # Выводим результат
        if "error" in result:
            print(f"Ошибка: {result['error']}")
        else:
            print(f"Успешно импортировано товаров: {result['created']} создано, {result['updated']} обновлено")
            
        if "errors" in result:
            print("\nОшибки при импорте отдельных товаров:")
            for error in result["errors"]:
                print(f"- {error}")
    
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()