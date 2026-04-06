# products/views.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer
from .filters import ProductFilter

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().prefetch_related('images', 'variants', 'category')
    lookup_field = 'slug' # Para que las URLs sean /products/morral-cuero/
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['category__slug', 'collections__slug']
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['created_at', 'variants__price']

    def get_serializer_class(self):
        # Si es la lista (grilla), usamos el serializer liviano
        if self.action == 'list':
            return ProductListSerializer
        # Si es el detalle de un producto, el completo
        return ProductDetailSerializer