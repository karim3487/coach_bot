class CoachApiClientError(Exception):
    """Base exception for Coach API client errors."""


class BackupCodeInvalidOrUsed(CoachApiClientError):
    """Backup code is invalid or already used."""


class TelegramIDAlreadyLinked(CoachApiClientError):
    """Telegram ID already linked to another profile."""


class ClientProfileNotFound(CoachApiClientError):
    """Raised when telegram_id does not map to an existing ClientProfile."""


class ProgramNotFoundOrInactive(CoachApiClientError):
    """Raised when provided program_id is invalid or inactive."""
