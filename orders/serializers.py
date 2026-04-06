# carts/serializers.py
from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    # Campos dinámicos calculados en el modelo
    subtotal = serializers.ReadOnlyField()
    # Datos extraídos de la variante para el front (Minimalist design needs this)
    product_variant_id = serializers.IntegerField(
        source="product_variant.id", read_only=True
    )
    product_name = serializers.CharField(
        source="product_variant.product.name", read_only=True
    )
    sku = serializers.CharField(source="product_variant.sku", read_only=True)
    price = serializers.DecimalField(
        source="product_variant.price", max_digits=10, decimal_places=2, read_only=True
    )

    # Atributos aplanados (Ej: "Negro / M")
    product_variant_attributes = serializers.SerializerMethodField()

    # Imagen destacada (Cloudinary)
    feature_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product_variant_id",
            "quantity",
            "subtotal",
            "product_name",
            "sku",
            "price",
            "product_variant_attributes",
            "feature_image",
        ]

    def get_product_variant_attributes(self, obj):
        # Se asume que obj.variant.attributes es una lista de strings ['Color: Negro', 'Talla: M']
        try:
            # # Accedemos a la variante a través de la relación definida en tu CartItem
            # variant = obj.product_variant # O obj.product_variant, según tu modelo
        
            # attrs = variant.attribute_values.all()
            
            if obj.product_variant.attribute_values.all():
                return " / ".join(
                    [
                        attr.split(": ")[1]
                        for attr in obj.product_variant.attribute_values
                        if ": " in attr
                    ]
                )
            return ""
        except Exception as e:
            print(f"Error en serializador de Quilla: {e}")
            return ""

    def get_feature_image(self, obj):
        # Obtenemos la imagen marcada como feature del producto asociado a la variante
        feature_img = obj.product_variant.product.images.filter(is_feature=True).first()
        if feature_img:
            return feature_img.image_url  # Cloudinary URL
        return None


class CartSerializer(serializers.ModelSerializer):
    # Campos dinámicos del modelo
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    # Relación de items anidada
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_items", "total_price", "updated_at"]
