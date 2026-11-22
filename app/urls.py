from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from core.views import CustomTokenVerifyView, UserViewSet
from core.views.commercial import CommercialAccessView
from core.views.registration import StoreRegistrationView
from core.views.session import CookieLoginView, CookieLogoutView, CookieRefreshView
from uploader.router import router as uploader_router

router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuarios')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/token/', CookieLoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', CookieLogoutView.as_view(), name='token_logout'),
    path('api/token/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),
    path('api/registro/', StoreRegistrationView.as_view(), name='user_registration'),
    path('api/admin/access/', CommercialAccessView.as_view(), name='commercial_access'),
    path('api/media/', include(uploader_router.urls)),
    path('api/', include(router.urls)),
]
if settings.DEBUG and not settings.CLOUDINARY_URL:
    urlpatterns += static(settings.MEDIA_ENDPOINT, document_root=settings.MEDIA_ROOT)
