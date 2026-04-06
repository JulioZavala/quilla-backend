from django.db import models


class TimestampedModel(models.Model):
    """
    Clase base abstracta para que todos nuestros modelos tengan seguimiento de tiempo automáticamente.
    """

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )

    class Meta:
        abstract = True  # Para que no se cree una tabla 'core_timestampedmodel'
