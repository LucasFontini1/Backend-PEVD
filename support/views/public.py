from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from support.models import FAQ
from support.serializers.contact import ContactSerializer, PublicFAQSerializer


class PublicFAQViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PublicFAQSerializer
    queryset = FAQ.objects.filter(published=True)


class ContactView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('website'):
            return Response({'message': 'Solicitação recebida.'}, status=status.HTTP_202_ACCEPTED)
        serializer.save()
        return Response({'message': 'Solicitação recebida.'}, status=status.HTTP_202_ACCEPTED)
