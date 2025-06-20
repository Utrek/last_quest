from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, help_text='Уникальный идентификатор товара',
                                   max_length=100, null=True, unique=True),
        ),
    ]
