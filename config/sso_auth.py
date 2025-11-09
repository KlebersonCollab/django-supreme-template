"""
SSO Authentication for Mobile Apps.

This module handles OAuth token verification from mobile apps
and creates/authenticates users, returning Django JWT tokens.
"""

import logging

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

User = get_user_model()


def verify_google_token(access_token: str) -> dict | None:
    """
    Verify Google OAuth token and return user info.

    Args:
        access_token: Google OAuth access token

    Returns:
        User info dict with email, name, etc. or None if invalid
    """
    try:
        import requests

        # Verify token with Google
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error verifying Google token: {e}")
        return None


def verify_github_token(access_token: str) -> dict | None:
    """
    Verify GitHub OAuth token and return user info.

    Args:
        access_token: GitHub OAuth access token

    Returns:
        User info dict with email, name, etc. or None if invalid
    """
    try:
        import requests

        # Get user info
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)

        if response.status_code == 200:
            user_data = response.json()
            # Get email if not in public profile
            if not user_data.get("email"):
                email_response = requests.get(
                    "https://api.github.com/user/emails", headers=headers, timeout=10
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next(
                        (e for e in emails if e.get("primary")), emails[0] if emails else None
                    )
                    if primary_email:
                        user_data["email"] = primary_email.get("email")

            return user_data
        return None
    except Exception as e:
        logger.error(f"Error verifying GitHub token: {e}")
        return None


def verify_microsoft_token(access_token: str) -> dict | None:
    """
    Verify Microsoft OAuth token and return user info.

    Args:
        access_token: Microsoft OAuth access token

    Returns:
        User info dict with email, name, etc. or None if invalid
    """
    try:
        import requests

        # Verify token with Microsoft Graph API
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error verifying Microsoft token: {e}")
        return None


def get_or_create_user_from_sso(provider: str, user_data: dict) -> tuple[User, bool]:
    """
    Get or create user from SSO provider data.

    Args:
        provider: Provider name (google, github, microsoft)
        user_data: User data from provider

    Returns:
        Tuple of (User, created)
    """
    email = user_data.get("email") or user_data.get("mail")
    if not email:
        raise ValidationError("Email is required from SSO provider")

    # Get UID from provider
    uid = str(user_data.get("id") or user_data.get("sub") or user_data.get("userPrincipalName"))

    # Try to find existing social account
    try:
        social_account = SocialAccount.objects.get(provider=provider, uid=uid)
        return social_account.user, False
    except SocialAccount.DoesNotExist:
        pass

    # Try to find user by email
    try:
        user = User.objects.get(email=email)
        # Link social account to existing user
        SocialAccount.objects.create(
            user=user,
            provider=provider,
            uid=uid,
            extra_data=user_data,
        )
        return user, False
    except User.DoesNotExist:
        pass

    # Create new user
    username = user_data.get("login") or user_data.get("name") or email.split("@")[0]
    # Ensure username is unique
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=user_data.get("given_name") or user_data.get("first_name") or "",
        last_name=user_data.get("family_name") or user_data.get("last_name") or "",
    )

    # Adicionar ao grupo "Membro da equipe" por padrão
    from django.contrib.auth.models import Group
    try:
        grupo_membro = Group.objects.get(name="Membro da equipe")
        user.groups.add(grupo_membro)
        logger.info(f"Usuário {user.username} adicionado ao grupo 'Membro da equipe' via SSO API")
    except Group.DoesNotExist:
        # Se o grupo não existir, criar automaticamente
        grupo_membro = Group.objects.create(name="Membro da equipe")
        user.groups.add(grupo_membro)
        logger.info(f"Grupo 'Membro da equipe' criado e usuário {user.username} adicionado via SSO API")

    # Create social account
    SocialAccount.objects.create(
        user=user,
        provider=provider,
        uid=uid,
        extra_data=user_data,
    )

    return user, True


@api_view(["POST"])
@permission_classes([AllowAny])
def sso_authenticate(request):
    """
    Authenticate mobile app user with SSO token.

    Request body:
    {
        "provider": "google|github|microsoft",
        "access_token": "token_from_provider"
    }

    Response:
    {
        "access": "jwt_access_token",
        "refresh": "jwt_refresh_token",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "username": "username",
            "is_new_user": true/false
        }
    }
    """
    provider = request.data.get("provider", "").lower()
    access_token = request.data.get("access_token")

    if not provider or not access_token:
        return Response(
            {"error": "provider and access_token are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if provider not in ["google", "github", "microsoft"]:
        return Response(
            {"error": f"Unsupported provider: {provider}. Supported: google, github, microsoft"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verify token with provider
    user_data = None
    if provider == "google":
        user_data = verify_google_token(access_token)
    elif provider == "github":
        user_data = verify_github_token(access_token)
    elif provider == "microsoft":
        user_data = verify_microsoft_token(access_token)

    if not user_data:
        return Response(
            {"error": "Invalid or expired token"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        # Get or create user
        user, is_new = get_or_create_user_from_sso(provider, user_data)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token_jwt = str(refresh.access_token)
        refresh_token_jwt = str(refresh)

        return Response(
            {
                "access": access_token_jwt,
                "refresh": refresh_token_jwt,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_new_user": is_new,
                },
            },
            status=status.HTTP_200_OK,
        )
    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Error in SSO authentication: {e}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
