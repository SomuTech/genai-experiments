"""
Enhanced RAG (Retrieval-Augmented Generation) System

This module provides an intelligent document processing and question-answering system
that combines vector database retrieval with Perplexity AI for generating responses.

Author: SomuTech
Date: July 2025
License: MIT
"""

import os
import logging
import re
from typing import List, Dict, Tuple, Optional

import requests
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from vector_store import VectorDB

# Load environment variables
load_dotenv()

# Configure logging with proper formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("rag_app.log"), logging.StreamHandler()],
)


class EnhancedRAG:
    """
    Enhanced Retrieval-Augmented Generation system for document-based question answering.

    This class combines local vector search capabilities with Perplexity AI to provide
    intelligent responses based on uploaded documents and conversation history.

    """

    # Class constants
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    MAX_CHAT_HISTORY = 10
    API_TIMEOUT = 60
    DEFAULT_MODEL = "sonar"

    def __init__(self) -> None:
        """
        Initialize the Enhanced RAG system.

        Raises:
            ValueError: If PERPLEXITY_API_KEY environment variable is not set
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing EnhancedRAG system...")

        try:
            # Initialize vector database for document storage
            self.vector_db = VectorDB()
            self.logger.debug("Vector database initialized successfully")

            # Initialize local embedding model (kept for potential future use)
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.logger.debug("Embedding model loaded successfully")

            # Initialize legacy attributes for backward compatibility
            self.index = None
            self.chunks = []
            self.is_indexed = False

            # Configure Perplexity API
            self._setup_perplexity_api()

            self.logger.info("EnhancedRAG system initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize EnhancedRAG: {e}")
            raise

    def _setup_perplexity_api(self) -> None:
        """
        Configure Perplexity API settings and validate API key.

        Raises:
            ValueError: If PERPLEXITY_API_KEY environment variable is not found
        """
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")

        if not self.perplexity_api_key:
            error_msg = "PERPLEXITY_API_KEY not found in environment variables"
            self.logger.error(error_msg)
            raise ValueError("Please set PERPLEXITY_API_KEY environment variable")

        self.perplexity_url = self.PERPLEXITY_API_URL
        self.logger.debug("Perplexity API configuration completed")

    def chunk_text(self, text: str) -> None:
        """
        Delegate text chunking to the vector database.

        Args:
            text (str): Input text to be chunked
        """
        self.logger.debug("Delegating text chunking to vector database")
        self.vector_db.chunk_text(text)

    def build_index(self, text: str) -> None:
        """
        Build document index using the vector database.

        Args:
            text (str): Document text to be indexed
        """
        self.logger.info("Building document index...")

        try:
            self.vector_db.build_index(text)
            self.logger.info("Document index built successfully")

        except Exception as e:
            self.logger.error(f"Failed to build document index: {e}")
            raise

    def retrieve_context(self, query: str) -> List[str]:
        """
        Retrieve relevant document chunks for a given query.

        Args:
            query (str): User query to search for relevant context

        Returns:
            List[str]: List of relevant document chunks
        """
        self.logger.debug(f"Retrieving context for query: '{query[:50]}...'")

        try:
            context_chunks = self.vector_db.retrieve(query)
            self.logger.debug(f"Retrieved {len(context_chunks)} context chunks")
            return context_chunks

        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            return []

    def clean_response(self, response: str) -> str:
        """
        Clean AI response by removing thinking steps and formatting artifacts.

        Args:
            response (str): Raw response from AI model

        Returns:
            str: Cleaned response text
        """
        if not response:
            return ""

        try:
            # Remove thinking blocks and reasoning patterns
            patterns_to_remove = [
                (r"<think>.*?</think>", "thinking blocks"),
                (r"\[THINKING\].*?\[/THINKING\]", "thinking sections"),
                (r"Let me think about this.*?\n\n", "thinking phrases"),
            ]

            cleaned = response
            for pattern, description in patterns_to_remove:
                original_length = len(cleaned)
                cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)

                if len(cleaned) < original_length:
                    self.logger.debug(f"Removed {description} from response")

            # Clean up excessive whitespace
            cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
            cleaned = cleaned.strip()

            return cleaned

        except Exception as e:
            self.logger.warning(f"Error cleaning response: {e}, returning original")
            return response.strip()

    def _build_system_message(self) -> Dict[str, str]:
        """
        Build the system message for the AI assistant.

        Returns:
            Dict[str, str]: System message configuration
        """
        return {
            "role": "system",
            "content": """You are a helpful AI assistant that answers questions based on the provided document context.
            
            IMPORTANT RULES:
            - ONLY use information from the "Context from document" section
            - If the document context doesn't contain the answer, clearly state this
            - Be specific and cite relevant parts of the document
            - Do not include <think> tags or reasoning steps in your response
            - Provide a report or summary based on the conversation so far when user asks
            - Be polite and build friendly conversation.
            
            Respond naturally to the user's question. If you find relevant information in the document, use it. If not, or if you need more current information, search the web. Be conversational and helpful.
            """,
        }

    def _build_conversation_messages(
        self, query: str, context: List[str], chat_history: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Build conversation messages for the AI model.

        Args:
            query (str): Current user query
            context (List[str]): Retrieved document context
            chat_history (List[Dict]): Previous conversation history

        Returns:
            List[Dict[str, str]]: Formatted messages for the AI model
        """
        messages = [self._build_system_message()]

        # Add recent chat history (last 10 messages)
        recent_history = (
            chat_history[-self.MAX_CHAT_HISTORY :]
            if len(chat_history) > self.MAX_CHAT_HISTORY
            else chat_history
        )

        for entry in recent_history:
            if isinstance(entry, dict) and "role" in entry and "content" in entry:
                messages.append(
                    {
                        "role": "user" if entry["role"] == "user" else "assistant",
                        "content": entry["content"],
                    }
                )

        # Prepare context text
        if context:
            context_text = "\n\n".join(context)
            self.logger.debug(f"Using {len(context)} context chunks")
        else:
            context_text = "No relevant context found in the uploaded document."
            self.logger.debug("No document context available")

        # Add current query with context
        current_message = f"""Context from document:
        {context_text}


        Question: {query}


        Provide a clean, direct response without showing thinking steps."""

        messages.append({"role": "user", "content": current_message})

        return messages

    def generate_response(
        self, query: str, context: List[str], chat_history: List[Dict]
    ) -> str:
        """
        Generate AI response using Perplexity API with conversation context.

        Args:
            query (str): User query
            context (List[str]): Retrieved document context
            chat_history (List[Dict]): Conversation history

        Returns:
            str: Generated AI response
        """
        self.logger.info("Generating AI response...")

        try:
            # Build conversation messages
            messages = self._build_conversation_messages(query, context, chat_history)

            # Prepare API request payload
            payload = {
                "model": self.DEFAULT_MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
            }

            # Make API request
            self.logger.debug("Sending request to Perplexity API...")
            response = self._make_api_request(payload)

            if response:
                # Extract and clean response
                raw_response = response.json()["choices"][0]["message"]["content"]
                cleaned_response = self.clean_response(raw_response)

                self.logger.info("AI response generated and cleaned successfully")
                return cleaned_response
            else:
                return "Sorry, I encountered an error while generating the response."

        except Exception as e:
            error_msg = f"Unexpected error in response generation: {e}"
            self.logger.error(error_msg)
            return "Sorry, I encountered an unexpected error. Please try again."

    def _make_api_request(self, payload: Dict) -> Optional[requests.Response]:
        """
        Make HTTP request to Perplexity API with proper error handling.

        Args:
            payload (Dict): Request payload for the API

        Returns:
            Optional[requests.Response]: API response object or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=self.API_TIMEOUT,
            )

            # Check for successful response
            if response.status_code == 200:
                self.logger.debug("API request successful")
                return response
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                self.logger.error(error_msg)
                return None

        except requests.exceptions.Timeout:
            self.logger.error("API request timed out")
            return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return None

    def reset_index(self) -> None:
        """
        Reset the vector database index for processing a new document.
        """
        self.logger.info("Resetting document index...")

        try:
            self.vector_db.reset()
            self.logger.info("Document index reset successfully")

        except Exception as e:
            self.logger.error(f"Error resetting index: {e}")
            raise

    def chat(self, query: str, chat_history: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Main chat function for processing user queries and maintaining conversation.

        Args:
            query (str): User input query
            chat_history (List[Dict]): Previous conversation messages

        Returns:
            Tuple[str, List[Dict]]: AI response and updated chat history
        """
        if not query or not isinstance(query, str):
            self.logger.warning("Invalid query provided")
            return "Please provide a valid question.", chat_history

        self.logger.info(f"Processing chat query: '{query[:50]}...'")

        try:
            # Retrieve relevant context from document
            context = self.retrieve_context(query)

            # Generate AI response
            response = self.generate_response(query, context, chat_history)

            # Update conversation history
            updated_history = chat_history.copy()
            updated_history.extend(
                [
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": response},
                ]
            )

            self.logger.info("Chat interaction completed successfully")
            return response, updated_history

        except Exception as e:
            error_msg = f"Error during chat processing: {e}"
            self.logger.error(error_msg)
            return (
                "I apologize, but I encountered an error. Please try again.",
                chat_history,
            )
