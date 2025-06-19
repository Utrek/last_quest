import os
import django
from django.conf import settings
import pytest

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
    django.setup()
    
    # Отключаем Celery для тестов
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Дает доступ к базе данных для всех тестов
    """
    pass