"""Shared utilities package."""
from backend.shared.config import settings
from backend.shared.logger import setup_logger
from backend.shared.auth import (
    create_access_token,
    decode_access_token,
    verify_access_key,
    get_current_user,
    AuthMiddleware
)

__all__ = [
    "settings",
    "setup_logger",
    "create_access_token",
    "decode_access_token",
    "verify_access_key",
    "get_current_user",
    "AuthMiddleware"
]
