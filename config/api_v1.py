"""
API v1 endpoints.

This module contains version 1 of the API endpoints.
Future versions (v2, v3, etc.) can be added in separate modules.
"""

from django.urls import path

from config.api_views import api_health_check, api_user_info
from config.sso_auth import sso_authenticate

app_name = "api_v1"

urlpatterns = [
    # SSO Authentication for Mobile Apps
    path("sso/authenticate/", sso_authenticate, name="sso_authenticate"),
    # Example API endpoints
    path("user/", api_user_info, name="api_user_info"),
    path("health/", api_health_check, name="api_health_check"),
]

