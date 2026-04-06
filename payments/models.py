from django.db import models

from core.models import TimestampedModel
from orders.models import Order


class PaymentMethod(models.TextChoices):
    CREDIT_CARD = "CARD", "Tarjeta de Crédito/Débito"
    TRANSFER = "TRANSFER", "Transferencia Bancaria"
    YAPE_PLIN = "E-WALLET", "Yape / Plin"


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    SUCCESS = "SUCCESS", "Aprobado"
    FAILED = "FAILED", "Fallido"
    REFUNDED = "REFUNDED", "Reembolsado"


class Transaction(TimestampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")

    # ID externo que devuelve la pasarela (Ej: Culqi Order ID)
    external_id = models.CharField(max_length=100, unique=True, blank=True, null=True)

    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(
        verbose_name="Fecha efectiva del pago",
        help_text="Fecha y hora exacta que reporta la pasarela de pagos",
    )

    # Para guardar el JSON de respuesta crudo de la pasarela por seguridad
    gateway_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Pago {self.id} - Orden {self.order.id} ({self.status})"
