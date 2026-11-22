from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from core.models import User
from core.serializers.user import UserRegistrationSerializer


class StoreRegistrationSerializer(UserRegistrationSerializer):
    accepted_terms = serializers.BooleanField(write_only=True)

    class Meta(UserRegistrationSerializer.Meta):
        fields = [*UserRegistrationSerializer.Meta.fields, 'accepted_terms']

    def validate_accepted_terms(self, value):
        if not value:
            raise serializers.ValidationError('É necessário aceitar os termos para criar conta.')
        return value

    def create(self, validated_data):
        validated_data.pop('accepted_terms')
        return super().create(validated_data)


@extend_schema(summary='Cadastro de cliente com aceite explícito', request=StoreRegistrationSerializer)
class StoreRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = StoreRegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
