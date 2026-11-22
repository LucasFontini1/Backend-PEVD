import re
from decimal import Decimal

from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from orders.serializers.manual import ManualOrderSerializer
from orders.services.manual import create_manual_order
from orders.views.report import completed_report

from core.permissions import IsActiveSuperUser
from orders.models import BlockedDate, BusinessHour, DeliveryZone, Order
from orders.serializers.order import AdminOrderSerializer
from orders.services.transitions import confirm_manual_payment, transition_order


class DeliveryZoneSerializer(serializers.ModelSerializer):
    fee = serializers.DecimalField(max_digits=9, decimal_places=2, min_value=Decimal('0.00'))
    minimum_order = serializers.DecimalField(
        max_digits=9, decimal_places=2, min_value=Decimal('0.00'), required=False,
    )

    def validate_zip_prefix(self, value):
        if not re.fullmatch(r'[0-9]{1,8}', value):
            raise serializers.ValidationError('Prefixo CEP deve conter de 1 a 8 dígitos.')
        return value

    class Meta:
        model = DeliveryZone
        fields = '__all__'


class HourSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHour
        fields = '__all__'

    def validate(self, attrs):
        opens = attrs.get('opens_at', getattr(self.instance, 'opens_at', None))
        closes = attrs.get('closes_at', getattr(self.instance, 'closes_at', None))
        if opens is not None and closes is not None and closes <= opens:
            raise serializers.ValidationError('O fechamento deve ser posterior à abertura.')
        return attrs


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedDate
        fields = '__all__'


class AdminBase(viewsets.ModelViewSet):
    permission_classes = [IsActiveSuperUser]


class DeliveryZoneViewSet(AdminBase):
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer


class HourViewSet(AdminBase):
    queryset = BusinessHour.objects.all()
    serializer_class = HourSerializer


class BlockedDateViewSet(AdminBase):
    queryset = BlockedDate.objects.all()
    serializer_class = BlockSerializer


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsActiveSuperUser]
    queryset = Order.objects.all().prefetch_related('items__options', 'history')
    serializer_class = AdminOrderSerializer

    @action(detail=False, methods=['post'], url_path='manual')
    def manual(self, request):
        serializer = ManualOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order, created = create_manual_order(request.user, serializer.validated_data)
        return Response(
            AdminOrderSerializer(self.get_queryset().get(pk=order.pk)).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='completed-report')
    def completed_report(self, request):
        return completed_report(request)

    @action(detail=True, methods=['post'], url_path='transitions')
    def transitions(self, request, pk=None):
        status_value = request.data.get('status')
        reason = request.data.get('reason', '')
        if not isinstance(reason, str) or len(reason) > 250:
            raise serializers.ValidationError({'reason': 'Motivo inválido.'})
        if status_value not in Order.Status.values:
            raise serializers.ValidationError({'status': 'Estado inválido.'})
        order = transition_order(self.get_object().pk, request.user, status_value, reason)
        return Response(AdminOrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        reason = request.data.get('reason')
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 200:
            raise serializers.ValidationError({'reason': 'Informe a confirmação manual do pagamento.'})
        order = confirm_manual_payment(self.get_object().pk, request.user, reason)
        return Response(AdminOrderSerializer(order).data)
