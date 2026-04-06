from django_filters import rest_framework as filters
from .models import Product, Category

class ProductFilter(filters.FilterSet):
    # Definimos el filtro de slug de forma personalizada
    category__slug = filters.CharFilter(method='filter_by_category_hierarchy')

    class Meta:
        model = Product
        fields = ['category__slug', 'collections__slug']

    def filter_by_category_hierarchy(self, queryset, name, value):
        try:
            # 1. Buscamos la categoría raíz o padre por el slug enviado
            category = Category.objects.get(slug=value)
            
            # 2. Usamos MPTT para obtener esa categoría y todas sus hijas (recursivo)
            descendants = category.get_descendants(include_self=True)
            
            # 3. Filtramos los productos que pertenezcan a cualquiera de esas categorías
            return queryset.filter(category__in=descendants)
        except Category.DoesNotExist:
            # Si el slug no existe, devolvemos el queryset original o vacío
            return queryset.none()