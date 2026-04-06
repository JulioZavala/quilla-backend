from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Address, Customer, Role, User


# 1. Registro del Usuario (Solo datos de acceso/cuenta)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_customer", "is_staff", "is_active")

    # Campos personalizados
    fieldsets = UserAdmin.fieldsets + (
        ("Información de Rol", {"fields": ("is_customer", "is_staff_member")}),
    )


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1


# 2. Registro del Cliente (Datos personales y comerciales)
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "document_number",
        "first_names",
        "paternal_last_name",
        "maternal_last_name",
        "phone_number",
    )
    list_filter = ("document_type",)
    search_fields = (
        "document_number",
        "first_names",
        "paternal_last_name",
        "maternal_last_name",
    )
    ordering = ("paternal_last_name",)

    # Agrupamos los campos para que se vea ordenado
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "user",
                    "first_names",
                    "paternal_last_name",
                    "maternal_last_name",
                    "birth_date",
                )
            },
        ),
        (
            "Identification & Contact",
            {"fields": ("document_type", "document_number", "phone_number")},
        ),
    )
    inlines = [AddressInline]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "color_tag", "description")

    def color_tag(self, obj):
        # Genera un pequeño círculo de color en el Admin
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>',
            obj.color_hex,
            obj.color_hex,
        )

    color_tag.short_description = "Vista Previa Color"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "address_line_1",
        "address_line_2",
        "district",
        "province",
        "state",
        "is_default",
    )
    list_filter = ("state", "province", "district")
    search_fields = ("address_line_1", "customer__user__email")
