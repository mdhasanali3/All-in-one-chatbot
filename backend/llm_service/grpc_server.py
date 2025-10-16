"""gRPC server for LLM service."""
import grpc
from concurrent import futures
from backend.shared import settings, setup_logger
from backend.proto import llm_service_pb2, llm_service_pb2_grpc
from backend.llm_service.openai_service import OpenAILLMService

logger = setup_logger(__name__)


class LLMServiceServicer(llm_service_pb2_grpc.LLMServiceServicer):
    """gRPC servicer for LLM operations."""

    def __init__(self):
        self.llm_service = OpenAILLMService()
        logger.info("LLM service servicer initialized")

    def Generate(self, request, context):
        """Generate response using LLM."""
        try:
            logger.info(f"Generating response for query: {request.query[:50]}...")

            # Convert conversation history
            conversation_history = [
                {
                    "user": turn.user,
                    "assistant": turn.assistant
                }
                for turn in request.conversation_history
            ]

            # Generate response
            result = self.llm_service.generate_response(
                query=request.query,
                context=request.context if request.context else None,
                conversation_history=conversation_history if conversation_history else None,
                system_prompt=request.system_prompt if request.system_prompt else None,
                temperature=request.temperature if request.temperature > 0 else 0.7,
                max_tokens=request.max_tokens if request.max_tokens > 0 else 1000
            )

            return llm_service_pb2.GenerateResponse(
                answer=result.get("answer", ""),
                model=result.get("model", ""),
                tokens_used=result.get("tokens_used", 0),
                status=result.get("status", "error")
            )

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return llm_service_pb2.GenerateResponse(
                answer=f"Error generating response: {str(e)}",
                model="",
                tokens_used=0,
                status="error"
            )

    def GenerateStream(self, request, context):
        """Generate streaming response using LLM."""
        try:
            logger.info(f"Generating streaming response for query: {request.query[:50]}...")

            # Convert conversation history
            conversation_history = [
                {
                    "user": turn.user,
                    "assistant": turn.assistant
                }
                for turn in request.conversation_history
            ]

            # Generate streaming response - need to use sync version for gRPC
            import asyncio

            async def stream_generator():
                async for chunk in self.llm_service.generate_response_stream(
                    query=request.query,
                    context=request.context if request.context else None,
                    conversation_history=conversation_history if conversation_history else None,
                    system_prompt=request.system_prompt if request.system_prompt else None,
                    temperature=request.temperature if request.temperature > 0 else 0.7,
                    max_tokens=request.max_tokens if request.max_tokens > 0 else 1000
                ):
                    yield llm_service_pb2.GenerateStreamResponse(chunk=chunk)

            # Run async generator in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_stream():
                async for response in stream_generator():
                    yield response

            for response in loop.run_until_complete(self._collect_stream(stream_generator())):
                yield response

        except Exception as e:
            logger.error(f"Streaming response failed: {str(e)}")
            yield llm_service_pb2.GenerateStreamResponse(chunk=f"Error: {str(e)}")

    async def _collect_stream(self, generator):
        """Collect async stream results."""
        results = []
        async for item in generator:
            results.append(item)
        return results


def serve():
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    llm_service_pb2_grpc.add_LLMServiceServicer_to_server(
        LLMServiceServicer(), server
    )
    server.add_insecure_port(f"[::]:{settings.llm_service_port}")
    server.start()
    logger.info(f"LLM service gRPC server started on port {settings.llm_service_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
