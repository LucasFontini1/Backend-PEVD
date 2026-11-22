from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('catalog', '0002_shopbrand')]
    operations = [
        migrations.AddField(model_name='shopbrand', name='business_email', field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name='shopbrand', name='phone', field=models.CharField(blank=True, max_length=24)),
        migrations.AddField(model_name='shopbrand', name='pickup_address', field=models.CharField(blank=True, max_length=240)),
        migrations.AddField(model_name='shopbrand', name='instagram_url', field=models.URLField(blank=True)),
        migrations.AddField(model_name='shopbrand', name='announcement', field=models.CharField(blank=True, max_length=220)),
        migrations.AddField(model_name='shopbrand', name='response_hours', field=models.PositiveSmallIntegerField(blank=True, null=True)),
    ]
