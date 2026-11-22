import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [('uploader', '0003_video')]
    operations = [
        migrations.CreateModel(name='Banner', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('title', models.CharField(max_length=160)),
            ('subtitle', models.CharField(max_length=220, blank=True)),
            ('link_path', models.CharField(max_length=220, default='/cardapio')),
            ('is_active', models.BooleanField(default=False)),
            ('sort_order', models.PositiveIntegerField(default=0)),
            ('image', models.ForeignKey(to='uploader.image', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True)),
        ], options={'ordering': ['sort_order', 'id']}),
    ]
