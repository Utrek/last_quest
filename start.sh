#!/bin/bash

# Проверка наличия файла .env
if [ ! -f .env ]; then
    echo "Файл .env не найден. Копирую из .env.example..."
    cp .env.example .env
    echo "Пожалуйста, отредактируйте файл .env перед запуском."
    exit 1
fi

# Запуск docker-compose
docker-compose up -d

# Создание суперпользователя
echo "Подождите, пока контейнеры запустятся..."
sleep 10
docker-compose exec web python manage.py createsuperuser