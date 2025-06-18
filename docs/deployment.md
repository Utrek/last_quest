# Руководство по развертыванию

## Требования

- Docker
- Docker Compose

## Подготовка к развертыванию

### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd myproject
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте файл `.env` и укажите необходимые параметры:

```
# Django settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com,www.example.com

# Database settings
DB_NAME=mydatabase
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=db
DB_PORT=5432

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@example.com

# Frontend URL
FRONTEND_URL=https://example.com
```

## Развертывание с использованием Docker

### 1. Сборка и запуск контейнеров

```bash
docker-compose up -d
```

### 2. Создание суперпользователя

```bash
docker-compose exec web python manage.py createsuperuser
```

### 3. Сбор статических файлов

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Применение миграций

```bash
docker-compose exec web python manage.py migrate
```

### 5. Проверка работоспособности

Откройте в браузере:
- Веб-приложение: http://localhost:80
- Админ-панель: http://localhost:80/admin
- Документация API: http://localhost:80/swagger/

## Настройка для производственной среды

### 1. Настройка HTTPS

Для настройки HTTPS с Let's Encrypt и Certbot, добавьте в `docker-compose.yml`:

```yaml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

И обновите конфигурацию Nginx:

```nginx
server {
    listen 80;
    server_name example.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location /static/ {
        alias /var/www/html/static/;
    }
    
    location /media/ {
        alias /var/www/html/media/;
    }
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Настройка резервного копирования

Создайте скрипт для резервного копирования базы данных:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Создаем директорию для резервных копий, если она не существует
mkdir -p $BACKUP_DIR

# Создаем резервную копию базы данных
docker-compose exec -T db pg_dump -U postgres mydatabase > $BACKUP_FILE

# Сжимаем резервную копию
gzip $BACKUP_FILE

# Удаляем старые резервные копии (оставляем последние 7)
find $BACKUP_DIR -name "backup_*.sql.gz" -type f -mtime +7 -delete
```

Добавьте задачу в crontab для ежедневного резервного копирования:

```
0 2 * * * /path/to/backup.sh
```

### 3. Настройка мониторинга

Для мониторинга контейнеров можно использовать Prometheus и Grafana:

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

## Обновление приложения

### 1. Получение последних изменений

```bash
git pull origin main
```

### 2. Пересборка и перезапуск контейнеров

```bash
docker-compose build
docker-compose up -d
```

### 3. Применение миграций

```bash
docker-compose exec web python manage.py migrate
```

### 4. Сбор статических файлов

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Управление контейнерами

### Просмотр логов

```bash
docker-compose logs -f
```

### Остановка контейнеров

```bash
docker-compose down
```

### Остановка контейнеров с удалением томов

```bash
docker-compose down -v
```

### Выполнение команд внутри контейнера

```bash
docker-compose exec web python manage.py <команда>
```