from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import CustomerAddress, Order
from orders.serializers import AddressSerializer, CheckoutSerializer, OrderSerializer
from orders.services.checkout import create_order, priced_quote, public_quote
from orders.services.transitions import transition_order


class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return CustomerAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
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

    @action(detail=True, methods=['post'], url_path='cancel-request')
    def cancel_request(self, request, public_id=None):
        order = self.get_object()
        if order.status != Order.Status.WAITING:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'status': 'Cancelamento direto permitido apenas antes da confirmação.'})
        updated = transition_order(order.pk, request.user, Order.Status.CANCELLED, 'Cancelado pelo cliente')
        return Response(OrderSerializer(updated).data)

    def create(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order, created = create_order(request.user, serializer.validated_data)
        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
