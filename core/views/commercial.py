from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsActiveSuperUser


class CommercialAccessView(APIView):
    permission_classes = [IsActiveSuperUser]

    @extend_schema(summary='Verificar acesso comercial da conta autenticada')
    def get(self, request):
        return Response({'authorized': True})
