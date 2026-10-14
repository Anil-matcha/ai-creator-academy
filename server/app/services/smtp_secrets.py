"""Encryption helpers for SMTP relay credentials stored in the database."""

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

PREFIX = "fernet:v1:"


def _fernet() -> Fernet:
    key = settings.SMTP_CONFIG_ENCRYPTION_KEY
    if not key:
        raise RuntimeError("SMTP_CONFIG_ENCRYPTION_KEY is required to access encrypted SMTP credentials")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("SMTP_CONFIG_ENCRYPTION_KEY must be a valid Fernet key") from exc


def encrypt_password(password: str) -> str:
    if not password:
        return ""
    token = _fernet().encrypt(password.encode("utf-8")).decode("ascii")
    return PREFIX + token


def decrypt_password(stored: str | None) -> str:
    if not stored:
        return ""
    if not stored.startswith(PREFIX):
        # Existing installations may have plaintext credentials; startup upgrades
        # these when an encryption key is configured.
        return stored
    try:
        return _fernet().decrypt(stored[len(PREFIX):].encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeEncodeError, RuntimeError) as exc:
        raise RuntimeError("Stored SMTP credential cannot be decrypted; verify the encryption key and its backup") from exc
