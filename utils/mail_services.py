import resend
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        resend.api_key = settings.RESEND_API_KEY
        for message in email_messages:
            # 1. Buscamos si existe una versión HTML en las 'alternatives'
            html_content = None
            if hasattr(message, "alternatives"):
                for content, mime_type in message.alternatives:
                    if mime_type == "text/html":
                        html_content = content
                        break

            # 2. Preparamos los parámetros para Resend
            params = {
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": message.to,
                "subject": message.subject,
                "html": html_content or message.body,
                "text": message.body,  # Siempre enviamos el texto por seguridad
            }
            resend.Emails.send(params)
        return len(email_messages)
