from typing import Dict, Optional
from backend.app.security_engine.encryption.crypt import AES256PayloadEncryptor

class SecretVaultManager:
    """Secure credentials vault preventing API token/key leakage in logs."""

    def __init__(self):
        self._vault: Dict[str, str] = {}
        self.encryptor = AES256PayloadEncryptor()

    def store_secret(self, key_id: str, raw_secret: str) -> bool:
        """Stores encrypted secret payload securely inside the vault."""
        encrypted = self.encryptor.encrypt_payload(raw_secret)
        self._vault[key_id.lower()] = encrypted
        return True

    def retrieve_secret(self, key_id: str) -> Optional[str]:
        """Retrieves and decrypts secret payload from the vault."""
        encrypted = self._vault.get(key_id.lower())
        if not encrypted:
            return None
        return self.encryptor.decrypt_payload(encrypted)

    def redact_secrets_from_log(self, log_message: str) -> str:
        """Sanitizes text logs by redacting raw secret occurrences."""
        redacted = log_message
        for key_id in self._vault.keys():
            raw_secret = self.retrieve_secret(key_id)
            if raw_secret and raw_secret in redacted:
                redacted = redacted.replace(raw_secret, "********")
        return redacted
