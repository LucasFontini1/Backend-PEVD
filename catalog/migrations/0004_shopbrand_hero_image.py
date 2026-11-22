from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('catalog', '0003_shopbrand_business')]
    operations = [
        migrations.AddField(
            model_name='shopbrand', name='hero_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='hero_for_shops', to='uploader.image'),
        ),
    ]
