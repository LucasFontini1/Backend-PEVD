from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import ShopBrand
from catalog.serializers import ShopBrandAdminSerializer, ShopBrandPublicSerializer
from core.permissions import IsActiveSuperUser
from support.services.audit import record_action


class PublicBrandView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        brand = ShopBrand.objects.first() or ShopBrand()
        return Response(ShopBrandPublicSerializer(brand).data)


class AdminBrandView(APIView):
    permission_classes = [IsActiveSuperUser]

    def get(self, request):
        brand = ShopBrand.objects.first() or ShopBrand()
        return Response(ShopBrandAdminSerializer(brand).data)

    def patch(self, request):
        brand = ShopBrand.objects.first() or ShopBrand()
        serializer = ShopBrandAdminSerializer(brand, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        brand = serializer.save()
        record_action(request.user, 'shop.update', brand)
        return Response(serializer.data)
