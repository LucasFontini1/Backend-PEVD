from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsActiveSuperUser
from support.models import SupportMessage, SupportTicket
from support.serializers.tickets import (
    AdminReplySerializer, ReplySerializer, TicketCreateSerializer, TicketSerializer,
)
from support.services.audit import record_action


def save_message(ticket, sender, body, next_status):
    SupportMessage.objects.create(ticket=ticket, sender=sender, body=body)
    ticket.status = next_status
    ticket.save(update_fields=['status', 'updated_at'])


class ClientTicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).prefetch_related('messages')

    @transaction.atomic
    def create(self, request):
        serializer = TicketCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        ticket = SupportTicket.objects.create(
            user=request.user, subject=data['subject'], order_id=data.get('order_id'),
        )
        save_message(ticket, request.user, data['message'], SupportTicket.Status.OPEN)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='messages')
    @transaction.atomic
    def messages(self, request, pk=None):
        ticket = SupportTicket.objects.select_for_update().filter(user=request.user, pk=pk).first()
        if not ticket:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        if ticket.status == SupportTicket.Status.CLOSED:
            raise ValidationError({'status': 'Ticket encerrado não aceita novas mensagens.'})
        serializer = ReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        save_message(ticket, request.user, serializer.validated_data['message'], SupportTicket.Status.OPEN)
        return Response(TicketSerializer(ticket).data)


class AdminTicketViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsActiveSuperUser]
    serializer_class = TicketSerializer
    queryset = SupportTicket.objects.all().prefetch_related('messages')

    def get_queryset(self):
        query = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter not in SupportTicket.Status.values:
                raise ValidationError({'status': 'Filtro inválido.'})
            query = query.filter(status=status_filter)
        return query

    @action(detail=True, methods=['post'], url_path='reply')
    @transaction.atomic
    def reply(self, request, pk=None):
        ticket = SupportTicket.objects.select_for_update().filter(pk=pk).first()
        if ticket is None:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        if ticket.status == SupportTicket.Status.CLOSED:
            raise ValidationError({'status': 'Ticket encerrado.'})
        serializer = AdminReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_status = SupportTicket.Status.CLOSED if serializer.validated_data['close'] else SupportTicket.Status.ANSWERED
        save_message(ticket, request.user, serializer.validated_data['message'], next_status)
        record_action(request.user, 'support.reply', ticket)
        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=['post'], url_path='close')
    @transaction.atomic
    def close(self, request, pk=None):
        ticket = SupportTicket.objects.select_for_update().filter(pk=pk).first()
        if ticket is None:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        ticket.status = SupportTicket.Status.CLOSED
        ticket.save(update_fields=['status', 'updated_at'])
        record_action(request.user, 'support.close', ticket)
        return Response(TicketSerializer(ticket).data)
