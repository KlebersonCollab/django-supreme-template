"""
Custom exception handlers for Django REST Framework.

Provides consistent error responses across the API.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.

    Returns consistent error responses with proper status codes.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, it's an unhandled exception
    if response is None:
        logger.exception(f"Unhandled exception: {exc}", exc_info=exc)
        return Response(
            {
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Customize the response data
    custom_response_data = {
        "error": response.data.get("detail", "An error occurred"),
        "status_code": response.status_code,
    }

    # Add field errors if present
    if isinstance(response.data, dict):
        field_errors = {k: v for k, v in response.data.items() if k != "detail"}
        if field_errors:
            custom_response_data["errors"] = field_errors

    response.data = custom_response_data

    return response
