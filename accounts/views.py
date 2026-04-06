from rest_framework import generics, permissions
from .models import Customer
from .serializers import CustomerSerializer

class CustomerView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retorna el perfil del usuario autenticado.
        Si por alguna razón el perfil no existe.
        """
        customer, created = Customer.objects.get_or_create(user=self.request.user)
        return customer