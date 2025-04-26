class CoachApiClientError(Exception):
    """Base exception for Coach API client errors."""


class BackupCodeInvalidOrUsed(CoachApiClientError):
    """Backup code is invalid or already used."""


class TelegramIDAlreadyLinked(CoachApiClientError):
    """Telegram ID already linked to another profile."""
