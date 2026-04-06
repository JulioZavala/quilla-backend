from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    # Campo para el color en la interfaz
    color_hex = models.CharField(
        max_length=7,
        default="#6c757d",
        help_text="Código hexadecimal para la UI (ej: #444444)",
    )

    def __str__(self):
        return self.name


# User por defecto de DJango.
class User(AbstractUser):
    """
    Centraliza la autenticación y los roles base.
    """

    # Usamos booleanos para identificar roles rápidamente
    is_customer = models.BooleanField(default=True)
    is_staff_member = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, related_name="users", blank=True)

    # Campo para auditoría o seguridad (opcional)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_verified(self):
        # Busca si el email principal del usuario está verificado
        from allauth.account.models import EmailAddress
        return EmailAddress.objects.filter(user=self, email=self.email, verified=True).exists()

    def __str__(self):
        return self.email or self.username


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer",
    )

    # campos apellido parterno y apellido materno
    first_names = models.CharField(max_length=150, verbose_name="Nombres")
    paternal_last_name = models.CharField(
        max_length=100, verbose_name="Apellido Paterno"
    )
    maternal_last_name = models.CharField(
        max_length=100, verbose_name="Apellido Materno"
    )

    # Documento de Identidad
    DNI = "DNI"
    RUC = "RUC"
    CE = "CE"
    PASSPORT = "PAS"

    DOCUMENT_TYPE_CHOICES = [
        (DNI, "DNI - Documento Nacional de Identidad"),
        (RUC, "RUC - Registro Único de Contribuyentes"),
        (CE, "Carnet de Extranjería"),
        (PASSPORT, "Pasaporte"),
    ]

    document_type = models.CharField(
        max_length=3,
        choices=DOCUMENT_TYPE_CHOICES,
        default=DNI,
        verbose_name="Tipo de Documento",
    )

    document_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,  # <--- Permite que sea nulo en la BD
        blank=True,  # <--- Permite que el formulario lo deje vacío
        verbose_name="Número de Documento",
    )

    # Informacion y contacto
    phone_number = models.CharField(max_length=15, verbose_name="Teléfono/Celular")
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de Nacimiento"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    def get_full_name(self):
        return f"{self.first_names} {self.paternal_last_name} {self.maternal_last_name}"

    def __str__(self):
        return f"{self.document_number} - {self.get_full_name()}"


class Address(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="addresses"
    )

    # Address details
    address_line_1 = models.CharField(
        max_length=255, verbose_name="Dirección (Av/Calle/Jr)"
    )
    address_line_2 = models.CharField(
        max_length=255, blank=True, verbose_name="Dpto/Int/Urb (Opcional)"
    )
    reference = models.TextField(blank=True, verbose_name="Referencia")

    # Peruvian location structure
    district = models.CharField(max_length=100, verbose_name="Distrito")
    province = models.CharField(max_length=100, verbose_name="Provincia")
    state = models.CharField(max_length=100, verbose_name="Departamento")
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name="Código Postal"
    )

    # Logic flags
    is_default = models.BooleanField(default=False, verbose_name="Dirección Principal")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.address_line_1}, {self.district}"

    def save(self, *args, **kwargs):
        # Si esta dirección es principal, quitamos el principal a las otras del cliente
        if self.is_default:
            Address.objects.filter(customer=self.customer, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)
