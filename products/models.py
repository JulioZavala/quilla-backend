from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

from core.models import TimestampedModel


class Category(MPTTModel, TimestampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre de Categoría")
    slug = models.SlugField(unique=True, blank=True, max_length=150)
    # usamos TreeForeignKey
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Categoría Padre",
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        verbose_name_plural = "Categories"
        # Se asegura que no haya dos categorías con el mismo nombre bajo el mismo padre
        unique_together = ("name", "parent")

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.parent:
                # Si tiene padre, combinamos: "Hombre Billeteras" -> "hombre-billeteras"
                self.slug = slugify(f"{self.parent.name}-{self.name}")
            else:
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Collection(TimestampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre de la Colección")
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(
        max_length=500, blank=True, verbose_name="URL Banner (Cloudinary)"
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attribute(TimestampedModel):
    """Ejemplo: Color, Talla, Tipo de Cuero"""

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class AttributeValue(TimestampedModel):
    """Ejemplo: Negro, XL, Napa Premium"""

    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="values"
    )
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(TimestampedModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    care_instructions = models.TextField(verbose_name="Instrucciones de Cuidado")
    collections = models.ManyToManyField(
        Collection, blank=True, related_name="products"
    )

    def get_price_range(self):
        # Un detalle extra para ver los precios rápido en la lista
        variants = self.variants.all()
        if variants:
            prices = [v.price for v in variants]
            return f"S/ {min(prices)} - S/ {max(prices)}"
        return "Sin precio"

    # Esto le dice al Admin cómo llamar a la columna
    get_price_range.short_description = "Rango de Precios"

    def get_base_price(self):
        """Retorna el precio más bajo entre las variantes"""
        variant = self.variants.order_by('price').first()
        return variant.price if variant else None
    
    def get_compare_at_price(self):
        """Retorna el precio de comparación (tachado) de la variante más barata"""
        variant = self.variants.order_by('price').first()
        # Asumiendo que el campo se llama compare_at_price en ProductVariant
        return getattr(variant, 'compare_at_price', None) if variant else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(TimestampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio de Venta"
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio Original (Tachado)",
    )
    stock = models.PositiveIntegerField(default=0)
    attribute_values = models.ManyToManyField(AttributeValue)

    @property
    def on_sale(self):
        return self.compare_at_price is not None and self.compare_at_price > self.price


class ProductImage(TimestampedModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    # URL del servicio externo
    image_url = models.URLField(max_length=500, verbose_name="URL de Cloudinary")

    # Atributos que definen su apariencia
    # (Ejemplo: Esta foto es para 'Color: Negro' y 'Cuero: Napa')
    related_attributes = models.ManyToManyField(
        AttributeValue, blank=True, related_name="attribute_images"
    )

    is_feature = models.BooleanField(
        default=False, help_text="Define si es la foto principal de portada"
    )
    sort_order = models.PositiveIntegerField(
        default=0, help_text="Orden de aparición en el carrusel"
    )

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Product Image"

    def __str__(self):
        return f"Image {self.id} - {self.product.name}"
