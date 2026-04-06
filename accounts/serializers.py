from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Customer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    # Extraemos solo lo necesario de Customer para el Header
    first_names = serializers.CharField(
        source="customer.first_names", read_only=True, default=""
    )
    paternal_last_name = serializers.CharField(
        source="customer.paternal_last_name", read_only=True, default=""
    )
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",  # Para el @username o ID de usuario
            "email",
            "first_names",  # Directo para el Header
            "paternal_last_name",  # Directo para el Header
            "is_staff",
            "is_staff_member",
            "is_customer",
            "is_verified",
        )
        read_only_fields = fields  # En el Header todo es de lectura


class CustomRegisterSerializer(RegisterSerializer):
    # Definimos el username como opcional en el Serializer para que no de error
    username = serializers.CharField(required=False, allow_blank=True)

    # Definimos el guardado atómico
    @transaction.atomic
    def save(self, request):
        # Obtenemos el email de los datos validados
        email = self.validated_data.get("email")

        # Generamos el username automáticamente (parte antes del @)
        # Si por alguna razón no hay email, usamos un fallback
        generated_username = email.split("@")[0] if email else "user"

        # Lo inyectamos en los datos antes de crear el usuario
        self.validated_data["username"] = generated_username

        # Llamamos al save original de la librería
        user = super().save(request)

        # Seteamos los valores de identidad
        user.is_customer = True
        user.is_staff_member = False
        user.save()

        # Creamos la instancia de Customer vinculada
        # Customer.objects.get_or_create(user=user)
        return user


class CustomerSerializer(serializers.ModelSerializer):
    # Traemos el username y email del usuario (solo lectura) para mostrarlo en el perfil
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    is_email_verified = serializers.BooleanField(
        source="user.is_verified", read_only=True
    )

    class Meta:
        model = Customer
        fields = [
            "username",
            "email",
            "is_email_verified",
            "first_names",
            "paternal_last_name",
            "maternal_last_name",
            "document_type",
            "document_number",
            "phone_number",
            "birth_date",
        ]
        # El username y email no se edita desde aquí, se hereda del User
        read_only_fields = ["email", "username"]
