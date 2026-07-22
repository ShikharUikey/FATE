from typing import Dict, Any, List, Optional
from backend.app.security_engine.vault.vault import SecretVaultManager

class BrowserAuthManager:
    """Manages browser session cookies, OAuth tokens, and credential vault retrieval."""

    def __init__(self):
        self._cookie_jar: Dict[str, List[Dict[str, Any]]] = {}
        self.vault = SecretVaultManager()

    def store_domain_cookies(self, domain: str, cookies: List[Dict[str, Any]]) -> bool:
        """Saves session cookies for target domain."""
        self._cookie_jar[domain.lower()] = cookies
        return True

    def get_domain_cookies(self, domain: str) -> List[Dict[str, Any]]:
        """Retrieves active session cookies for target domain."""
        return self._cookie_jar.get(domain.lower(), [])

    def fetch_credentials_from_vault(self, service_key: str) -> Optional[str]:
        """Queries Secret Vault for encrypted password/token credentials."""
        return self.vault.retrieve_secret(service_key)
