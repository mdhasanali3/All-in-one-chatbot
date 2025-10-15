"""STT service package."""
from backend.stt_service.whisper_service import WhisperSTTService, stt_service

__all__ = ["WhisperSTTService", "stt_service"]
