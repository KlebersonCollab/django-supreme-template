"""Tests for SSO authentication."""

from unittest.mock import Mock, patch

import pytest
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from config.sso_auth import (
    get_or_create_user_from_sso,
    verify_github_token,
    verify_google_token,
    verify_microsoft_token,
)

User = get_user_model()


class SSOAuthTestCase(TestCase):
    """Test SSO authentication."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    @patch("requests.get")
    def test_verify_google_token_valid(self, mock_get):
        """Test Google token verification with valid token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
        }
        mock_get.return_value = mock_response

        result = verify_google_token("valid_token")

        assert result is not None
        assert result["email"] == "test@example.com"
        assert result["id"] == "123456"

    @patch("requests.get")
    def test_verify_google_token_invalid(self, mock_get):
        """Test Google token verification with invalid token."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = verify_google_token("invalid_token")

        assert result is None

    @patch("requests.get")
    def test_verify_github_token_valid(self, mock_get):
        """Test GitHub token verification with valid token."""
        # Mock user endpoint
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            "id": 123456,
            "login": "testuser",
            "name": "Test User",
            "email": "test@example.com",
        }

        # Mock emails endpoint
        mock_emails_response = Mock()
        mock_emails_response.status_code = 200
        mock_emails_response.json.return_value = [{"email": "test@example.com", "primary": True}]

        mock_get.side_effect = [mock_user_response, mock_emails_response]

        result = verify_github_token("valid_token")

        assert result is not None
        assert result["email"] == "test@example.com"
        assert result["id"] == 123456

    @patch("requests.get")
    def test_verify_microsoft_token_valid(self, mock_get):
        """Test Microsoft token verification with valid token."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123456",
            "mail": "test@example.com",
            "givenName": "Test",
            "surname": "User",
            "userPrincipalName": "test@example.com",
        }
        mock_get.return_value = mock_response

        result = verify_microsoft_token("valid_token")

        assert result is not None
        assert result["mail"] == "test@example.com"

    def test_get_or_create_user_from_sso_new_user(self):
        """Test creating new user from SSO."""
        user_data = {
            "id": "123456",
            "email": "newuser@example.com",
            "name": "New User",
            "given_name": "New",
            "family_name": "User",
        }

        user, created = get_or_create_user_from_sso("google", user_data)

        assert created is True
        assert user.email == "newuser@example.com"
        assert SocialAccount.objects.filter(user=user, provider="google").exists()

    def test_get_or_create_user_from_sso_existing_social_account(self):
        """Test finding existing user by social account."""
        # Create user with social account
        user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
        )
        SocialAccount.objects.create(
            user=user,
            provider="google",
            uid="123456",
            extra_data={},
        )

        user_data = {
            "id": "123456",
            "email": "existing@example.com",
        }

        found_user, created = get_or_create_user_from_sso("google", user_data)

        assert created is False
        assert found_user.id == user.id

    def test_get_or_create_user_from_sso_existing_email(self):
        """Test finding existing user by email and linking social account."""
        user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
        )

        user_data = {
            "id": "123456",
            "email": "existing@example.com",
        }

        found_user, created = get_or_create_user_from_sso("google", user_data)

        assert created is False
        assert found_user.id == user.id
        assert SocialAccount.objects.filter(user=user, provider="google").exists()

    def test_get_or_create_user_from_sso_no_email(self):
        """Test error when SSO provider doesn't return email."""
        user_data = {
            "id": "123456",
            # No email
        }

        with pytest.raises(ValidationError, match="Email is required"):
            get_or_create_user_from_sso("google", user_data)

    @patch("config.sso_auth.verify_google_token")
    def test_sso_authenticate_success(self, mock_verify):
        """Test successful SSO authentication."""
        # Mock token verification
        mock_verify.return_value = {
            "id": "123456",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
        }

        response = self.client.post(
            "/api/sso/authenticate/",
            {"provider": "google", "access_token": "valid_token"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "test@example.com"

    def test_sso_authenticate_missing_provider(self):
        """Test SSO authentication with missing provider."""
        response = self.client.post(
            "/api/sso/authenticate/",
            {"access_token": "token"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_sso_authenticate_missing_token(self):
        """Test SSO authentication with missing token."""
        response = self.client.post(
            "/api/sso/authenticate/",
            {"provider": "google"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sso_authenticate_invalid_provider(self):
        """Test SSO authentication with invalid provider."""
        response = self.client.post(
            "/api/sso/authenticate/",
            {"provider": "invalid", "access_token": "token"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("config.sso_auth.verify_google_token")
    def test_sso_authenticate_invalid_token(self, mock_verify):
        """Test SSO authentication with invalid token."""
        mock_verify.return_value = None

        response = self.client.post(
            "/api/sso/authenticate/",
            {"provider": "google", "access_token": "invalid_token"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    @patch("requests.get")
    def test_verify_github_token_no_email_in_profile(self, mock_get):
        """Test GitHub token verification when email is not in profile."""
        # Mock user endpoint (no email)
        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            "id": 123456,
            "login": "testuser",
            "name": "Test User",
            # No email
        }

        # Mock emails endpoint
        mock_emails_response = Mock()
        mock_emails_response.status_code = 200
        mock_emails_response.json.return_value = [{"email": "test@example.com", "primary": True}]

        mock_get.side_effect = [mock_user_response, mock_emails_response]

        result = verify_github_token("valid_token")

        assert result is not None
        assert result["email"] == "test@example.com"
