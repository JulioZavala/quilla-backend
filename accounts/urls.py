# accounts/urls.py
from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.registration.views import SocialLoginView
from django.urls import include, path, re_path
from rest_framework_simplejwt.views import TokenVerifyView

from .views import CustomerView


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/auth/social/google/callback/"
    client_class = OAuth2Client


urlpatterns = [
    # Se intercepta la confirmación antes de que entre a 'registration/'
    # Esta ruta debe coincidir exactamente con el enlace que llega al correo
    re_path(
        r"^registration/account-confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    # Endpoints base: login, logout, user, password reset
    path("", include("dj_rest_auth.urls")),
    # Registro de nuevos clientes
    path("registration/", include("dj_rest_auth.registration.urls")),
    # Gestión de Tokens JWT
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Google login
    path("google/", GoogleLogin.as_view(), name="google_login"),
    # Aquí podrás añadir rutas propias de Quilla más adelante
    # path('profile/upload-image/', MyProfileImageView.as_view()),
    path("customer/", CustomerView.as_view(), name="customer"),
]
