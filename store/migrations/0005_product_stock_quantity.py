from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0004_single_store_orders_and_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=100, verbose_name='Số lượng tồn kho'),
        ),
    ]
