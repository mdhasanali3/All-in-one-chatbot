"""RAG engine combining document retrieval and generation."""
from typing import List, Dict, Optional, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from backend.shared import settings, setup_logger
from backend.rag_service.document_processor import DocumentProcessor
from backend.rag_service.vector_store import VectorStore

logger = setup_logger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine."""

    def __init__(self):
        """Initialize RAG engine components."""
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()

        # Initialize LangChain text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Load existing vector store if available
        self._load_vector_store()

        logger.info("RAG engine initialized")

    def _load_vector_store(self):
        """Load existing vector store from disk."""
        try:
            index_path = f"{settings.faiss_index_path}/index.faiss"
            docs_path = f"{settings.faiss_index_path}/documents.pkl"
            self.vector_store.load(index_path, docs_path)
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {str(e)}")

    def _save_vector_store(self):
        """Save vector store to disk."""
        try:
            import os
            os.makedirs(settings.faiss_index_path, exist_ok=True)

            index_path = f"{settings.faiss_index_path}/index.faiss"
            docs_path = f"{settings.faiss_index_path}/documents.pkl"
            self.vector_store.save(index_path, docs_path)
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")

    def ingest_document(self, file_path: str) -> Dict:
        """
        Ingest a document into the knowledge base.

        Args:
            file_path: Path to the document

        Returns:
            Ingestion status
        """
        try:
            logger.info(f"Ingesting document: {file_path}")

            # Extract text from document
            doc_data = self.document_processor.process_document(file_path)

            # Split text into chunks
            chunks = self.text_splitter.split_text(doc_data["text"])

            # Create metadata for each chunk
            metadata = [
                {
                    "filename": doc_data["filename"],
                    "file_type": doc_data["file_type"],
                    "chunk_index": i
                }
                for i in range(len(chunks))
            ]

            # Add to vector store
            self.vector_store.add_documents(chunks, metadata)

            # Save vector store
            self._save_vector_store()

            logger.info(f"Successfully ingested {len(chunks)} chunks from {doc_data['filename']}")

            return {
                "status": "success",
                "filename": doc_data["filename"],
                "chunks_created": len(chunks),
                "file_type": doc_data["file_type"]
            }

        except Exception as e:
            logger.error(f"Document ingestion failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def retrieve_context(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query
            k: Number of documents to retrieve

        Returns:
            List of relevant documents with scores and metadata
        """
        results = self.vector_store.search(query, k=k)
        logger.info(f"Retrieved {len(results)} documents for query")
        return results

    def generate_answer(
        self,
        query: str,
        context: List[Tuple[str, float, Dict]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict:
        """
        Generate answer using retrieved context and LLM.

        Args:
            query: User query
            context: Retrieved context documents
            conversation_history: Previous conversation turns

        Returns:
            Generated answer with sources
        """
        try:
            # Prepare context text
            context_text = "\n\n".join([doc[0] for doc in context])

            # Prepare conversation history
            history_text = ""
            if conversation_history:
                for turn in conversation_history[-10:]:  # Last 10 turns
                    history_text += f"User: {turn.get('user', '')}\n"
                    history_text += f"Assistant: {turn.get('assistant', '')}\n\n"

            # Create prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful AI assistant with access to a knowledge base.
Use the provided context to answer the user's question accurately.
If the context doesn't contain relevant information, say so clearly.
Be concise but thorough in your responses.

Context from knowledge base:
{context}

Previous conversation:
{history}
"""),
                ("user", "{query}")
            ])

            # Initialize LLM (placeholder - will be integrated with LLM service)
            # For now, return a structured response
            sources = [
                {
                    "filename": doc[2].get("filename", "unknown"),
                    "chunk_index": doc[2].get("chunk_index", 0),
                    "relevance_score": doc[1]
                }
                for doc in context
            ]

            # This is a placeholder - actual LLM call will be added
            answer = f"Based on the retrieved context, I found {len(context)} relevant documents. "
            answer += "The actual answer generation will be integrated with the LLM service."

            return {
                "answer": answer,
                "sources": sources,
                "context_used": len(context) > 0
            }

        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "context_used": False
            }

    def query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        k: int = 5
    ) -> Dict:
        """
        Complete RAG query pipeline.

        Args:
            query: User query
            conversation_history: Previous conversation turns
            k: Number of documents to retrieve

        Returns:
            Answer with sources
        """
        logger.info(f"Processing RAG query: {query[:50]}...")

        # Retrieve context
        context = self.retrieve_context(query, k=k)

        # Generate answer
        result = self.generate_answer(query, context, conversation_history)

        return result

    def get_stats(self) -> Dict:
        """
        Get RAG engine statistics.

        Returns:
            Statistics dictionary
        """
        return self.vector_store.get_stats()
