"""Whisper-based Speech-to-Text service."""
import whisper
import tempfile
import os
from typing import Optional, Dict
from pathlib import Path

from backend.shared import settings, setup_logger

logger = setup_logger(__name__)


class WhisperSTTService:
    """Speech-to-Text service using OpenAI Whisper."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Whisper STT service.

        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name or settings.whisper_model
        logger.info(f"Loading Whisper model: {self.model_name}")

        try:
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise

    def transcribe_file(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
            task: 'transcribe' or 'translate'

        Returns:
            Transcription result with text and metadata
        """
        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")

            # Transcribe audio
            options = {"task": task}
            if language:
                options["language"] = language

            result = self.model.transcribe(audio_file_path, **options)

            logger.info("Transcription completed successfully")

            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "text": "",
                "error": str(e),
                "status": "error"
            }

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for extension detection)
            language: Optional language code
            task: 'transcribe' or 'translate'

        Returns:
            Transcription result
        """
        try:
            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=Path(filename).suffix
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Transcribe
            result = self.transcribe_file(temp_path, language, task)

            # Clean up
            os.unlink(temp_path)

            return result

        except Exception as e:
            logger.error(f"Transcription from bytes failed: {str(e)}")
            return {
                "text": "",
                "error": str(e),
                "status": "error"
            }

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.

        Returns:
            List of language codes
        """
        return list(whisper.tokenizer.LANGUAGES.keys())

    def detect_language(self, audio_file_path: str) -> Dict:
        """
        Detect language from audio file.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Detected language and confidence
        """
        try:
            # Load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(audio_file_path)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

            # Detect the spoken language
            _, probs = self.model.detect_language(mel)
            detected_language = max(probs, key=probs.get)

            logger.info(f"Detected language: {detected_language}")

            return {
                "language": detected_language,
                "confidence": probs[detected_language],
                "all_probabilities": {k: float(v) for k, v in probs.items()},
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return {
                "language": "unknown",
                "error": str(e),
                "status": "error"
            }


# Global service instance
stt_service = WhisperSTTService()
