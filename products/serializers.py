# products/serializers.py
from rest_framework import serializers

from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "is_feature", "sort_order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    # Traemos los nombres de los atributos (ej: "M", "Negro")
    attributes = serializers.StringRelatedField(source="attribute_values", many=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "price", "compare_at_price", "stock", "attributes"]


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer liviano para la lista de productos (Grilla)"""

    category_name = serializers.ReadOnlyField(source="category.name")
    category_slug = serializers.ReadOnlyField(source="category.slug")
    images = ProductImageSerializer(many=True, read_only=True)
    price = serializers.DecimalField(
        source="get_base_price", max_digits=10, decimal_places=2, read_only=True
    )
    compare_at_price = serializers.DecimalField(
        source="get_compare_at_price", max_digits=10, decimal_places=2, read_only=True
    )
    price_range = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category_name",
            "category_slug",
            "images",
            "price",
            "compare_at_price",
            "price_range",
        ]

    def get_main_image(self, obj):
        # Buscamos la imagen marcada como 'is_feature' o la primera disponible
        image = obj.images.filter(is_feature=True).first() or obj.images.first()
        if image:
            return image.image_url  # Cloudinary genera la URL automáticamente
        return None

    def get_price_range(self, obj):
        # Reutilizamos la lógica de ingeniería que vimos para el Admin
        return obj.get_price_range()  # Asumiendo que moviste la lógica al Modelo


class ProductDetailSerializer(ProductListSerializer):
    """Serializer completo para la página de producto individual"""

    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    description = serializers.CharField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            "description",
            "images",
            "variants",
        ]
