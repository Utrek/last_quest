#!/bin/bash

# Генерация документации с помощью MkDocs
echo "Генерация документации..."
mkdocs build

# Генерация документации API с помощью drf-yasg
echo "Генерация документации API..."
python manage.py generate_swagger swagger.yaml

# Копирование документации API в директорию MkDocs
echo "Копирование документации API..."
cp swagger.yaml site/swagger.yaml

echo "Документация успешно сгенерирована в директории 'site'"