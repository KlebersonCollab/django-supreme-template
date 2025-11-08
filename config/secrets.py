"""
Secrets Management Integration.

Supports multiple secret management providers:
- AWS Secrets Manager
- Google Cloud Secret Manager
- Azure Key Vault
- HashiCorp Vault
- Environment Variables (fallback)
"""

import json
import os
from typing import Any

# Try to import secret management clients (optional dependencies)
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import secretmanager

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    import hvac

    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


class SecretsManager:
    """Unified interface for multiple secret management providers."""

    def __init__(self, provider: str | None = None):
        """
        Initialize secrets manager.

        Args:
            provider: Secret provider ('aws', 'gcp', 'azure', 'vault', 'env').
                       If None, auto-detect from SECRETS_PROVIDER env var.
        """
        self.provider = provider or os.environ.get("SECRETS_PROVIDER", "env").lower()
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate secret management client."""
        if self.provider == "aws":
            self._init_aws()
        elif self.provider == "gcp":
            self._init_gcp()
        elif self.provider == "azure":
            self._init_azure()
        elif self.provider == "vault":
            self._init_vault()
        elif self.provider == "env":
            self._client = None  # Use environment variables directly
        else:
            raise ValueError(f"Unknown secrets provider: {self.provider}")

    def _init_aws(self):
        """Initialize AWS Secrets Manager client."""
        if not AWS_AVAILABLE:
            raise ImportError(
                "boto3 is required for AWS Secrets Manager. Install with: pip install boto3"
            )

        region = os.environ.get("AWS_SECRETS_REGION", os.environ.get("AWS_REGION", "us-east-1"))
        self._client = boto3.client("secretsmanager", region_name=region)

    def _init_gcp(self):
        """Initialize Google Cloud Secret Manager client."""
        if not GCP_AVAILABLE:
            raise ImportError(
                "google-cloud-secret-manager is required. Install with: pip install google-cloud-secret-manager"
            )

        project_id = os.environ.get("GCP_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT"))
        if not project_id:
            raise ValueError("GCP_PROJECT_ID or GOOGLE_CLOUD_PROJECT must be set")

        self._client = secretmanager.SecretManagerServiceClient()
        self._gcp_project = project_id

    def _init_azure(self):
        """Initialize Azure Key Vault client."""
        if not AZURE_AVAILABLE:
            raise ImportError(
                "azure-keyvault-secrets and azure-identity are required. "
                "Install with: pip install azure-keyvault-secrets azure-identity"
            )

        vault_url = os.environ.get("AZURE_KEY_VAULT_URL")
        if not vault_url:
            raise ValueError("AZURE_KEY_VAULT_URL must be set")

        credential = DefaultAzureCredential()
        self._client = SecretClient(vault_url=vault_url, credential=credential)

    def _init_vault(self):
        """Initialize HashiCorp Vault client."""
        if not VAULT_AVAILABLE:
            raise ImportError(
                "hvac is required for HashiCorp Vault. Install with: pip install hvac"
            )

        vault_url = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
        vault_token = os.environ.get("VAULT_TOKEN")

        self._client = hvac.Client(url=vault_url, token=vault_token)

        # Verify connection
        if not self._client.is_authenticated():
            raise ValueError("Vault authentication failed. Check VAULT_TOKEN.")

    def get_secret(self, secret_name: str, default: str | None = None) -> str | None:
        """
        Get a secret value by name.

        Args:
            secret_name: Name of the secret
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        try:
            if self.provider == "aws":
                return self._get_aws_secret(secret_name)
            elif self.provider == "gcp":
                return self._get_gcp_secret(secret_name)
            elif self.provider == "azure":
                return self._get_azure_secret(secret_name)
            elif self.provider == "vault":
                return self._get_vault_secret(secret_name)
            else:  # env
                return os.environ.get(secret_name, default)
        except Exception as e:
            # Log error but return default to prevent app crash
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to get secret '{secret_name}': {e}")
            return default

    def _get_aws_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager."""
        try:
            response = self._client.get_secret_value(SecretId=secret_name)
            secret_string = response["SecretString"]

            # Try to parse as JSON (AWS Secrets Manager often stores JSON)
            try:
                secret_dict = json.loads(secret_string)
                # If it's a dict, return the first value or the whole dict as JSON
                if isinstance(secret_dict, dict) and len(secret_dict) == 1:
                    return list(secret_dict.values())[0]
                return secret_string
            except (json.JSONDecodeError, TypeError):
                return secret_string
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found in AWS Secrets Manager") from e
            raise

    def _get_gcp_secret(self, secret_name: str) -> str:
        """Get secret from Google Cloud Secret Manager."""
        project_id = self._gcp_project
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

        try:
            response = self._client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            if "not found" in str(e).lower():
                raise ValueError(f"Secret '{secret_name}' not found in GCP Secret Manager") from e
            raise

    def _get_azure_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault."""
        try:
            secret = self._client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            if "not found" in str(e).lower() or "NotFound" in str(e):
                raise ValueError(f"Secret '{secret_name}' not found in Azure Key Vault") from e
            raise

    def _get_vault_secret(self, secret_name: str) -> str:
        """Get secret from HashiCorp Vault."""
        mount_point = os.environ.get("VAULT_MOUNT_POINT", "secret")
        secret_path = secret_name

        try:
            # Vault v2 (KV secrets engine v2) uses 'data' path
            if os.environ.get("VAULT_KV_VERSION", "2") == "2":
                response = self._client.secrets.kv.v2.read_secret_version(path=secret_path, mount_point=mount_point)
                secret_data = response["data"]["data"]
                # If single key-value, return value; otherwise return JSON
                if isinstance(secret_data, dict) and len(secret_data) == 1:
                    return list(secret_data.values())[0]
                return json.dumps(secret_data)
            else:
                # Vault v1 (KV secrets engine v1)
                response = self._client.secrets.kv.v1.read_secret(path=secret_path, mount_point=mount_point)
                secret_data = response["data"]
                if isinstance(secret_data, dict) and len(secret_data) == 1:
                    return list(secret_data.values())[0]
                return json.dumps(secret_data)
        except Exception as e:
            if "not found" in str(e).lower():
                raise ValueError(f"Secret '{secret_name}' not found in Vault") from e
            raise

    def get_secrets_dict(self, secret_name: str) -> dict[str, Any]:
        """
        Get multiple secrets as a dictionary.

        Useful when a secret contains multiple key-value pairs (e.g., JSON in AWS Secrets Manager).

        Args:
            secret_name: Name of the secret

        Returns:
            Dictionary of secrets
        """
        secret_value = self.get_secret(secret_name)
        if not secret_value:
            return {}

        try:
            return json.loads(secret_value)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, return as single key-value
            return {"value": secret_value}


# Global secrets manager instance
_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    """Get or create the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


def get_secret(secret_name: str, default: str | None = None) -> str | None:
    """
    Convenience function to get a secret.

    Args:
        secret_name: Name of the secret
        default: Default value if secret not found

    Returns:
        Secret value or default
    """
    return get_secrets_manager().get_secret(secret_name, default)


def get_secrets_dict(secret_name: str) -> dict[str, Any]:
    """
    Convenience function to get secrets as a dictionary.

    Args:
        secret_name: Name of the secret

    Returns:
        Dictionary of secrets
    """
    return get_secrets_manager().get_secrets_dict(secret_name)

