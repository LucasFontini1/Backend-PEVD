from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='order', name='user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL, null=True, blank=True,
                related_name='orders', on_delete=django.db.models.deletion.PROTECT,
            ),
        ),
        migrations.AddField(
            model_name='order', name='source',
            field=models.CharField(max_length=16, default='site', choices=[
                ('site', 'Site'), ('whatsapp', 'WhatsApp'),
            ]),
        ),
        migrations.AddField(
            model_name='order', name='customer_name',
            field=models.CharField(max_length=160, blank=True),
        ),
        migrations.AddField(
            model_name='order', name='customer_phone',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
