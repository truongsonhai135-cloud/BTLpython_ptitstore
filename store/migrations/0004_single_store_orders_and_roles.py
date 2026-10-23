import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0003_alter_product_options_product_vendor_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE store_userprofile SET role = 'customer' WHERE role = 'vendor'",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(model_name='product', name='vendor'),
        migrations.AddField(
            model_name='order', name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='orders', to=settings.AUTH_USER_MODEL,
                                    verbose_name='Tài khoản đặt hàng'),
        ),
        migrations.AlterField(
            model_name='userprofile', name='role',
            field=models.CharField(choices=[('customer', 'Khách hàng')], default='customer',
                                   max_length=20, verbose_name='Vai trò'),
        ),
        migrations.AlterField(
            model_name='orderitem', name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.product', verbose_name='Sản phẩm'),
        ),
        migrations.AlterField(
            model_name='orderitem', name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='Số lượng'),
        ),
        migrations.AlterField(
            model_name='order', name='total_price',
            field=models.DecimalField(decimal_places=0, max_digits=12, verbose_name='Tổng tiền'),
        ),
    ]
