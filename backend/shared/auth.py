"""Authentication utilities."""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.shared.config import settings
from backend.shared.logger import setup_logger

logger = setup_logger(__name__)
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_access_key(access_key: str) -> bool:
    """
    Verify if the provided access key is valid.

    Args:
        access_key: Access key to verify

    Returns:
        True if valid, False otherwise
    """
    return access_key == settings.access_key


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    Validate JWT token from request and return user data.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User data from token

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    # Verify access key from payload
    if not payload.get("access_key_verified"):
        raise HTTPException(status_code=401, detail="Access key not verified")

    return payload


class AuthMiddleware:
    """Middleware for authentication validation."""

    @staticmethod
    def validate_token_and_key(token: str) -> Dict:
        """
        Validate both JWT token and access key.

        Args:
            token: JWT token

        Returns:
            Validated payload
        """
        payload = decode_access_token(token)

        if not payload.get("access_key_verified"):
            raise HTTPException(
                status_code=401,
                detail="Access key verification required"
            )

        return payload
