from rest_framework import viewsets, status, decorators
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import ProductVariant

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    # Mixin de Ingeniería para obtener o crear el carrito actual (Guest/User)
    def get_object(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            return cart
        else:
            # Lógica de sesión para invitados (usando session_key de Django)
            if not self.request.session.session_key:
                self.request.session.create()
            
            session_id = self.request.session.session_key
            cart, created = Cart.objects.get_or_create(id=session_id)
            return cart

    # Reemplazamos 'list' y 'retrieve' para que siempre devuelvan el carrito actual
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # ACCIÓN: Añadir item al carrito
    @decorators.action(detail=False, methods=['POST'])
    def add_item(self, request):
        cart = self.get_object()
        product_variant_id = request.data.get('product_variant_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_variant_id:
            return Response({'error': 'product_variant_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(id=product_variant_id)
        except ProductVariant.DoesNotExist:
            return Response({'error': 'Variant not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validación de Stock técnica
        if product_variant.stock < quantity:
            return Response({'error': f'Only {product_variant.stock} units available'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear o actualizar item
        item, created = CartItem.objects.get_or_create(cart=cart, product_variant=product_variant)
        if not created:
            # Si ya existía, validamos stock acumulado
            if product_variant.stock < (item.quantity + quantity):
                return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity += quantity
        else:
            item.quantity = quantity
        
        item.save()
        cart.save() # Actualiza updated_at

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    # ACCIÓN: Actualizar cantidad de un item
    @decorators.action(detail=False, methods=['PATCH'])
    def update_item_quantity(self, request):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity'))

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            item.delete()
        else:
            if item.product_variant.stock < quantity:
                 return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = quantity
            item.save()
            
        cart.save()
        return Response(CartSerializer(cart).data)

    # ACCIÓN: Eliminar item
    @decorators.action(detail=False, methods=['DELETE'])
    def remove_item(self, request):
        cart = self.get_object()
        item_id = request.data.get('item_id')

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
            cart.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)