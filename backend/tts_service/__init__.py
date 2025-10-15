"""TTS service package."""
from backend.tts_service.elevenlabs_service import ElevenLabsTTSService, tts_service

__all__ = ["ElevenLabsTTSService", "tts_service"]
