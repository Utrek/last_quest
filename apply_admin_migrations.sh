#!/bin/bash

# Создание миграций
echo "Создание миграций..."
python manage.py makemigrations

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Создание суперпользователя, если его нет
echo "Проверка наличия суперпользователя..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан: admin/admin123')
else:
    print('Суперпользователь уже существует')
"

echo "Миграции успешно применены!"