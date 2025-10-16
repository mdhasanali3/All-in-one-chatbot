"""gRPC clients for gateway to communicate with microservices."""
import grpc
from typing import List, Dict, Optional
from backend.shared import settings, setup_logger
from backend.proto import rag_service_pb2, rag_service_pb2_grpc
from backend.proto import llm_service_pb2, llm_service_pb2_grpc
from backend.proto import stt_service_pb2, stt_service_pb2_grpc
from backend.proto import tts_service_pb2, tts_service_pb2_grpc

logger = setup_logger(__name__)


class RAGClient:
    """gRPC client for RAG service."""

    def __init__(self):
        self.host = settings.rag_service_host
        self.port = settings.rag_service_port
        self.address = f"{self.host}:{self.port}"

    def _get_stub(self):
        """Get gRPC stub with channel."""
        channel = grpc.insecure_channel(self.address)
        return rag_service_pb2_grpc.RAGServiceStub(channel), channel

    def ingest_document(self, file_data: bytes, filename: str) -> Dict:
        """Ingest document into RAG system."""
        try:
            stub, channel = self._get_stub()

            request = rag_service_pb2.IngestDocumentRequest(
                file_data=file_data,
                filename=filename
            )

            response = stub.IngestDocument(request)
            channel.close()

            return {
                "status": response.status,
                "filename": response.filename,
                "chunks_created": response.chunks_created,
                "file_type": response.file_type,
                "message": response.message
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in ingest_document: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def query(self, query: str, conversation_history: Optional[List[Dict]] = None, k: int = 5) -> Dict:
        """Query RAG system."""
        try:
            stub, channel = self._get_stub()

            history = []
            if conversation_history:
                for turn in conversation_history:
                    history.append(rag_service_pb2.ConversationTurn(
                        user=turn.get("user", ""),
                        assistant=turn.get("assistant", "")
                    ))

            request = rag_service_pb2.QueryRequest(
                query=query,
                conversation_history=history,
                k=k
            )

            response = stub.Query(request)
            channel.close()

            sources = [
                {
                    "filename": source.filename,
                    "chunk_index": source.chunk_index,
                    "relevance_score": source.relevance_score
                }
                for source in response.sources
            ]

            return {
                "answer": response.answer,
                "sources": sources,
                "context_used": response.context_used
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in query: {e}")
            return {
                "answer": f"Error querying RAG service: {str(e)}",
                "sources": [],
                "context_used": False
            }

    def get_stats(self) -> Dict:
        """Get RAG statistics."""
        try:
            stub, channel = self._get_stub()

            request = rag_service_pb2.GetStatsRequest()
            response = stub.GetStats(request)
            channel.close()

            return {
                "total_documents": response.total_documents,
                "total_chunks": response.total_chunks
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0
            }


class LLMClient:
    """gRPC client for LLM service."""

    def __init__(self):
        self.host = settings.llm_service_host
        self.port = settings.llm_service_port
        self.address = f"{self.host}:{self.port}"

    def _get_stub(self):
        """Get gRPC stub with channel."""
        channel = grpc.insecure_channel(self.address)
        return llm_service_pb2_grpc.LLMServiceStub(channel), channel

    def generate(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """Generate response using LLM."""
        try:
            stub, channel = self._get_stub()

            history = []
            if conversation_history:
                for turn in conversation_history:
                    history.append(llm_service_pb2.ConversationTurn(
                        user=turn.get("user", ""),
                        assistant=turn.get("assistant", "")
                    ))

            request = llm_service_pb2.GenerateRequest(
                query=query,
                context=context or "",
                conversation_history=history,
                system_prompt=system_prompt or "",
                temperature=temperature,
                max_tokens=max_tokens
            )

            response = stub.Generate(request)
            channel.close()

            return {
                "answer": response.answer,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "status": response.status
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in generate: {e}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "status": "error"
            }

    def generate_stream(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Generate streaming response using LLM."""
        try:
            stub, channel = self._get_stub()

            history = []
            if conversation_history:
                for turn in conversation_history:
                    history.append(llm_service_pb2.ConversationTurn(
                        user=turn.get("user", ""),
                        assistant=turn.get("assistant", "")
                    ))

            request = llm_service_pb2.GenerateRequest(
                query=query,
                context=context or "",
                conversation_history=history,
                system_prompt=system_prompt or "",
                temperature=temperature,
                max_tokens=max_tokens
            )

            for response in stub.GenerateStream(request):
                yield response.chunk

            channel.close()
        except grpc.RpcError as e:
            logger.error(f"gRPC error in generate_stream: {e}")
            yield f"Error: {str(e)}"


class STTClient:
    """gRPC client for STT service."""

    def __init__(self):
        self.host = settings.stt_service_host
        self.port = settings.stt_service_port
        self.address = f"{self.host}:{self.port}"

    def _get_stub(self):
        """Get gRPC stub with channel."""
        channel = grpc.insecure_channel(self.address)
        return stt_service_pb2_grpc.STTServiceStub(channel), channel

    def transcribe(
        self,
        audio_data: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """Transcribe audio to text."""
        try:
            stub, channel = self._get_stub()

            request = stt_service_pb2.TranscribeRequest(
                audio_data=audio_data,
                filename=filename,
                language=language or "",
                task=task
            )

            response = stub.Transcribe(request)
            channel.close()

            return {
                "text": response.text,
                "language": response.language,
                "status": response.status,
                "error": response.error
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in transcribe: {e}")
            return {
                "text": "",
                "status": "error",
                "error": str(e)
            }

    def detect_language(self, audio_data: bytes, filename: str = "audio.wav") -> Dict:
        """Detect language from audio."""
        try:
            stub, channel = self._get_stub()

            request = stt_service_pb2.DetectLanguageRequest(
                audio_data=audio_data,
                filename=filename
            )

            response = stub.DetectLanguage(request)
            channel.close()

            return {
                "language": response.language,
                "confidence": response.confidence,
                "status": response.status,
                "error": response.error
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in detect_language: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "status": "error",
                "error": str(e)
            }


class TTSClient:
    """gRPC client for TTS service."""

    def __init__(self):
        self.host = settings.tts_service_host
        self.port = settings.tts_service_port
        self.address = f"{self.host}:{self.port}"

    def _get_stub(self):
        """Get gRPC stub with channel."""
        channel = grpc.insecure_channel(self.address)
        return tts_service_pb2_grpc.TTSServiceStub(channel), channel

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
        """Synthesize speech from text."""
        try:
            stub, channel = self._get_stub()

            request = tts_service_pb2.SynthesizeRequest(
                text=text,
                voice_id=voice_id or "",
                model=model,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )

            response = stub.SynthesizeSpeech(request)
            channel.close()

            return {
                "audio_data": response.audio_data,
                "voice_id": response.voice_id,
                "model": response.model,
                "text_length": response.text_length,
                "status": response.status,
                "error": response.error
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in synthesize_speech: {e}")
            return {
                "audio_data": b"",
                "status": "error",
                "error": str(e)
            }

    def stream_audio(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ):
        """Stream audio generation."""
        try:
            stub, channel = self._get_stub()

            request = tts_service_pb2.SynthesizeRequest(
                text=text,
                voice_id=voice_id or "",
                model=model,
                stability=stability,
                similarity_boost=similarity_boost,
                style=style,
                use_speaker_boost=use_speaker_boost
            )

            for response in stub.StreamAudio(request):
                yield response.chunk_data

            channel.close()
        except grpc.RpcError as e:
            logger.error(f"gRPC error in stream_audio: {e}")
            yield b""

    def get_available_voices(self) -> Dict:
        """Get available voices."""
        try:
            stub, channel = self._get_stub()

            request = tts_service_pb2.GetVoicesRequest()
            response = stub.GetAvailableVoices(request)
            channel.close()

            voices = [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                    "description": voice.description
                }
                for voice in response.voices
            ]

            return {
                "voices": voices,
                "status": response.status,
                "error": response.error
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_available_voices: {e}")
            return {
                "voices": [],
                "status": "error",
                "error": str(e)
            }


# Global client instances
rag_client = RAGClient()
llm_client = LLMClient()
stt_client = STTClient()
tts_client = TTSClient()
