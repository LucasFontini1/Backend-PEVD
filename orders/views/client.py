from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import CustomerAddress, Order
from orders.serializers import AddressSerializer, CheckoutSerializer, OrderSerializer
from orders.services.checkout import create_order, priced_quote, public_quote


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CustomerAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    lookup_field = 'public_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__options', 'history')

    @action(detail=False, methods=['post'], url_path='quote')
    def quote(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(public_quote(priced_quote(request.user, serializer.validated_data)))

    def create(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order, created = create_order(request.user, serializer.validated_data)
        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
