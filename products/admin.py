from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin

from .models import (
    Attribute,
    AttributeValue,
    Category,
    Collection,
    Product,
    ProductImage,
    ProductVariant,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_url", "preview", "related_attributes", "is_feature", "sort_order")
    readonly_fields = ("preview",)
    filter_horizontal = ("related_attributes",)

    def preview(self, obj):
        if obj.image_url:
            # Mostramos una miniatura pequeña en el admin
            return format_html(
                '<img src="{}" style="width: 80px; height: auto; border-radius: 5px;" />',
                obj.image_url,
            )
        return "No image"


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ("attribute_values",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "get_category_slug", "get_price_range", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductVariantInline, ProductImageInline]

    # Filtros por Categoría o por Colección (Ofertas, etc)
    list_filter = ("category", "collections", "created_at")

    search_fields = ("name", "category__name")

    # Para seleccionar múltiples colecciones
    filter_horizontal = ("collections",)

    def get_category_slug(self, obj):
        # Accedemos al objeto relacionado y traemos su slug
        return obj.category.slug if obj.category else "-"

    get_category_slug.short_description = "Slug Categoría"
    get_category_slug.admin_order_field = (
        "category__slug"  # Permite ordenar por esta columna
    )

    # def get_price_range(self, obj):
    #     # Un detalle extra para ver los precios rápido en la lista
    #     variants = obj.variants.all()
    #     if variants:
    #         prices = [v.price for v in variants]
    #         return f"S/ {min(prices)} - S/ {max(prices)}"
    #     return "Sin precio"

    # get_price_range.short_description = "Rango de Precios"


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ("tree_actions", "indented_title", "slug", "parent")
    list_display_links = ("indented_title",)
    readonly_fields = ("slug",)
    search_fields = ("name",)


admin.site.register(Attribute)
admin.site.register(AttributeValue)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}
