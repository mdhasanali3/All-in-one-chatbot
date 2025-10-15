"""OpenAI LLM service for answer generation."""
from typing import List, Dict, Optional, AsyncGenerator
from openai import OpenAI, AsyncOpenAI
import json

from backend.shared import settings, setup_logger

logger = setup_logger(__name__)


class OpenAILLMService:
    """LLM service using OpenAI GPT models."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize OpenAI LLM service.

        Args:
            model: Model name (default: gpt-4o-mini)
            api_key: OpenAI API key
        """
        self.model = model or settings.openai_model
        self.api_key = api_key or settings.openai_api_key

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        logger.info(f"OpenAI LLM service initialized with model: {self.model}")

    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """
        Generate response using OpenAI.

        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous conversation turns
            system_prompt: Custom system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        try:
            # Build messages
            messages = []

            # System message
            if not system_prompt:
                system_prompt = """You are a helpful AI assistant with access to a knowledge base.
Use the provided context to answer questions accurately and concisely.
If the context doesn't contain relevant information, say so clearly.
Be professional, clear, and helpful in your responses."""

            if context:
                system_prompt += f"\n\nContext from knowledge base:\n{context}"

            messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            if conversation_history:
                for turn in conversation_history[-10:]:  # Last 10 turns
                    if "user" in turn:
                        messages.append({"role": "user", "content": turn["user"]})
                    if "assistant" in turn:
                        messages.append({"role": "assistant", "content": turn["assistant"]})

            # Add current query
            messages.append({"role": "user", "content": query})

            logger.info(f"Generating response for query: {query[:50]}...")

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            answer = response.choices[0].message.content

            logger.info("Response generated successfully")

            return {
                "answer": answer,
                "model": self.model,
                "tokens_used": response.usage.total_tokens,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return {
                "answer": f"Error generating response: {str(e)}",
                "status": "error"
            }

    async def generate_response_stream(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using OpenAI.

        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous conversation turns
            system_prompt: Custom system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Response chunks
        """
        try:
            # Build messages (same as non-streaming)
            messages = []

            if not system_prompt:
                system_prompt = """You are a helpful AI assistant with access to a knowledge base.
Use the provided context to answer questions accurately and concisely.
If the context doesn't contain relevant information, say so clearly.
Be professional, clear, and helpful in your responses."""

            if context:
                system_prompt += f"\n\nContext from knowledge base:\n{context}"

            messages.append({"role": "system", "content": system_prompt})

            if conversation_history:
                for turn in conversation_history[-10:]:
                    if "user" in turn:
                        messages.append({"role": "user", "content": turn["user"]})
                    if "assistant" in turn:
                        messages.append({"role": "assistant", "content": turn["assistant"]})

            messages.append({"role": "user", "content": query})

            logger.info(f"Generating streaming response for query: {query[:50]}...")

            # Call OpenAI API with streaming
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

            logger.info("Streaming response completed")

        except Exception as e:
            logger.error(f"Streaming response failed: {str(e)}")
            yield f"Error: {str(e)}"

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text using LLM.

        Args:
            text: Text to summarize
            max_length: Maximum summary length in words

        Returns:
            Summarized text
        """
        try:
            prompt = f"Summarize the following text in no more than {max_length} words:\n\n{text}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=max_length * 2
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return f"Error: {str(e)}"

    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Text to extract keywords from
            num_keywords: Number of keywords to extract

        Returns:
            List of keywords
        """
        try:
            prompt = f"Extract the {num_keywords} most important keywords from the following text. Return only the keywords as a JSON array:\n\n{text}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts keywords."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            keywords_str = response.choices[0].message.content
            keywords = json.loads(keywords_str)

            return keywords if isinstance(keywords, list) else []

        except Exception as e:
            logger.error(f"Keyword extraction failed: {str(e)}")
            return []


# Global service instance
llm_service = OpenAILLMService()
