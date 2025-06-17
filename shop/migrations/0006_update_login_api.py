from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_add_admin_fields'),
    ]

    operations = [
        # Эта миграция не содержит изменений схемы базы данных,
        # она нужна только для отслеживания изменений в API
    ]