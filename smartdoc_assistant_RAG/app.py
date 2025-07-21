"""
SmartDoc Assistant - Streamlit Web Application

A professional document processing and chat application that combines RAG (Retrieval-Augmented
Generation) capabilities with an intuitive web interface for document-based question answering.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

import streamlit as st

from file_processor import extract_text_from_file
from rag import EnhancedRAG

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SmartDocAssistant:
    """
    Main application class for SmartDoc Assistant web interface.

    This class handles the Streamlit web application, session management,
    UI components, and user interactions for the document chat system.
    """

    # Application constants
    APP_TITLE = "SmartDoc Assistant"
    APP_ICON = "🤖"
    MAX_FILE_SIZE_MB = 20
    SUPPORTED_FORMATS = ["pdf", "docx", "txt"]

    # UI styling constants
    CHAT_CONTAINER_HEIGHT = "500px"
    TIMESTAMP_FORMAT = "%H:%M"

    def __init__(self):
        """Initialize the SmartDoc Assistant application."""
        logger.info("Initializing SmartDoc Assistant application")
        self._configure_page()
        self._inject_custom_styles()
        self._initialize_session_state()

    def _configure_page(self) -> None:
        """Configure Streamlit page settings and metadata."""
        try:
            st.set_page_config(
                page_title=self.APP_TITLE,
                page_icon=self.APP_ICON,
                layout="wide",
                initial_sidebar_state="expanded",
            )
            logger.debug("Page configuration completed successfully")
        except Exception as e:
            logger.error(f"Failed to configure page: {e}")
            raise

    def _inject_custom_styles(self) -> None:
        """Inject custom CSS styles for enhanced UI appearance."""
        try:
            custom_css = """
            <style>
                /* Chat container styling */
                .chat-container {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    border: 1px solid #dee2e6;
                    max-height: 500px;
                    overflow-y: auto;
                }
                
                /* Message timestamp styling */
                .message-time {
                    font-size: 11px;
                    color: #6c757d;
                    text-align: right;
                    margin-top: 5px;
                    font-style: italic;
                }
                
                /* Session info styling */
                .session-info {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px 0;
                }
                
                /* Input area styling */
                .chat-input-area {
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 1px solid #dee2e6;
                }
                
                /* Welcome message styling */
                .welcome-container {
                    text-align: center;
                    color: #6c757d;
                    padding: 30px;
                }
                
                /* Error message styling */
                .stError {
                    margin-top: 10px;
                }
            </style>
            """

            st.markdown(custom_css, unsafe_allow_html=True)
            logger.debug("Custom CSS styles injected successfully")

        except Exception as e:
            logger.warning(f"Failed to inject custom styles: {e}")

    def _initialize_session_state(self) -> None:
        """Initialize and configure Streamlit session state variables."""
        try:
            # Initialize RAG model
            if "rag_model" not in st.session_state:
                try:
                    st.session_state.rag_model = EnhancedRAG()
                    logger.info("RAG model initialized successfully")
                except ValueError as e:
                    error_msg = f"❌ Failed to initialize RAG model: {str(e)}"
                    st.error(error_msg)
                    logger.error(error_msg)
                    st.stop()

            # Initialize other session variables with defaults
            session_defaults = {
                "chat_history": [],
                "file_processed": False,
                "message_timestamps": [],
                "current_document_name": None,
                "document_stats": {},
            }

            for key, default_value in session_defaults.items():
                st.session_state.setdefault(key, default_value)

            logger.debug("Session state initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize session state: {e}")
            raise

    @staticmethod
    def generate_timestamp() -> str:
        """
        Generate current timestamp in HH:MM format.

        Returns:
            str: Formatted timestamp string
        """
        return datetime.now().strftime(SmartDocAssistant.TIMESTAMP_FORMAT)

    @staticmethod
    def display_message_with_timestamp(
        message: Dict[str, Any], role: str, timestamp: Optional[str] = None
    ) -> None:
        """
        Display a chat message with WhatsApp-style timestamp.

        Args:
            message (Dict[str, Any]): Message dictionary containing content
            role (str): Message role ('user' or 'assistant')
            timestamp (Optional[str]): Message timestamp
        """
        try:
            with st.chat_message(role):
                # Display message content
                if isinstance(message, dict) and "content" in message:
                    st.write(message["content"])
                else:
                    st.write(str(message))

                # Display timestamp if provided
                if timestamp:
                    st.markdown(
                        f'<div class="message-time">{timestamp}</div>',
                        unsafe_allow_html=True,
                    )
        except Exception as e:
            logger.warning(f"Error displaying message: {e}")
            st.error("Error displaying message")

    def _handle_file_upload(self) -> None:
        """Handle document file upload and processing."""
        st.header("📁 Document Upload")

        try:
            # File upload widget
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=self.SUPPORTED_FORMATS,
                help=f"Upload {', '.join(self.SUPPORTED_FORMATS).upper()} files (Max: {self.MAX_FILE_SIZE_MB}MB)",
                key="file_uploader",
            )

            if uploaded_file is not None:
                # Validate file size
                file_size_mb = uploaded_file.size / (1024 * 1024)
                if file_size_mb > self.MAX_FILE_SIZE_MB:
                    st.error(
                        f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({self.MAX_FILE_SIZE_MB}MB)"
                    )
                    return

                # Process the uploaded file
                self._process_uploaded_file(uploaded_file)

        except Exception as e:
            error_msg = f"Error handling file upload: {e}"
            logger.error(error_msg)
            st.error("❌ Failed to handle file upload. Please try again.")

    def _process_uploaded_file(self, uploaded_file) -> None:
        """
        Process the uploaded file and update session state.

        Args:
            uploaded_file: Streamlit uploaded file object
        """
        try:
            with st.spinner("🔄 Processing document..."):
                logger.info(f"Processing uploaded file: {uploaded_file.name}")

                # Extract text from file
                text = extract_text_from_file(uploaded_file)

                if text and text.strip():
                    # Build document index
                    st.session_state.rag_model.build_index(text)

                    # Update session state
                    st.session_state.file_processed = True
                    st.session_state.current_document_name = uploaded_file.name

                    # Calculate document statistics
                    char_count = len(text)
                    word_count = len(text.split())
                    st.session_state.document_stats = {
                        "characters": char_count,
                        "words": word_count,
                        "file_size": uploaded_file.size,
                    }

                    # Display success message and stats
                    st.success(f"✅ Successfully processed: {uploaded_file.name}")
                    st.info(
                        f"📄 Document: {char_count:,} characters, {word_count:,} words"
                    )

                    logger.info(
                        f"Document processed successfully: {word_count} words, {char_count} characters"
                    )

                else:
                    st.error(
                        "❌ Could not extract text from file. Please check the file format and try again."
                    )
                    logger.warning(
                        f"Failed to extract text from file: {uploaded_file.name}"
                    )

        except Exception as e:
            error_msg = f"Error processing file {uploaded_file.name}: {e}"
            logger.error(error_msg)
            st.error(
                "❌ Failed to process document. Please try again with a different file."
            )

    def _render_chat_controls(self) -> None:
        """Render chat control buttons in the sidebar."""
        st.header("💬 Chat Controls")

        try:
            # Clear chat history button
            if st.button(
                "🔄 Clear Chat History", use_container_width=True, key="clear_chat"
            ):
                self._clear_chat_history()

            # Remove document button
            if st.button(
                "🗑️ Remove Document", use_container_width=True, key="remove_doc"
            ):
                self._remove_current_document()

        except Exception as e:
            logger.error(f"Error rendering chat controls: {e}")
            st.error("❌ Error with chat controls")

    def _clear_chat_history(self) -> None:
        """Clear the chat history and timestamps."""
        try:
            st.session_state.chat_history = []
            st.session_state.message_timestamps = []
            logger.info("Chat history cleared successfully")
            st.rerun()
        except Exception as e:
            logger.error(f"Error clearing chat history: {e}")
            st.error("❌ Failed to clear chat history")

    def _remove_current_document(self) -> None:
        """Remove the currently loaded document and reset the index."""
        try:
            st.session_state.file_processed = False
            st.session_state.current_document_name = None
            st.session_state.document_stats = {}
            st.session_state.rag_model.reset_index()
            logger.info("Current document removed and index reset")
            st.rerun()
        except Exception as e:
            logger.error(f"Error removing document: {e}")
            st.error("❌ Failed to remove document")

    def _render_session_info(self) -> None:
        """Render session information in the sidebar."""
        st.header("📊 Session Info")

        try:
            # Session info container with custom styling
            st.markdown('<div class="session-info">', unsafe_allow_html=True)

            # Display metrics in columns
            col1, col2 = st.columns(2)

            with col1:
                message_count = len(st.session_state.chat_history)
                st.metric("Messages", message_count)

            with col2:
                doc_status = "✅ Yes" if st.session_state.file_processed else "❌ No"
                st.metric("Document", doc_status)

            # Show additional info if document is loaded
            if (
                st.session_state.file_processed
                and st.session_state.current_document_name
            ):
                st.caption(f"📎 {st.session_state.current_document_name}")

                # Show conversation context info
                if st.session_state.chat_history:
                    st.caption("💭 Last 10 messages used for context")

            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            logger.error(f"Error rendering session info: {e}")
            st.error("❌ Error displaying session info")

    def _ensure_timestamp_sync(self) -> None:
        """Ensure message timestamps list is synchronized with chat history."""
        try:
            while len(st.session_state.message_timestamps) < len(
                st.session_state.chat_history
            ):
                st.session_state.message_timestamps.append(self.generate_timestamp())
        except Exception as e:
            logger.warning(f"Error synchronizing timestamps: {e}")

    def _render_chat_history(self) -> None:
        """Render the chat history with timestamps in a styled container."""
        try:
            # Start chat container
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)

            if st.session_state.chat_history:
                # Ensure timestamps are synchronized
                self._ensure_timestamp_sync()

                # Display each message with its timestamp
                for i, message in enumerate(st.session_state.chat_history):
                    timestamp = (
                        st.session_state.message_timestamps[i]
                        if i < len(st.session_state.message_timestamps)
                        else None
                    )

                    self.display_message_with_timestamp(
                        message, message["role"], timestamp
                    )
            else:
                # Display welcome message
                self._render_welcome_message()

            # Close chat container
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            logger.error(f"Error rendering chat history: {e}")
            st.error("❌ Error displaying chat history")

    def _render_welcome_message(self) -> None:
        """Render welcome message when no chat history exists."""
        welcome_html = """
        <div class="welcome-container">
            <h5>👋 Welcome to SmartDoc Assistant!</h5>
            <p>Upload a document to get started or ask general questions.</p>
        </div>
        """
        st.markdown(welcome_html, unsafe_allow_html=True)

    def _get_chat_placeholder_text(self) -> str:
        """
        Generate dynamic placeholder text for chat input based on application state.

        Returns:
            str: Appropriate placeholder text
        """
        return (
            "Ask me anything about your document..."
            if st.session_state.file_processed
            else "Upload a document first, or ask general questions..."
        )

    def _handle_user_input(self, user_prompt: str) -> None:
        """
        Process user input and generate AI response.

        Args:
            user_prompt (str): User's input message
        """
        try:
            logger.info(f"Processing user input: '{user_prompt[:50]}...'")

            # Generate timestamps
            user_timestamp = self.generate_timestamp()

            # Display user message immediately
            with st.chat_message("user"):
                st.write(user_prompt)
                st.markdown(
                    f'<div class="message-time">{user_timestamp}</div>',
                    unsafe_allow_html=True,
                )

            # Generate and display AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        response, updated_history = st.session_state.rag_model.chat(
                            user_prompt, st.session_state.chat_history
                        )

                        # Display response
                        st.write(response)

                        # Generate assistant timestamp
                        assistant_timestamp = self.generate_timestamp()
                        st.markdown(
                            f'<div class="message-time">{assistant_timestamp}</div>',
                            unsafe_allow_html=True,
                        )

                        # Update session state
                        st.session_state.chat_history = updated_history
                        st.session_state.message_timestamps.extend(
                            [user_timestamp, assistant_timestamp]
                        )

                        logger.info("User input processed successfully")

                    except Exception as e:
                        error_msg = f"Error generating response: {e}"
                        logger.error(error_msg)
                        st.error("❌ Sorry, I encountered an error. Please try again.")

        except Exception as e:
            logger.error(f"Error handling user input: {e}")
            st.error("❌ Failed to process your message. Please try again.")

    def _render_chat_interface(self) -> None:
        """Render the main chat interface."""
        try:

            # Render chat history
            self._render_chat_history()

            # Render chat input area
            st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)

            # Get dynamic placeholder text
            placeholder_text = self._get_chat_placeholder_text()

            # Chat input widget
            user_prompt = st.chat_input(placeholder_text, key="main_chat_input")

            if user_prompt:
                # Validate that document is loaded (if required)
                if not st.session_state.file_processed:
                    st.error("❌ Please upload a document first!")
                    logger.warning("User attempted to chat without uploading document")
                else:
                    # Process user input
                    self._handle_user_input(user_prompt)

            # Show helpful hint when no document is uploaded
            if not st.session_state.file_processed:
                st.info(
                    "💡 **Tip:** Upload a document to ask specific questions about its content, or ask general questions for web-based answers."
                )

            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            logger.error(f"Error rendering chat interface: {e}")
            st.error("❌ Error with chat interface")

    def render_sidebar(self) -> None:
        """Render the complete sidebar with all components."""
        try:
            with st.sidebar:
                # File upload section
                self._handle_file_upload()
                st.divider()

                # Chat controls section
                self._render_chat_controls()
                st.divider()

                # Session information section
                self._render_session_info()

        except Exception as e:
            logger.error(f"Error rendering sidebar: {e}")
            st.error("❌ Error with sidebar components")

    def run(self) -> None:
        """Run the main application."""
        try:
            logger.info("Starting SmartDoc Assistant application")

            # Render main header
            st.title(f"{self.APP_ICON} {self.APP_TITLE}")
            st.markdown(
                "Upload documents and chat with their content using Perplexity AI"
            )

            # Render sidebar
            self.render_sidebar()

            # Render main chat interface
            self._render_chat_interface()

        except Exception as e:
            logger.error(f"Critical error in application: {e}")
            st.error("❌ A critical error occurred. Please refresh the page.")


def main() -> None:
    """Main entry point for the Streamlit application."""
    try:
        app = SmartDocAssistant()
        app.run()
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        st.error(
            "❌ Failed to start the application. Please check the logs and try again."
        )


if __name__ == "__main__":
    main()
