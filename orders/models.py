import uuid
from django.conf import settings
from django.db import models

from core.models import TimestampedModel
from products.models import ProductVariant


class OrderStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente de Pago"
    PAID = "PAID", "Pagado"
    SHIPPED = "SHIPPED", "Enviado"
    DELIVERED = "DELIVERED", "Entregado"
    CANCELLED = "CANCELLED", "Cancelado"


class Order(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    # Datos del receptor del envio
    shipping_name = models.CharField(max_length=100, verbose_name="Quién recibe")
    shipping_dni = models.CharField(max_length=15, verbose_name="DNI de quien recibe")
    shipping_phone = models.CharField(max_length=20)

    # Dirección de Envío (Copiada de accounts.Address)
    shipping_address_line_1 = models.CharField(max_length=255)
    shipping_address_line_2 = models.CharField(max_length=255)
    shipping_reference = models.TextField(blank=True, null=True)
    shipping_district = models.CharField(max_length=100)
    shipping_province = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=10)

    # Datos de facturación
    billing_name = models.CharField(
        max_length=100, verbose_name="Razón Social o Nombre"
    )
    billing_id_number = models.CharField(max_length=15, verbose_name="DNI o RUC")
    billing_address = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Orden {self.id} - {self.shipping_name}"


class OrderItem(TimestampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

    # El precio se guarda aquí para el histórico
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Item {self.id} de Orden {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity


class Cart(TimestampedModel):
    # ID único y oculto para sesiones de invitado, ForeignKey para usuarios
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='carts', 
        null=True, 
        blank=True
    )
    
    class Meta:
        ordering = ['-updated_at']

    # Lógica de negocio (como en tu imagen b59d69)
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())
    
    def __str__(self):
        return f"Cart {self.id} - User: {self.user or 'Guest'}"

class CartItem(TimestampedModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product_variant')

    # Lógica de negocio (como en tu imagen b59d44)
    @property
    def subtotal(self):
        # Usamos el precio dinámico de la variante
        return self.product_variant.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} ({self.product_variant.sku})"
