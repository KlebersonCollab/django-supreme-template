"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from config.api_views import api_health_check, api_user_info
from config.sso_auth import sso_authenticate

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Django Allauth (SSO) - Portal authentication
    path("accounts/", include("allauth.urls")),
    # API Documentation (OpenAPI/Swagger)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API Versioned Endpoints (v1)
    path("api/v1/", include("config.api_v1")),
    # API Authentication (JWT) - Versioned
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair_v1"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh_v1"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify_v1"),
    # Legacy API endpoints (backward compatibility - maps to v1)
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/sso/authenticate/", sso_authenticate, name="sso_authenticate"),
    path("api/user/", api_user_info, name="api_user_info"),
    path("api/health/", api_health_check, name="api_health_check"),
    # REST Framework browsable API
    path("api-auth/", include("rest_framework.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
