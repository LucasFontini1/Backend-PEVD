from django.conf import settings
from django.db import models


class CustomerAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_addresses')
    label = models.CharField(max_length=80, default='Principal')
    zip_code = models.CharField(max_length=8)
    street = models.CharField(max_length=180)
    number = models.CharField(max_length=24)
    complement = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=2)

    class Meta:
        ordering = ['id']
