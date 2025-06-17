#!/usr/bin/env python
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

def check_export_directory():
    """
    Проверяет директорию для экспорта файлов
    """
    # Путь к директории экспорта
    export_dir = os.path.join(settings.BASE_DIR, 'exports')
    
    # Проверяем существование директории
    if not os.path.exists(export_dir):
        print(f"Директория {export_dir} не существует. Создаем...")
        try:
            os.makedirs(export_dir, exist_ok=True)
            print(f"Директория {export_dir} успешно создана.")
        except Exception as e:
            print(f"Ошибка при создании директории: {str(e)}")
            return False
    
    # Проверяем права на запись
    if not os.access(export_dir, os.W_OK):
        print(f"Нет прав на запись в директорию {export_dir}")
        print("Выполните команду:")
        print(f"chmod -R 777 {export_dir}")
        return False
    
    # Проверяем возможность создания файла
    test_file = os.path.join(export_dir, 'test_file.txt')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        print(f"Тестовый файл успешно создан: {test_file}")
        os.remove(test_file)
        print("Тестовый файл успешно удален.")
    except Exception as e:
        print(f"Ошибка при создании тестового файла: {str(e)}")
        return False
    
    print(f"Директория {export_dir} доступна для записи.")
    return True

if __name__ == "__main__":
    if check_export_directory():
        sys.exit(0)
    else:
        sys.exit(1)