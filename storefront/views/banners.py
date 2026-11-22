from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsActiveSuperUser
from storefront.models import Banner
from storefront.serializers import AdminBannerSerializer, PublicBannerSerializer


class BannerPublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PublicBannerSerializer
    queryset = Banner.objects.filter(is_active=True).select_related('image')


class BannerAdminViewSet(viewsets.ModelViewSet):
    permission_classes = [IsActiveSuperUser]
    serializer_class = AdminBannerSerializer
    queryset = Banner.objects.all().select_related('image')

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])
