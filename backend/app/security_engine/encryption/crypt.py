import base64
from typing import Union

class AES256PayloadEncryptor:
    """Mock AES-256 payload encryption & decryption simulation for memory databases."""

    def __init__(self, key: str = "JARVIS_SECRET_KEY"):
        self.key = key

    def encrypt_payload(self, raw_text: str) -> str:
        """Simulates AES-256 base64 payload encryption cycle."""
        # Simple cipher simulation: reverse string + base64 encoding
        reversed_text = raw_text[::-1]
        encoded = base64.b64encode(reversed_text.encode("utf-8")).decode("utf-8")
        return f"enc__{encoded}"

    def decrypt_payload(self, encrypted_text: str) -> str:
        """Simulates AES-256 base64 payload decryption cycle."""
        if not encrypted_text.startswith("enc__"):
            return encrypted_text
        
        encoded = encrypted_text[5:]
        decoded = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
        return decoded[::-1]
