"""
Tests for secrets management module.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from config.secrets import (
    AZURE_AVAILABLE,
    GCP_AVAILABLE,
    VAULT_AVAILABLE,
    SecretsManager,
    get_secret,
    get_secrets_dict,
)


class TestSecretsManager:
    """Test SecretsManager class."""

    def test_init_with_env_provider(self):
        """Test initialization with env provider."""
        manager = SecretsManager(provider="env")
        assert manager.provider == "env"
        assert manager._client is None

    def test_get_secret_env_provider(self, monkeypatch):
        """Test getting secret from environment variables."""
        monkeypatch.setenv("TEST_SECRET", "test-value")
        manager = SecretsManager(provider="env")
        result = manager.get_secret("TEST_SECRET")
        assert result == "test-value"

    def test_get_secret_env_provider_not_found(self):
        """Test getting secret from env when not found."""
        manager = SecretsManager(provider="env")
        result = manager.get_secret("NONEXISTENT_SECRET", default="default-value")
        assert result == "default-value"

    @patch("config.secrets.AWS_AVAILABLE", True)
    @patch("config.secrets.boto3")
    def test_init_aws_provider(self, mock_boto3):
        """Test initialization with AWS provider."""
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        os.environ["AWS_SECRETS_REGION"] = "us-east-1"
        manager = SecretsManager(provider="aws")
        assert manager.provider == "aws"
        assert manager._client == mock_client
        mock_boto3.client.assert_called_once_with("secretsmanager", region_name="us-east-1")

    @patch("config.secrets.AWS_AVAILABLE", False)
    def test_init_aws_provider_not_available(self):
        """Test initialization with AWS provider when boto3 not available."""
        with pytest.raises(ImportError, match="boto3 is required"):
            SecretsManager(provider="aws")

    @pytest.mark.skip(reason="Requires google-cloud-secret-manager to be installed")
    def test_init_gcp_provider(self):
        """Test initialization with GCP provider."""
        # Skip if library not available
        if not GCP_AVAILABLE:
            pytest.skip("google-cloud-secret-manager not installed")
        os.environ["GCP_PROJECT_ID"] = "test-project"
        manager = SecretsManager(provider="gcp")
        assert manager.provider == "gcp"

    @patch("config.secrets.GCP_AVAILABLE", False)
    def test_init_gcp_provider_not_available(self):
        """Test initialization with GCP provider when library not available."""
        with pytest.raises(ImportError, match="google-cloud-secret-manager"):
            SecretsManager(provider="gcp")

    @pytest.mark.skip(reason="Requires azure-keyvault-secrets to be installed")
    def test_init_azure_provider(self):
        """Test initialization with Azure provider."""
        # Skip if library not available
        if not AZURE_AVAILABLE:
            pytest.skip("azure-keyvault-secrets not installed")
        os.environ["AZURE_KEY_VAULT_URL"] = "https://test.vault.azure.net/"
        manager = SecretsManager(provider="azure")
        assert manager.provider == "azure"

    @patch("config.secrets.AZURE_AVAILABLE", False)
    def test_init_azure_provider_not_available(self):
        """Test initialization with Azure provider when library not available."""
        with pytest.raises(ImportError, match="azure-keyvault-secrets"):
            SecretsManager(provider="azure")

    @pytest.mark.skip(reason="Requires hvac to be installed")
    def test_init_vault_provider(self):
        """Test initialization with Vault provider."""
        # Skip if library not available
        if not VAULT_AVAILABLE:
            pytest.skip("hvac not installed")
        os.environ["VAULT_TOKEN"] = "test-token"
        manager = SecretsManager(provider="vault")
        assert manager.provider == "vault"

    @patch("config.secrets.VAULT_AVAILABLE", False)
    def test_init_vault_provider_not_available(self):
        """Test initialization with Vault provider when library not available."""
        with pytest.raises(ImportError, match="hvac"):
            SecretsManager(provider="vault")

    def test_init_unknown_provider(self):
        """Test initialization with unknown provider."""
        with pytest.raises(ValueError, match="Unknown secrets provider"):
            SecretsManager(provider="unknown")

    @patch("config.secrets.AWS_AVAILABLE", True)
    @patch("config.secrets.boto3")
    def test_get_aws_secret(self, mock_boto3):
        """Test getting secret from AWS Secrets Manager."""
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {"SecretString": "test-secret-value"}
        mock_boto3.client.return_value = mock_client
        os.environ["AWS_SECRETS_REGION"] = "us-east-1"

        manager = SecretsManager(provider="aws")
        result = manager.get_secret("test-secret")
        assert result == "test-secret-value"

    @patch("config.secrets.AWS_AVAILABLE", True)
    @patch("config.secrets.boto3")
    def test_get_aws_secret_json(self, mock_boto3):
        """Test getting JSON secret from AWS Secrets Manager."""
        import json

        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            "SecretString": json.dumps({"key": "value"})
        }
        mock_boto3.client.return_value = mock_client
        os.environ["AWS_SECRETS_REGION"] = "us-east-1"

        manager = SecretsManager(provider="aws")
        result = manager.get_secret("test-secret")
        assert result == "value"  # Returns first value if single key-value

    def test_get_secrets_dict(self, monkeypatch):
        """Test getting secrets as dictionary."""
        import json

        monkeypatch.setenv("TEST_SECRET_JSON", json.dumps({"key1": "value1", "key2": "value2"}))
        manager = SecretsManager(provider="env")
        result = manager.get_secrets_dict("TEST_SECRET_JSON")
        assert result == {"key1": "value1", "key2": "value2"}

    def test_get_secrets_dict_non_json(self, monkeypatch):
        """Test getting non-JSON secret as dictionary."""
        monkeypatch.setenv("TEST_SECRET", "simple-value")
        manager = SecretsManager(provider="env")
        result = manager.get_secrets_dict("TEST_SECRET")
        assert result == {"value": "simple-value"}


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_get_secret_function(self, monkeypatch):
        """Test get_secret convenience function."""
        monkeypatch.setenv("TEST_SECRET", "test-value")
        result = get_secret("TEST_SECRET")
        assert result == "test-value"

    def test_get_secrets_dict_function(self, monkeypatch):
        """Test get_secrets_dict convenience function."""
        import json

        monkeypatch.setenv("TEST_SECRET_JSON", json.dumps({"key": "value"}))
        result = get_secrets_dict("TEST_SECRET_JSON")
        assert result == {"key": "value"}

