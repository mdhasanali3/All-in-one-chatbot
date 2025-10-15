"""Authentication service package."""
from backend.auth_service.keycloak_client import keycloak_client, KeycloakClient

__all__ = ["keycloak_client", "KeycloakClient"]
