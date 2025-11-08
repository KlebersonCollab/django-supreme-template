"""
Example API views for Django Template.

This file demonstrates how to create protected API endpoints using JWT authentication.
"""

from django.db import connection
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle


@extend_schema(
    summary="Get authenticated user information",
    description="Returns information about the currently authenticated user",
    responses={
        200: OpenApiResponse(
            description="User information",
            response={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "is_staff": {"type": "boolean"},
                    "is_superuser": {"type": "boolean"},
                },
            },
        ),
        401: OpenApiResponse(description="Unauthorized"),
    },
    tags=["Users"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_user_info(request):
    """
    Example protected API endpoint.

    Returns information about the authenticated user.
    Requires JWT token in Authorization header: Bearer <token>
    """
    return Response(
        {
            "user_id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    summary="Health check endpoint",
    description="Check API and database health status",
    responses={
        200: OpenApiResponse(
            description="Service is healthy",
            response={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "database": {"type": "string"},
                    "authenticated_user": {"type": "string"},
                },
            },
        ),
        503: OpenApiResponse(description="Service unavailable"),
    },
    tags=["Health"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])  # Rate limit for health checks
def api_health_check(request):
    """
    Health check endpoint with database verification.

    Useful for monitoring and load balancer health checks.
    """
    # Check database connection
    db_status = "ok"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = f"error: {str(e)}"
        return Response(
            {
                "status": "unhealthy",
                "message": "Database connection failed",
                "database": db_status,
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    response_data = {
        "status": "ok",
        "message": "Service is healthy",
        "database": db_status,
    }

    # Add user info if authenticated
    if request.user.is_authenticated:
        response_data["authenticated_user"] = request.user.email

    return Response(response_data, status=status.HTTP_200_OK)
