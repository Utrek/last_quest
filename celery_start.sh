#!/bin/bash

# Запуск Celery worker
celery -A myproject worker -l info