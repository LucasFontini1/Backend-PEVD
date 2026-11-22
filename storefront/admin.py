from django.contrib import admin

from storefront.models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'link_path', 'is_active', 'sort_order']
    list_filter = ['is_active']
