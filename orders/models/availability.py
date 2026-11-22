from django.db import models
from django.db.models import Q


class DeliveryZone(models.Model):
    name = models.CharField(max_length=120)
    zip_prefix = models.CharField(max_length=8, unique=True)
    fee = models.DecimalField(max_digits=9, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(condition=Q(fee__gte=0), name='delivery_fee_nonnegative'),
            models.CheckConstraint(condition=Q(minimum_order__gte=0), name='delivery_minimum_nonnegative'),
        ]


class BusinessHour(models.Model):
    weekday = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(7)])
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    pickup_enabled = models.BooleanField(default=True)
    delivery_enabled = models.BooleanField(default=False)

    class Meta:
        ordering = ['weekday', 'opens_at']
        constraints = [
            models.CheckConstraint(condition=Q(closes_at__gt=models.F('opens_at')), name='valid_business_hour'),
            models.UniqueConstraint(fields=['weekday', 'opens_at', 'closes_at'], name='unique_business_window'),
        ]


class BlockedDate(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=180, blank=True)
