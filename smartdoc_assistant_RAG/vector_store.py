"""
Vector Database Module for Document Retrieval

This module provides a professional vector database implementation using FAISS
for efficient similarity search and retrieval of document chunks. It handles
text chunking, embedding generation, index management, and semantic retrieval
operations for RAG (Retrieval-Augmented Generation) systems.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
from typing import List, Optional
import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

# Configure module logger
logger = logging.getLogger(__name__)


class VectorDBError(Exception):
    """Custom exception for VectorDB-specific errors."""

    pass


class VectorDB:
    """
    Professional vector database for document chunk storage and retrieval.

    """

    # Class constants for configuration
    DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
    DEFAULT_CHUNK_SIZE = 600
    DEFAULT_OVERLAP = 50
    DEFAULT_TOP_K = 5
    DEFAULT_SIMILARITY_THRESHOLD = 0.2
    MIN_CHUNK_LENGTH = 10  # Minimum characters for a valid chunk
    MAX_CHUNK_SIZE = 2000  # Maximum chunk size for memory efficiency

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        """
        Initialize VectorDB with specified embedding model.

        Args:
            model_name (str): Name of the SentenceTransformer model to use

        Raises:
            VectorDBError: If model initialization fails
        """
        self.model_name = model_name
        self.embedding_dimension: Optional[int] = None
        self.index: Optional[faiss.Index] = None
        self.chunks: List[str] = []
        self.is_indexed = False

        logger.info(f"Initializing VectorDB with model: {model_name}")

        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded embedding model: {model_name}")

        except Exception as e:
            error_msg = f"Failed to initialize embedding model '{model_name}': {e}"
            logger.error(error_msg)
            raise VectorDBError(error_msg) from e

    def _validate_text_input(self, text: str) -> None:
        """
        Validate text input for processing.

        Args:
            text (str): Input text to validate

        Raises:
            VectorDBError: If text is invalid
        """
        if not isinstance(text, str):
            raise VectorDBError(f"Text must be a string, got {type(text)}")

        if not text.strip():
            raise VectorDBError("Text cannot be empty or whitespace only")

        if len(text) < self.MIN_CHUNK_LENGTH:
            raise VectorDBError(
                f"Text too short (minimum {self.MIN_CHUNK_LENGTH} characters)"
            )

    def _validate_chunk_parameters(self, chunk_size: int, overlap: int) -> None:
        """
        Validate chunking parameters.

        Args:
            chunk_size (int): Size of each chunk in words
            overlap (int): Number of overlapping words between chunks

        Raises:
            VectorDBError: If parameters are invalid
        """
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise VectorDBError("Chunk size must be a positive integer")

        if not isinstance(overlap, int) or overlap < 0:
            raise VectorDBError("Overlap must be a non-negative integer")

        if overlap >= chunk_size:
            raise VectorDBError("Overlap must be less than chunk size")

        if chunk_size > self.MAX_CHUNK_SIZE:
            raise VectorDBError(f"Chunk size cannot exceed {self.MAX_CHUNK_SIZE} words")

    def chunk_text(
        self,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> List[str]:
        """
        Split text into overlapping word-based chunks for optimal retrieval.

        """
        logger.debug(
            f"Chunking text: {len(text)} characters, chunk_size={chunk_size}, overlap={overlap}"
        )

        try:
            # Validate inputs
            self._validate_text_input(text)
            self._validate_chunk_parameters(chunk_size, overlap)

            # Split text into words
            words = text.split()
            total_words = len(words)

            if total_words <= chunk_size:
                logger.info(f"Text has {total_words} words, creating single chunk")
                return [text.strip()]

            # Create overlapping chunks
            chunks = []
            step_size = chunk_size - overlap

            for i in range(0, total_words, step_size):
                # Extract chunk words
                chunk_words = words[i : i + chunk_size]
                chunk_text = " ".join(chunk_words).strip()

                # Only add non-empty chunks with sufficient content
                if len(chunk_text) >= self.MIN_CHUNK_LENGTH:
                    chunks.append(chunk_text)

                # Stop if we've reached the end
                if i + chunk_size >= total_words:
                    break

            logger.info(f"Created {len(chunks)} text chunks from {total_words} words")
            return chunks

        except VectorDBError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during text chunking: {e}"
            logger.error(error_msg)
            raise VectorDBError(error_msg) from e

    def _create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Create and configure FAISS index for similarity search.

        """
        try:
            dimension = embeddings.shape[1]

            # Create inner product index for cosine similarity (after normalization)
            index = faiss.IndexFlatIP(dimension)

            # Normalize embeddings for proper cosine similarity
            faiss.normalize_L2(embeddings)

            # Add embeddings to index
            index.add(embeddings.astype("float32"))

            logger.debug(f"Created FAISS index with dimension {dimension}")
            return index

        except Exception as e:
            error_msg = f"Failed to create FAISS index: {e}"
            logger.error(error_msg)
            raise VectorDBError(error_msg) from e

    def build_index(
        self,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> None:
        """
        Build FAISS index from document text with comprehensive error handling.

        This method performs one-time indexing of the document text, creating
        chunks and building the vector index for efficient retrieval.

        """
        if self.is_indexed:
            logger.info("Index already built, skipping rebuild")
            return

        logger.info("Building FAISS index from document text...")

        try:
            # Create text chunks
            self.chunks = self.chunk_text(text, chunk_size, overlap)

            if not self.chunks:
                raise VectorDBError("No valid chunks created from input text")

            logger.info(f"Processing {len(self.chunks)} chunks for indexing")

            # Generate embeddings for all chunks
            logger.debug("Generating embeddings for text chunks...")
            embeddings = self.embedding_model.encode(
                self.chunks, show_progress_bar=False, convert_to_numpy=True
            )

            # Store embedding dimension
            self.embedding_dimension = embeddings.shape[1]

            # Create and populate FAISS index
            self.index = self._create_faiss_index(embeddings)

            # Mark as successfully indexed
            self.is_indexed = True

            logger.info(
                f"FAISS index built successfully with {self.index.ntotal} vectors"
            )
            logger.info(
                f"Index stats - Chunks: {len(self.chunks)}, Dimension: {self.embedding_dimension}"
            )

        except VectorDBError:
            raise
        except Exception as e:
            # Clean up on failure
            self._cleanup_failed_index()
            error_msg = f"Unexpected error during index building: {e}"
            logger.error(error_msg)
            raise VectorDBError(error_msg) from e

    def _cleanup_failed_index(self) -> None:
        """Clean up resources after failed index creation."""
        self.index = None
        self.chunks = []
        self.is_indexed = False
        self.embedding_dimension = None
        logger.debug("Cleaned up resources after failed index creation")

    def _validate_retrieval_parameters(
        self, query: str, top_k: int, threshold: float
    ) -> None:
        """
        Validate parameters for retrieval operation.

        """
        if not isinstance(query, str) or not query.strip():
            raise VectorDBError("Query must be a non-empty string")

        if not isinstance(top_k, int) or top_k <= 0:
            raise VectorDBError("top_k must be a positive integer")

        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            raise VectorDBError("Threshold must be a number between 0 and 1")

        if top_k > len(self.chunks):
            logger.warning(
                f"top_k ({top_k}) exceeds available chunks ({len(self.chunks)})"
            )

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> List[str]:
        """
        Retrieve most similar document chunks for a given query.

        Performs semantic similarity search using the pre-built FAISS index
        to find the most relevant text chunks for the input query.

        """
        logger.debug(
            f"Retrieving chunks for query: '{query[:100]}...', top_k={top_k}, threshold={threshold}"
        )

        try:
            # Validate retrieval state
            if not self.is_indexed or self.index is None:
                raise VectorDBError("Index not available - build index first")

            # Validate parameters
            self._validate_retrieval_parameters(query, top_k, threshold)

            # Generate query embedding
            query_embedding = self.embedding_model.encode(
                [query], show_progress_bar=False, convert_to_numpy=True
            )

            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)

            # Perform similarity search
            scores, indices = self.index.search(
                query_embedding.astype("float32"), min(top_k, len(self.chunks))
            )

            # Filter results by threshold and collect chunks
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx < len(self.chunks) and score > threshold:
                    results.append(self.chunks[idx])
                    logger.debug(
                        f"Selected chunk {idx} with similarity score {score:.3f}"
                    )

            logger.info(
                f"Retrieved {len(results)} relevant chunks (threshold: {threshold})"
            )
            return results

        except VectorDBError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during retrieval: {e}"
            logger.error(error_msg)
            raise VectorDBError(error_msg) from e

    def get_index_stats(self) -> dict:
        """
        Get comprehensive statistics about the current index.

        Returns:
            dict: Dictionary containing index statistics
        """
        stats = {
            "is_indexed": self.is_indexed,
            "model_name": self.model_name,
            "chunk_count": len(self.chunks),
            "embedding_dimension": self.embedding_dimension,
            "index_size": self.index.ntotal if self.index else 0,
        }

        if self.chunks:
            chunk_lengths = [len(chunk) for chunk in self.chunks]
            stats.update(
                {
                    "avg_chunk_length": np.mean(chunk_lengths),
                    "min_chunk_length": min(chunk_lengths),
                    "max_chunk_length": max(chunk_lengths),
                }
            )

        return stats

    def reset(self) -> None:
        """
        Reset the vector database to clean state for new document processing.

        """
        logger.info("Resetting VectorDB to clean state...")

        try:
            # Clear index and data
            self.index = None
            self.chunks.clear()
            self.is_indexed = False
            self.embedding_dimension = None

            logger.info("VectorDB reset completed successfully")

        except Exception as e:
            error_msg = f"Error during VectorDB reset: {e}"
            logger.error(error_msg)
            # Continue with reset even if there are errors
            self.index = None
            self.chunks = []
            self.is_indexed = False
            self.embedding_dimension = None

    def __len__(self) -> int:
        """Return the number of indexed chunks."""
        return len(self.chunks)

    def __bool__(self) -> bool:
        """Return True if the database is indexed and ready for use."""
        return self.is_indexed and self.index is not None

    def __repr__(self) -> str:
        """Return a string representation of the VectorDB instance."""
        return (
            f"VectorDB(model='{self.model_name}', "
            f"indexed={self.is_indexed}, "
            f"chunks={len(self.chunks)}, "
            f"dimension={self.embedding_dimension})"
        )
