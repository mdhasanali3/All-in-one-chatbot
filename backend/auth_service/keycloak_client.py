"""Keycloak client for authentication management."""
from typing import Optional, Dict
from keycloak import KeycloakOpenID, KeycloakAdmin
from backend.shared import settings, setup_logger

logger = setup_logger(__name__)


class KeycloakClient:
    """Keycloak client for managing authentication."""

    def __init__(self):
        """Initialize Keycloak client."""
        self.server_url = settings.keycloak_server_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self.client_secret = settings.keycloak_client_secret

        # Initialize Keycloak OpenID client
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm,
            client_secret_key=self.client_secret
        )

        logger.info("Keycloak client initialized")

    def get_token(self, username: str, password: str) -> Dict:
        """
        Get access token from Keycloak.

        Args:
            username: User username
            password: User password

        Returns:
            Token response with access_token, refresh_token, etc.
        """
        try:
            token = self.keycloak_openid.token(username, password)
            logger.info(f"Token obtained for user: {username}")
            return token
        except Exception as e:
            logger.error(f"Failed to get token: {str(e)}")
            raise

    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            New token response
        """
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            logger.info("Token refreshed successfully")
            return token
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise

    def logout(self, refresh_token: str) -> None:
        """
        Logout user by invalidating refresh token.

        Args:
            refresh_token: Refresh token to invalidate
        """
        try:
            self.keycloak_openid.logout(refresh_token)
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error(f"Failed to logout: {str(e)}")
            raise

    def introspect_token(self, token: str) -> Dict:
        """
        Introspect token to check if it's valid.

        Args:
            token: Access token to introspect

        Returns:
            Token introspection result
        """
        try:
            token_info = self.keycloak_openid.introspect(token)
            return token_info
        except Exception as e:
            logger.error(f"Failed to introspect token: {str(e)}")
            raise

    def decode_token(self, token: str) -> Dict:
        """
        Decode JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token payload
        """
        try:
            options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
            token_info = self.keycloak_openid.decode_token(token, **options)
            return token_info
        except Exception as e:
            logger.error(f"Failed to decode token: {str(e)}")
            raise

    def get_userinfo(self, token: str) -> Dict:
        """
        Get user information from token.

        Args:
            token: Access token

        Returns:
            User information
        """
        try:
            userinfo = self.keycloak_openid.userinfo(token)
            return userinfo
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            raise


# Global Keycloak client instance
keycloak_client = KeycloakClient()
