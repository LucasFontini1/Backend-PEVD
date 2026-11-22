from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsActiveSuperUser
from support.models import CustomQuote
from support.serializers.quotes import AdminQuoteSerializer, QuoteProposalSerializer, QuoteRequestSerializer, QuoteSerializer
from support.services.audit import record_action


class ClientQuoteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomQuote.objects.filter(user=self.request.user)

    def create(self, request):
        form = QuoteRequestSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        quote = form.save(user=request.user)
        return Response(QuoteSerializer(quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='accept')
    @transaction.atomic
    def accept(self, request, pk=None):
        quote = CustomQuote.objects.select_for_update().filter(pk=pk, user=request.user).first()
        if not quote:
            raise NotFound()
        if quote.status != CustomQuote.Status.PROPOSED or quote.valid_until <= timezone.now():
            raise ValidationError({'status': 'Proposta indisponível ou vencida.'})
        quote.status = CustomQuote.Status.ACCEPTED
        quote.accepted_at = timezone.now()
        quote.save(update_fields=['status', 'accepted_at', 'updated_at'])
        record_action(request.user, 'quote.accept', quote)
        return Response(QuoteSerializer(quote).data)

    @action(detail=True, methods=['post'], url_path='decline')
    @transaction.atomic
    def decline(self, request, pk=None):
        quote = CustomQuote.objects.select_for_update().filter(pk=pk, user=request.user).first()
        if not quote:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        if quote.status != CustomQuote.Status.PROPOSED:
            raise ValidationError({'status': 'Sem proposta pendente.'})
        quote.status = CustomQuote.Status.DECLINED
        quote.save(update_fields=['status', 'updated_at'])
        return Response(QuoteSerializer(quote).data)


class AdminQuoteViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsActiveSuperUser]
    queryset = CustomQuote.objects.all()
    serializer_class = AdminQuoteSerializer

    @action(detail=True, methods=['post'], url_path='close')
    @transaction.atomic
    def close(self, request, pk=None):
        quote = CustomQuote.objects.select_for_update().filter(pk=pk).first()
        if quote is None:
            raise NotFound()
        if quote.status not in (CustomQuote.Status.REQUESTED, CustomQuote.Status.PROPOSED):
            raise ValidationError({'status': 'Esta proposta já está encerrada.'})
        quote.status = CustomQuote.Status.DECLINED
        quote.save(update_fields=['status', 'updated_at'])
        record_action(request.user, 'quote.close', quote)
        return Response(QuoteSerializer(quote).data)

    @action(detail=True, methods=['post'], url_path='propose')
    @transaction.atomic
    def propose(self, request, pk=None):
        quote = CustomQuote.objects.select_for_update().filter(pk=pk).first()
        if quote is None:
            from rest_framework.exceptions import NotFound
            raise NotFound()
        if quote.status not in [CustomQuote.Status.REQUESTED, CustomQuote.Status.PROPOSED]:
            raise ValidationError({'status': 'Não é possível alterar esta proposta.'})
        serializer = QuoteProposalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for key, value in serializer.validated_data.items():
            setattr(quote, key, value)
        quote.status = CustomQuote.Status.PROPOSED
        quote.save(update_fields=['proposed_price', 'proposed_details', 'valid_until', 'status', 'updated_at'])
        record_action(request.user, 'quote.propose', quote)
        return Response(QuoteSerializer(quote).data)
