"""Access em JSON; refresh em cookie HttpOnly com rotação e revogação."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.views.token import EmailOrUsernameTokenSerializer

COOKIE_NAME = 'pv_refresh'


def set_refresh_cookie(response, token):
    response.set_cookie(
        COOKIE_NAME, token, httponly=True, secure=not settings.DEBUG,
        samesite='Lax', max_age=7 * 24 * 60 * 60, path='/api/token/',
    )


class AccessResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


@extend_schema(request=EmailOrUsernameTokenSerializer, responses={200: AccessResponseSerializer})
class CookieLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get_authenticate_header(self, request):
        return 'Bearer realm="api"'

    def post(self, request):
        serializer = EmailOrUsernameTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        response = Response({'access': serializer.validated_data['access']})
        set_refresh_cookie(response, serializer.validated_data['refresh'])
        get_token(request)
        response.set_cookie(
            'pv_csrf', request.META['CSRF_COOKIE'], secure=not settings.DEBUG,
            httponly=False, samesite='Lax', path='/',
        )
        return response


@method_decorator(csrf_protect, name='dispatch')
@extend_schema(request=None, responses={200: AccessResponseSerializer})
class CookieRefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw = request.COOKIES.get(COOKIE_NAME)
        if not raw:
            return Response({'detail': 'Sessão expirada.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            old_token = RefreshToken(raw)
            user = get_user_model().objects.get(pk=old_token['user_id'], is_active=True)
            old_token.blacklist()
            new_token = RefreshToken.for_user(user)
        except (TokenError, KeyError, ValueError, get_user_model().DoesNotExist):
            return Response({'detail': 'Sessão inválida.'}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({'access': str(new_token.access_token)})
        set_refresh_cookie(response, str(new_token))
        return response


@method_decorator(csrf_protect, name='dispatch')
@extend_schema(request=None, responses={204: OpenApiResponse(description='Sessão encerrada')})
class CookieLogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        raw = request.COOKIES.get(COOKIE_NAME)
        if raw:
            try:
                RefreshToken(raw).blacklist()
            except TokenError:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(COOKIE_NAME, path='/api/token/', samesite='Lax')
        response.delete_cookie('pv_csrf', path='/', samesite='Lax')
        return response
