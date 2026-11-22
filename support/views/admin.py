from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsActiveSuperUser
from support.models import ContactInquiry, FAQ
from support.serializers.contact import FAQSerializer
from support.services.audit import record_action


class AdminFAQViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveSuperUser]
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()

    def perform_create(self, serializer):
        faq = serializer.save()
        record_action(self.request.user, 'faq.create', faq)

    def perform_update(self, serializer):
        faq = serializer.save()
        record_action(self.request.user, 'faq.update', faq)

    def perform_destroy(self, instance):
        instance.published = False
        instance.save(update_fields=['published'])
        record_action(self.request.user, 'faq.unpublish', instance)


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at', 'handled_at']
        read_only_fields = fields


class AdminContactViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsActiveSuperUser]
    serializer_class = InquirySerializer
    queryset = ContactInquiry.objects.all()

    @action(detail=True, methods=['post'], url_path='mark-handled')
    def mark_handled(self, request, pk=None):
        inquiry = self.get_object()
        inquiry.handled_at = timezone.now()
        inquiry.save(update_fields=['handled_at'])
        record_action(request.user, 'contact.handled', inquiry)
        return Response(InquirySerializer(inquiry).data)
