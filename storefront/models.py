from django.db import models


class Banner(models.Model):
    title = models.CharField(max_length=160)
    subtitle = models.CharField(max_length=220, blank=True)
    image = models.ForeignKey('uploader.Image', on_delete=models.SET_NULL, null=True, blank=True)
    link_path = models.CharField(max_length=220, default='/cardapio')
    is_active = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
