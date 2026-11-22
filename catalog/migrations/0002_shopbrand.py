import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='ShopBrand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Pensei em Você Doces', max_length=120)),
                ('background_color', models.CharField(default='#FFF5E9', max_length=7)),
                ('primary_color', models.CharField(default='#C96680', max_length=7)),
                ('heading_color', models.CharField(default='#704438', max_length=7)),
                ('logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='uploader.image')),
            ],
        ),
    ]
