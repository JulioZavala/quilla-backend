from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet # Asegúrate de que el ViewSet esté en orders/views.py

router = DefaultRouter()
# Esto registrará la ruta base como /api/orders/cart/
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]