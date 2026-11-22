from django.conf import settings
from django.db import models


class CustomQuote(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'solicitado', 'Solicitado'
        PROPOSED = 'proposto', 'Proposto'
        ACCEPTED = 'aceito', 'Aceito'
        DECLINED = 'recusado', 'Recusado'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='custom_quotes')
    title = models.CharField(max_length=160)
    details = models.TextField()
    flavor = models.CharField(max_length=120)
    portions = models.PositiveIntegerField()
    desired_date = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proposed_details = models.TextField(blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
