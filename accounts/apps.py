from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Importamos las señales para que Django las registre al iniciar la aplicación.
        import accounts.signals  # noqa
