"""gRPC server for RAG service."""
import grpc
from concurrent import futures
import tempfile
import os
from backend.shared import settings, setup_logger
from backend.proto import rag_service_pb2, rag_service_pb2_grpc
from backend.rag_service.rag_engine import RAGEngine

logger = setup_logger(__name__)


class RAGServiceServicer(rag_service_pb2_grpc.RAGServiceServicer):
    """gRPC servicer for RAG operations."""

    def __init__(self):
        self.rag_engine = RAGEngine()
        logger.info("RAG service servicer initialized")

    def IngestDocument(self, request, context):
        """Ingest document into RAG system."""
        try:
            logger.info(f"Ingesting document: {request.filename}")

            # Save bytes to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=os.path.splitext(request.filename)[1]
            ) as temp_file:
                temp_file.write(request.file_data)
                temp_path = temp_file.name

            # Process document
            result = self.rag_engine.ingest_document(temp_path)

            # Clean up
            os.unlink(temp_path)

            return rag_service_pb2.IngestDocumentResponse(
                status=result.get("status", "error"),
                filename=result.get("filename", request.filename),
                chunks_created=result.get("chunks_created", 0),
                file_type=result.get("file_type", "unknown"),
                message=result.get("message", "")
            )

        except Exception as e:
            logger.error(f"Document ingestion failed: {str(e)}")
            return rag_service_pb2.IngestDocumentResponse(
                status="error",
                filename=request.filename,
                chunks_created=0,
                file_type="unknown",
                message=str(e)
            )

    def Query(self, request, context):
        """Query RAG system."""
        try:
            logger.info(f"Processing query: {request.query[:50]}...")

            # Convert conversation history
            conversation_history = [
                {
                    "user": turn.user,
                    "assistant": turn.assistant
                }
                for turn in request.conversation_history
            ]

            # Query RAG engine
            result = self.rag_engine.query(
                query=request.query,
                conversation_history=conversation_history if conversation_history else None,
                k=request.k if request.k > 0 else 5
            )

            # Build sources
            sources = [
                rag_service_pb2.Source(
                    filename=source.get("filename", "unknown"),
                    chunk_index=source.get("chunk_index", 0),
                    relevance_score=source.get("relevance_score", 0.0)
                )
                for source in result.get("sources", [])
            ]

            return rag_service_pb2.QueryResponse(
                answer=result.get("answer", ""),
                sources=sources,
                context_used=result.get("context_used", False)
            )

        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return rag_service_pb2.QueryResponse(
                answer=f"Error processing query: {str(e)}",
                sources=[],
                context_used=False
            )

    def GetStats(self, request, context):
        """Get RAG statistics."""
        try:
            stats = self.rag_engine.get_stats()
            return rag_service_pb2.GetStatsResponse(
                total_documents=stats.get("total_documents", 0),
                total_chunks=stats.get("total_chunks", 0)
            )
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return rag_service_pb2.GetStatsResponse(
                total_documents=0,
                total_chunks=0
            )


def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rag_service_pb2_grpc.add_RAGServiceServicer_to_server(
        RAGServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{settings.rag_service_port}")
    server.start()
    logger.info(f"RAG service gRPC server started on port {settings.rag_service_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
