from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsActiveSuperUser
from storefront.models import Banner
from storefront.serializers import AdminBannerSerializer, PublicBannerSerializer
from support.services.audit import record_action


class BannerPublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PublicBannerSerializer
    queryset = Banner.objects.filter(is_active=True).select_related('image')


class BannerAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveSuperUser]
    serializer_class = AdminBannerSerializer
    queryset = Banner.objects.all().select_related('image')

    def perform_create(self, serializer):
        banner = serializer.save()
        record_action(self.request.user, 'banner.create', banner)

    def perform_update(self, serializer):
        banner = serializer.save()
        record_action(self.request.user, 'banner.update', banner)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        record_action(self.request.user, 'banner.unpublish', instance)
