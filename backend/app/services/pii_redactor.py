import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from backend.app.config import settings

class PIIRedactor:
    """
    Handles encrypting and decrypting sensitive Personal Identifiable Information
    at rest in the Database. $0 Cost. Uses app JWT_SECRET as derivation base.
    """
    def __init__(self):
        # Derive a secure 32 URL-safe base64-encoded key from the JWT SECRET
        # It's important the SALT and SECRET stay static for the lifespan of the DB
        salt = b"velos-pii-encryption-salt-2025"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.JWT_SECRET.encode()))
        self.cipher_suite = Fernet(key)

    def encrypt_data(self, plaintext: str) -> str:
        """Encrypts a string of PII text"""
        if not plaintext:
            return plaintext
        return self.cipher_suite.encrypt(plaintext.encode()).decode()

    def decrypt_data(self, ciphertext: str) -> str:
        """Decrypts a string of PII text"""
        if not ciphertext:
            return ciphertext
        try:
            return self.cipher_suite.decrypt(ciphertext.encode()).decode()
        except Exception:
            # If decryption fails (e.g key changed), return marker
            return "[ENCRYPTED_DATA_UNREADABLE]"

pii_redactor = PIIRedactor()
