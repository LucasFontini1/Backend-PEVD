from rest_framework.routers import DefaultRouter

from storefront.views.banners import BannerAdminViewSet, BannerPublicViewSet

public_router = DefaultRouter()
public_router.register('banners', BannerPublicViewSet, basename='banners')
admin_router = DefaultRouter()
admin_router.register('banners', BannerAdminViewSet, basename='admin-banners')
