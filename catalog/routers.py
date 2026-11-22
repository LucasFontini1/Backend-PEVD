from rest_framework.routers import DefaultRouter

from catalog.views import (
    CategoryAdminViewSet, CategoryPublicViewSet, OptionAdminViewSet, OptionGroupAdminViewSet,
    ProductAdminViewSet, ProductImageAdminViewSet, ProductPublicViewSet,
)

public_router = DefaultRouter()
public_router.register('categories', CategoryPublicViewSet, basename='categories')
public_router.register('products', ProductPublicViewSet, basename='products')

admin_router = DefaultRouter()
admin_router.register('categories', CategoryAdminViewSet, basename='admin-categories')
admin_router.register('products', ProductAdminViewSet, basename='admin-products')
admin_router.register('product-images', ProductImageAdminViewSet, basename='admin-product-images')
admin_router.register('option-groups', OptionGroupAdminViewSet, basename='admin-option-groups')
admin_router.register('options', OptionAdminViewSet, basename='admin-options')

# Marca exposta em endpoints individuais pelo app.urls, não pelo Router.
