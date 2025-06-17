from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_add_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='characteristics',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Характеристики'),
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='apartment',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Квартира'),
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='building',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Корпус'),
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='first_name',
            field=models.CharField(default='', max_length=100, verbose_name='Имя'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='house',
            field=models.CharField(default='', max_length=20, verbose_name='Дом'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='last_name',
            field=models.CharField(default='', max_length=100, verbose_name='Фамилия'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Отчество'),
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='street',
            field=models.CharField(default='', max_length=255, verbose_name='Улица'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='deliveryaddress',
            name='structure',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Строение'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='address',
            field=models.TextField(verbose_name='Полный адрес'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='city',
            field=models.CharField(max_length=100, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='Адрес по умолчанию'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='name',
            field=models.CharField(help_text="Название адреса (например, 'Дом', 'Работа')", max_length=100, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='phone',
            field=models.CharField(max_length=15, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='postal_code',
            field=models.CharField(max_length=20, verbose_name='Почтовый индекс'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='recipient_name',
            field=models.CharField(max_length=100, verbose_name='Имя получателя'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AlterField(
            model_name='deliveryaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_addresses', to='shop.user', verbose_name='Пользователь'),
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='deliveryaddress',
            options={'verbose_name': 'Адрес доставки', 'verbose_name_plural': 'Адреса доставки'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'Элемент заказа', 'verbose_name_plural': 'Элементы заказа'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name'], 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['user__company_name', 'user__username'], 'verbose_name': 'Поставщик', 'verbose_name_plural': 'Поставщики'},
        ),
        migrations.AlterModelOptions(
            name='cartitem',
            options={'verbose_name': 'Элемент корзины', 'verbose_name_plural': 'Элементы корзины'},
        ),
    ]