"""Vector store management with FAISS."""
import os
import pickle
from typing import List, Dict, Optional, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.shared import settings, setup_logger

logger = setup_logger(__name__)


class VectorStore:
    """FAISS vector store for document embeddings."""

    def __init__(self, embedding_model: Optional[str] = None):
        """
        Initialize vector store.

        Args:
            embedding_model: Name of the sentence transformer model
        """
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []  # Store document chunks with metadata

        logger.info(f"Vector store initialized with model: {self.embedding_model_name}")
        logger.info(f"Embedding dimension: {self.dimension}")

    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None):
        """
        Add documents to the vector store.

        Args:
            texts: List of text chunks to add
            metadata: Optional metadata for each chunk
        """
        if not texts:
            logger.warning("No texts to add")
            return

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Convert to numpy array
        embeddings_np = np.array(embeddings).astype('float32')

        # Add to FAISS index
        self.index.add(embeddings_np)

        # Store documents with metadata
        for i, text in enumerate(texts):
            doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
            self.documents.append({
                "text": text,
                "metadata": doc_metadata
            })

        logger.info(f"Added {len(texts)} documents to vector store")
        logger.info(f"Total documents in store: {len(self.documents)}")

    def search(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (text, score, metadata) tuples
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        query_embedding_np = np.array(query_embedding).astype('float32')

        # Search in FAISS
        distances, indices = self.index.search(query_embedding_np, k)

        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                results.append((
                    doc["text"],
                    float(distances[0][i]),
                    doc["metadata"]
                ))

        logger.info(f"Found {len(results)} results for query")
        return results

    def save(self, index_path: str, documents_path: str):
        """
        Save vector store to disk.

        Args:
            index_path: Path to save FAISS index
            documents_path: Path to save documents
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, index_path)

            # Save documents
            with open(documents_path, 'wb') as f:
                pickle.dump(self.documents, f)

            logger.info(f"Vector store saved to {index_path}")
        except Exception as e:
            logger.error(f"Failed to save vector store: {str(e)}")
            raise

    def load(self, index_path: str, documents_path: str):
        """
        Load vector store from disk.

        Args:
            index_path: Path to FAISS index
            documents_path: Path to documents
        """
        try:
            if not os.path.exists(index_path) or not os.path.exists(documents_path):
                logger.warning("Vector store files not found")
                return

            # Load FAISS index
            self.index = faiss.read_index(index_path)

            # Load documents
            with open(documents_path, 'rb') as f:
                self.documents = pickle.load(f)

            logger.info(f"Vector store loaded from {index_path}")
            logger.info(f"Loaded {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Failed to load vector store: {str(e)}")
            raise

    def clear(self):
        """Clear all documents from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        logger.info("Vector store cleared")

    def get_stats(self) -> Dict:
        """
        Get vector store statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal,
            "embedding_dimension": self.dimension,
            "embedding_model": self.embedding_model_name
        }
