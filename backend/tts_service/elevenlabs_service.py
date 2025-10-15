"""ElevenLabs Text-to-Speech service."""
from typing import Optional, Dict
import io
from elevenlabs import generate, voices, Voice, VoiceSettings

from backend.shared import settings, setup_logger

logger = setup_logger(__name__)


class ElevenLabsTTSService:
    """Text-to-Speech service using ElevenLabs."""

    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        """
        Initialize ElevenLabs TTS service.

        Args:
            api_key: ElevenLabs API key
            voice_id: Default voice ID
        """
        self.api_key = api_key or settings.elevenlabs_api_key
        self.default_voice_id = voice_id or settings.elevenlabs_voice_id

        logger.info("ElevenLabs TTS service initialized")

    def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> Dict:
        """
        Synthesize speech from text.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (optional)
            model: Model to use for generation
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enable speaker boost

        Returns:
            Audio data and metadata
        """
        try:
            logger.info(f"Synthesizing speech for text: {text[:50]}...")

            voice_id = voice_id or self.default_voice_id

            if not voice_id:
                logger.error("No voice ID provided")
                return {
                    "status": "error",
                    "error": "Voice ID is required"
                }

            # Create voice settings
            voice_settings = VoiceSettings(
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )

            # Generate audio
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=voice_settings
                ),
                model=model,
                api_key=self.api_key
            )

            # Convert generator to bytes
            audio_bytes = b''.join(audio) if hasattr(audio, '__iter__') else audio

            logger.info("Speech synthesis completed successfully")

            return {
                "audio": audio_bytes,
                "voice_id": voice_id,
                "model": model,
                "text_length": len(text),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Synthesize speech and save to file.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice_id: Voice ID to use
            **kwargs: Additional synthesis parameters

        Returns:
            Status and metadata
        """
        try:
            result = self.synthesize_speech(text, voice_id, **kwargs)

            if result["status"] == "error":
                return result

            # Save to file
            with open(output_path, 'wb') as f:
                f.write(result["audio"])

            logger.info(f"Audio saved to: {output_path}")

            return {
                "status": "success",
                "output_path": output_path,
                "file_size": len(result["audio"])
            }

        except Exception as e:
            logger.error(f"Failed to save audio: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_available_voices(self) -> Dict:
        """
        Get list of available voices.

        Returns:
            List of available voices with metadata
        """
        try:
            available_voices = voices(api_key=self.api_key)

            voice_list = []
            for voice in available_voices:
                voice_list.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', 'unknown'),
                    "labels": getattr(voice, 'labels', {}),
                    "description": getattr(voice, 'description', '')
                })

            logger.info(f"Retrieved {len(voice_list)} available voices")

            return {
                "voices": voice_list,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}")
            return {
                "voices": [],
                "status": "error",
                "error": str(e)
            }

    def stream_audio(self, text: str, voice_id: Optional[str] = None, **kwargs):
        """
        Stream audio generation (generator).

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            **kwargs: Additional synthesis parameters

        Yields:
            Audio chunks
        """
        try:
            voice_id = voice_id or self.default_voice_id

            logger.info(f"Streaming audio for text: {text[:50]}...")

            # Create voice settings
            voice_settings = VoiceSettings(
                stability=kwargs.get('stability', 0.5),
                similarity_boost=kwargs.get('similarity_boost', 0.75),
                style=kwargs.get('style', 0.0),
                use_speaker_boost=kwargs.get('use_speaker_boost', True)
            )

            # Generate audio stream
            audio_stream = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=voice_settings
                ),
                model=kwargs.get('model', 'eleven_monolingual_v1'),
                stream=True,
                api_key=self.api_key
            )

            for chunk in audio_stream:
                yield chunk

            logger.info("Audio streaming completed")

        except Exception as e:
            logger.error(f"Audio streaming failed: {str(e)}")
            raise


# Global service instance
tts_service = ElevenLabsTTSService()
