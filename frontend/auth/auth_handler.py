"""Authentication handler for frontend."""
import requests
from typing import Dict


class AuthHandler:
    """Handle authentication operations."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize auth handler.

        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
        self.auth_endpoint = f"{base_url}/auth/login"
        self.verify_endpoint = f"{base_url}/auth/verify"

    def login(self, access_key: str) -> Dict:
        """
        Login with access key.

        Args:
            access_key: Access key for authentication

        Returns:
            Login result with token
        """
        try:
            response = requests.post(
                self.auth_endpoint,
                json={"access_key": access_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "token": data.get("access_token"),
                    "token_type": data.get("token_type", "bearer")
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("detail", "Authentication failed")
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }

    def verify_token(self, token: str) -> Dict:
        """
        Verify if token is valid.

        Args:
            token: JWT token to verify

        Returns:
            Verification result
        """
        try:
            response = requests.post(
                self.verify_endpoint,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "valid": True,
                    "user": response.json()
                }
            else:
                return {
                    "valid": False,
                    "error": "Token validation failed"
                }

        except requests.exceptions.RequestException as e:
            return {
                "valid": False,
                "error": str(e)
            }
