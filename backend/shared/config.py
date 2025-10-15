"""Shared configuration across all services."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Authentication
    keycloak_server_url: str = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
    keycloak_realm: str = os.getenv("KEYCLOAK_REALM", "ai-assistant")
    keycloak_client_id: str = os.getenv("KEYCLOAK_CLIENT_ID", "ai-assistant-client")
    keycloak_client_secret: str = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    access_key: str = os.getenv("ACCESS_KEY", "admin_hasan_007_no_exit")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"

    # ElevenLabs
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    elevenlabs_voice_id: str = os.getenv("ELEVENLABS_VOICE_ID", "")

    # Service Ports
    gateway_port: int = int(os.getenv("GATEWAY_PORT", "8000"))
    stt_service_port: int = int(os.getenv("STT_SERVICE_PORT", "50051"))
    rag_service_port: int = int(os.getenv("RAG_SERVICE_PORT", "50052"))
    llm_service_port: int = int(os.getenv("LLM_SERVICE_PORT", "50053"))
    tts_service_port: int = int(os.getenv("TTS_SERVICE_PORT", "50054"))

    # Service Hosts (for Docker networking)
    stt_service_host: str = os.getenv("STT_SERVICE_HOST", "localhost")
    rag_service_host: str = os.getenv("RAG_SERVICE_HOST", "localhost")
    llm_service_host: str = os.getenv("LLM_SERVICE_HOST", "localhost")
    tts_service_host: str = os.getenv("TTS_SERVICE_HOST", "localhost")

    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))

    # Monitoring
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "9090"))

    # Storage
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "./data/knowledge_base")
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")

    # Model Configuration
    whisper_model: str = os.getenv("WHISPER_MODEL", "base")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Conversation Settings
    max_conversation_turns: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
