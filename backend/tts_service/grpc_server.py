"""gRPC server for TTS service."""
import grpc
from concurrent import futures
from backend.shared import settings, setup_logger
from backend.proto import tts_service_pb2, tts_service_pb2_grpc
from backend.tts_service.elevenlabs_service import ElevenLabsTTSService

logger = setup_logger(__name__)


class TTSServiceServicer(tts_service_pb2_grpc.TTSServiceServicer):
    """gRPC servicer for TTS operations."""

    def __init__(self):
        self.tts_service = ElevenLabsTTSService()
        logger.info("TTS service servicer initialized")

    def SynthesizeSpeech(self, request, context):
        """Synthesize speech from text."""
        try:
            logger.info(f"Synthesizing speech for text: {request.text[:50]}...")

            # Synthesize speech
            result = self.tts_service.synthesize_speech(
                text=request.text,
                voice_id=request.voice_id if request.voice_id else None,
                model=request.model if request.model else "eleven_monolingual_v1",
                stability=request.stability if request.stability > 0 else 0.5,
                similarity_boost=request.similarity_boost if request.similarity_boost > 0 else 0.75,
                style=request.style if request.style > 0 else 0.0,
                use_speaker_boost=request.use_speaker_boost
            )

            return tts_service_pb2.SynthesizeResponse(
                audio_data=result.get("audio", b""),
                voice_id=result.get("voice_id", ""),
                model=result.get("model", ""),
                text_length=result.get("text_length", 0),
                status=result.get("status", "error"),
                error=result.get("error", "")
            )

        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            return tts_service_pb2.SynthesizeResponse(
                audio_data=b"",
                voice_id="",
                model="",
                text_length=0,
                status="error",
                error=str(e)
            )

    def StreamAudio(self, request, context):
        """Stream audio generation."""
        try:
            logger.info(f"Streaming audio for text: {request.text[:50]}...")

            # Stream audio
            for chunk in self.tts_service.stream_audio(
                text=request.text,
                voice_id=request.voice_id if request.voice_id else None,
                model=request.model if request.model else "eleven_monolingual_v1",
                stability=request.stability if request.stability > 0 else 0.5,
                similarity_boost=request.similarity_boost if request.similarity_boost > 0 else 0.75,
                style=request.style if request.style > 0 else 0.0,
                use_speaker_boost=request.use_speaker_boost
            ):
                yield tts_service_pb2.AudioChunk(chunk_data=chunk)

        except Exception as e:
            logger.error(f"Audio streaming failed: {str(e)}")
            yield tts_service_pb2.AudioChunk(chunk_data=b"")

    def GetAvailableVoices(self, request, context):
        """Get available voices."""
        try:
            logger.info("Getting available voices")

            result = self.tts_service.get_available_voices()

            voices = [
                tts_service_pb2.Voice(
                    voice_id=voice.get("voice_id", ""),
                    name=voice.get("name", ""),
                    category=voice.get("category", ""),
                    description=voice.get("description", "")
                )
                for voice in result.get("voices", [])
            ]

            return tts_service_pb2.GetVoicesResponse(
                voices=voices,
                status=result.get("status", "error"),
                error=result.get("error", "")
            )

        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}")
            return tts_service_pb2.GetVoicesResponse(
                voices=[],
                status="error",
                error=str(e)
            )


def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tts_service_pb2_grpc.add_TTSServiceServicer_to_server(
        TTSServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{settings.tts_service_port}")
    server.start()
    logger.info(f"TTS service gRPC server started on port {settings.tts_service_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
