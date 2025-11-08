"""Tests for API views."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class APIViewsTestCase(TestCase):
    """Test API views."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_api_user_info_authenticated(self):
        """Test authenticated user info endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/user/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["user_id"] == self.user.id
        assert response.data["email"] == self.user.email
        assert response.data["username"] == self.user.username

    def test_api_user_info_unauthenticated(self):
        """Test unauthenticated user info endpoint."""
        response = self.client.get("/api/user/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api_health_check_authenticated(self):
        """Test authenticated health check endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ok"
        assert response.data["authenticated_user"] == self.user.email

    def test_api_health_check_unauthenticated(self):
        """Test unauthenticated health check endpoint."""
        response = self.client.get("/api/health/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "ok"
        assert response.data["database"] == "ok"
        assert "authenticated_user" not in response.data
