"""Tests for URL configuration."""

from django.test import Client, TestCase


class URLsTestCase(TestCase):
    """Test URL configuration."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_admin_url(self):
        """Test admin URL is accessible."""
        response = self.client.get("/admin/")
        # Should redirect to login or return 200 if already logged in
        assert response.status_code in [200, 302]

    def test_accounts_urls_exist(self):
        """Test allauth URLs are configured."""
        # Test login URL exists
        response = self.client.get("/accounts/login/")
        assert response.status_code in [200, 302]

    def test_api_token_urls_exist(self):
        """Test JWT token URLs are configured."""
        # Test token obtain endpoint exists
        response = self.client.post("/api/token/", {})
        # Should return 400 (bad request) not 404 (not found)
        assert response.status_code != 404

    def test_api_sso_authenticate_url_exists(self):
        """Test SSO authenticate endpoint exists."""
        response = self.client.post("/api/sso/authenticate/", {})
        # Should return 400 (bad request) not 404 (not found)
        assert response.status_code != 404

    def test_api_user_url_exists(self):
        """Test API user endpoint exists."""
        response = self.client.get("/api/user/")
        # Should return 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404

    def test_api_health_url_exists(self):
        """Test API health endpoint exists."""
        response = self.client.get("/api/health/")
        # Should return 401 (unauthorized) not 404 (not found)
        assert response.status_code != 404
