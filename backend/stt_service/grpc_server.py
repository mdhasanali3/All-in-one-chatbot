"""gRPC server for STT service."""
import grpc
from concurrent import futures
import tempfile
import os
from backend.shared import settings, setup_logger
from backend.proto import stt_service_pb2, stt_service_pb2_grpc
from backend.stt_service.whisper_service import WhisperSTTService

logger = setup_logger(__name__)


class STTServiceServicer(stt_service_pb2_grpc.STTServiceServicer):
    """gRPC servicer for STT operations."""

    def __init__(self):
        self.stt_service = WhisperSTTService()
        logger.info("STT service servicer initialized")

    def Transcribe(self, request, context):
        """Transcribe audio to text."""
        try:
            logger.info(f"Transcribing audio: {request.filename}")

            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(request.filename)[1]
            ) as temp_file:
                temp_file.write(request.audio_data)
                temp_path = temp_file.name

            # Transcribe
            result = self.stt_service.transcribe_file(
                audio_file_path=temp_path,
                language=request.language if request.language else None,
                task=request.task if request.task else "transcribe"
            )

            # Clean up
            os.unlink(temp_path)

            return stt_service_pb2.TranscribeResponse(
                text=result.get("text", ""),
                language=result.get("language", "unknown"),
                status=result.get("status", "error"),
                error=result.get("error", "")
            )

        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return stt_service_pb2.TranscribeResponse(
                text="",
                language="unknown",
                status="error",
                error=str(e)
            )

    def DetectLanguage(self, request, context):
        """Detect language from audio."""
        try:
            logger.info(f"Detecting language: {request.filename}")

            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(request.filename)[1]
            ) as temp_file:
                temp_file.write(request.audio_data)
                temp_path = temp_file.name

            # Detect language
            result = self.stt_service.detect_language(temp_path)

            # Clean up
            os.unlink(temp_path)

            return stt_service_pb2.DetectLanguageResponse(
                language=result.get("language", "unknown"),
                confidence=result.get("confidence", 0.0),
                status=result.get("status", "error"),
                error=result.get("error", "")
            )

        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return stt_service_pb2.DetectLanguageResponse(
                language="unknown",
                confidence=0.0,
                status="error",
                error=str(e)
            )


def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stt_service_pb2_grpc.add_STTServiceServicer_to_server(
        STTServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{settings.stt_service_port}")
    server.start()
    logger.info(f"STT service gRPC server started on port {settings.stt_service_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
