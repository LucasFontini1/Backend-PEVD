import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def pk():
    return models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(name='FAQ', fields=[
            ('id', pk()), ('question', models.CharField(max_length=240)),
            ('answer', models.TextField()), ('sort_order', models.PositiveIntegerField(default=0)),
            ('published', models.BooleanField(default=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
        ], options={'ordering': ['sort_order', 'id']}),
        migrations.CreateModel(name='ContactInquiry', fields=[
            ('id', pk()), ('name', models.CharField(max_length=120)),
            ('email', models.EmailField(max_length=254)), ('subject', models.CharField(max_length=180)),
            ('message', models.TextField()), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('handled_at', models.DateTimeField(blank=True, null=True)),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel(name='SupportTicket', fields=[
            ('id', pk()), ('subject', models.CharField(max_length=180)),
            ('status', models.CharField(max_length=16, default='aberto', choices=[
                ('aberto', 'Aberto'), ('respondido', 'Respondido'), ('encerrado', 'Encerrado'),
            ])), ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('order', models.ForeignKey(null=True, blank=True, to='orders.order',
                                        on_delete=django.db.models.deletion.SET_NULL)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                       on_delete=django.db.models.deletion.PROTECT, related_name='support_tickets')),
        ], options={'ordering': ['-updated_at']}),
        migrations.CreateModel(name='SupportMessage', fields=[
            ('id', pk()), ('body', models.TextField()),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                         on_delete=django.db.models.deletion.PROTECT)),
            ('ticket', models.ForeignKey(to='support.supportticket', related_name='messages',
                                         on_delete=django.db.models.deletion.CASCADE)),
        ], options={'ordering': ['created_at', 'id']}),
        migrations.CreateModel(name='CustomQuote', fields=[
            ('id', pk()), ('title', models.CharField(max_length=160)),
            ('details', models.TextField()), ('flavor', models.CharField(max_length=120)),
            ('portions', models.PositiveIntegerField()),
            ('desired_date', models.DateField()),
            ('status', models.CharField(max_length=16, default='solicitado', choices=[
                ('solicitado', 'Solicitado'), ('proposto', 'Proposto'),
                ('aceito', 'Aceito'), ('recusado', 'Recusado'),
            ])),
            ('proposed_price', models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)),
            ('proposed_details', models.TextField(blank=True)),
            ('valid_until', models.DateTimeField(null=True, blank=True)),
            ('accepted_at', models.DateTimeField(null=True, blank=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                       on_delete=django.db.models.deletion.PROTECT, related_name='custom_quotes')),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel(name='CommercialAudit', fields=[
            ('id', pk()), ('action', models.CharField(max_length=100)),
            ('target_type', models.CharField(max_length=60)),
            ('target_id', models.PositiveBigIntegerField()),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('actor', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True,
                                        on_delete=django.db.models.deletion.SET_NULL)),
        ], options={'ordering': ['-created_at']}),
    ]
