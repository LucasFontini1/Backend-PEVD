from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import BusinessHour


class ScheduleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response([
            {
                'weekday': item.weekday, 'opens_at': item.opens_at.isoformat(),
                'closes_at': item.closes_at.isoformat(), 'pickup_enabled': item.pickup_enabled,
                'delivery_enabled': item.delivery_enabled,
            }
            for item in BusinessHour.objects.all()
        ])
