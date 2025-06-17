# Интернет-магазин

## Запуск проекта с использованием Docker

### Предварительные требования

- Docker
- Docker Compose

### Шаги для запуска

1. **Клонирование репозитория**

```bash
git clone <url-репозитория>
cd myproject
```

2. **Настройка переменных окружения**

```bash
cp .env.example .env
```

Отредактируйте файл `.env` и укажите необходимые параметры.

3. **Сборка и запуск контейнеров**

```bash
./start.sh
```

или вручную:

```bash
docker-compose up -d
```

4. **Создание суперпользователя**

```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Доступ к приложению**

- Веб-приложение: http://localhost:80
- Админ-панель: http://localhost:80/admin

### Управление контейнерами

- **Остановка контейнеров**

```bash
docker-compose down
```

- **Просмотр логов**

```bash
docker-compose logs -f
```

- **Выполнение команд внутри контейнера**

```bash
docker-compose exec web python manage.py <команда>
```

## Структура проекта

- `myproject/` - основной проект Django
- `shop/` - приложение интернет-магазина
- `nginx/` - конфигурация Nginx
- `Dockerfile` - инструкции для сборки контейнера Django
- `Dockerfile.celery` - инструкции для сборки контейнера Celery
- `docker-compose.yml` - конфигурация Docker Compose
- `requirements.txt` - зависимости Python