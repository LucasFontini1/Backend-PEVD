from django.contrib import admin

from catalog.models import Category, Product, ProductImage, ProductOption, ProductOptionGroup, ShopBrand


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductOptionGroupInline(admin.TabularInline):
    model = ProductOptionGroup
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'is_available', 'is_featured']
    list_filter = ['is_active', 'is_available', 'category', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductOptionGroupInline]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'group', 'additional_price', 'is_active']
    list_filter = ['is_active']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'sort_order']


@admin.register(ProductOptionGroup)
class ProductOptionGroupAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'required', 'multiple']


@admin.register(ShopBrand)
class ShopBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_color', 'background_color']

    def has_add_permission(self, request):
        return not ShopBrand.objects.exists()
