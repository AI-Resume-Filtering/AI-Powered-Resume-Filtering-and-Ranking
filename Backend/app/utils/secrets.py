"""
Centralised secrets resolver.

Priority order:
  1. Azure Key Vault   — when AZURE_KEY_VAULT_URL is configured
  2. Environment vars  — always-available fallback

The Azure SDK (``azure-identity`` + ``azure-keyvault-secrets``) is optional.
If not installed, Key Vault lookups are skipped silently and env vars are used.

Usage::

    from app.utils.secrets import get_secret

    smtp_password = get_secret("SMTP_PASSWORD")
    secret_key    = get_secret("SECRET_KEY")

Secret names in Key Vault should match environment variable names, with
underscores replaced by hyphens (Azure Key Vault naming convention):
  SMTP_PASSWORD  →  SMTP-PASSWORD
"""

import logging
import os

logger = logging.getLogger(__name__)

_AZURE_AVAILABLE = False
_kv_client = None  # azure-keyvault-secrets SecretClient

try:
    from azure.identity import DefaultAzureCredential  # type: ignore
    from azure.keyvault.secrets import SecretClient   # type: ignore
    _AZURE_AVAILABLE = True
except ImportError:
    pass


def init_key_vault(vault_url: str) -> None:
    """
    Connect to Azure Key Vault.  Call once from create_app() when
    AZURE_KEY_VAULT_URL is set.  Fails silently if SDK is not installed
    or credentials are unavailable.
    """
    global _kv_client
    if not _AZURE_AVAILABLE or not vault_url:
        return
    try:
        credential = DefaultAzureCredential()
        _kv_client = SecretClient(vault_url=vault_url, credential=credential)
        # Probe connectivity with a cheap call
        _kv_client.get_secret("SECRET-KEY")
        logger.info("Azure Key Vault connected: %s", vault_url)
    except Exception as exc:
        logger.warning(
            "Azure Key Vault unavailable (%s) — using environment variables", exc
        )
        _kv_client = None


def get_secret(name: str, default: str = "") -> str:
    """
    Resolve a secret value.

    1. Try Azure Key Vault (name with underscores → hyphens).
    2. Fall back to ``os.getenv(name, default)``.
    """
    if _kv_client is not None:
        kv_name = name.replace("_", "-")
        try:
            secret = _kv_client.get_secret(kv_name)
            return secret.value or default
        except Exception as exc:
            logger.debug(
                "Key Vault miss for %s (%s) — using env fallback", kv_name, exc
            )

    return os.getenv(name, default)
