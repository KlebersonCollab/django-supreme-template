"""Tests for Django settings configuration."""

from django.test import TestCase


class SettingsTestCase(TestCase):
    """Test Django settings configuration."""

    def test_secret_key_is_set(self):
        """Test that SECRET_KEY is configured."""
        from django.conf import settings

        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, "")

    def test_debug_default(self):
        """Test DEBUG default value."""
        from django.conf import settings

        # In test environment, DEBUG may be False
        self.assertIsInstance(settings.DEBUG, bool)

    def test_allowed_hosts(self):
        """Test ALLOWED_HOSTS configuration."""
        from django.conf import settings

        self.assertIsInstance(settings.ALLOWED_HOSTS, list)

    def test_database_config(self):
        """Test database configuration."""
        from django.conf import settings

        self.assertIn("default", settings.DATABASES)
        self.assertIn("ENGINE", settings.DATABASES["default"])

    def test_installed_apps(self):
        """Test that required apps are installed."""
        from django.conf import settings

        required_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
