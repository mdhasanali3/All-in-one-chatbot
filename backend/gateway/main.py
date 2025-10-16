"""FastAPI Gateway - Main entry point for all client requests."""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict
import grpc
from datetime import timedelta

from backend.shared import (
    settings,
    setup_logger,
    create_access_token,
    verify_access_key,
    get_current_user
)
from backend.gateway.grpc_clients import rag_client, llm_client, stt_client, tts_client
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logger = setup_logger(__name__)

# Prometheus metrics
request_counter = Counter('gateway_requests_total', 'Total requests', ['endpoint', 'method'])
request_duration = Histogram('gateway_request_duration_seconds', 'Request duration', ['endpoint'])

app = FastAPI(
    title="AI Voice Knowledge Assistant Gateway",
    description="Central gateway for all microservices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request with access key."""
    access_key: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


class QueryRequest(BaseModel):
    """Query request for RAG system."""
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class QueryResponse(BaseModel):
    """Query response from RAG system."""
    answer: str
    sources: Optional[List[str]] = []


class TTSRequest(BaseModel):
    """Text-to-speech request."""
    text: str
    voice_id: Optional[str] = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    request_counter.labels(endpoint='/health', method='GET').inc()
    return {"status": "healthy", "service": "gateway"}


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST
    )


# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with access key and return JWT token.

    Args:
        request: Login request with access key

    Returns:
        JWT token for authenticated requests
    """
    request_counter.labels(endpoint='/auth/login', method='POST').inc()
    logger.info("Login attempt")

    if not verify_access_key(request.access_key):
        logger.warning("Invalid access key provided")
        raise HTTPException(status_code=401, detail="Invalid access key")

    # Create JWT token
    token_data = {
        "access_key_verified": True,
        "user_type": "authenticated"
    }
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=24)
    )

    logger.info("Login successful")
    return LoginResponse(access_token=access_token)


@app.post("/auth/verify")
async def verify_token(current_user: Dict = Depends(get_current_user)):
    """
    Verify JWT token validity.

    Args:
        current_user: Current authenticated user

    Returns:
        Verification status
    """
    request_counter.labels(endpoint='/auth/verify', method='POST').inc()
    return {"valid": True, "user": current_user}


# Document upload endpoint
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Upload document to knowledge base.

    Args:
        file: Document file to upload
        current_user: Authenticated user

    Returns:
        Upload status
    """
    request_counter.labels(endpoint='/documents/upload', method='POST').inc()
    logger.info(f"Document upload: {file.filename}")

    try:
        # Read file data
        file_data = await file.read()

        # Call RAG service via gRPC to process document
        result = rag_client.ingest_document(file_data, file.filename)

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(
    request: QueryRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Query the knowledge base with RAG.

    Args:
        request: Query request with text and conversation history
        current_user: Authenticated user

    Returns:
        Answer from knowledge base
    """
    request_counter.labels(endpoint='/query', method='POST').inc()
    logger.info(f"Query received: {request.query[:50]}...")

    try:
        # Call RAG service via gRPC
        rag_result = rag_client.query(
            query=request.query,
            conversation_history=request.conversation_history,
            k=5
        )

        # Build context from RAG results
        context_text = rag_result.get("answer", "")

        # Call LLM service via gRPC to generate final answer
        llm_result = llm_client.generate(
            query=request.query,
            context=context_text,
            conversation_history=request.conversation_history
        )

        # Format sources for response
        sources = [source.get("filename", "unknown") for source in rag_result.get("sources", [])]

        return QueryResponse(
            answer=llm_result.get("answer", "Error generating response"),
            sources=sources
        )
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# STT endpoint
@app.post("/stt/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Transcribe audio to text using Whisper.

    Args:
        file: Audio file to transcribe
        current_user: Authenticated user

    Returns:
        Transcribed text
    """
    request_counter.labels(endpoint='/stt/transcribe', method='POST').inc()
    logger.info(f"Audio transcription: {file.filename}")

    try:
        # Read audio data
        audio_data = await file.read()

        # Call STT service via gRPC
        result = stt_client.transcribe(
            audio_data=audio_data,
            filename=file.filename
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# TTS endpoint
@app.post("/tts/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Convert text to speech using ElevenLabs.

    Args:
        request: TTS request with text
        current_user: Authenticated user

    Returns:
        Audio file stream
    """
    request_counter.labels(endpoint='/tts/synthesize', method='POST').inc()
    logger.info(f"TTS synthesis: {request.text[:50]}...")

    try:
        # Call TTS service via gRPC
        result = tts_client.synthesize_speech(
            text=request.text,
            voice_id=request.voice_id
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

        # Return audio as binary response
        return Response(
            content=result.get("audio_data", b""),
            media_type="audio/mpeg"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting gateway on port {settings.gateway_port}")
    uvicorn.run(app, host="0.0.0.0", port=settings.gateway_port)
