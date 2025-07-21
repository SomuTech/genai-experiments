"""
Configuration and exception handling for AI Research Assistant.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("research_agent.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


class ResearchError(Exception):
    """Raised when research operations fail."""

    pass


class APIError(Exception):
    """Raised when external API calls fail."""

    pass


def load_environment_variables() -> None:
    """
    Load and validate environment variables.

    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    load_dotenv()

    # Set user agent for web requests
    os.environ["USER_AGENT"] = "AI Research Assistant v1.0"

    # Validate required API keys
    required_keys = ["SERPER_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        raise ConfigurationError(
            f"Missing required environment variables: {', '.join(missing_keys)}"
        )

    # Set API keys in environment
    for key in required_keys:
        os.environ[key] = os.getenv(key)

    logger.info("Environment variables loaded successfully")


def get_llm(temperature: float = 0.3, max_tokens: int = 5000) -> ChatGoogleGenerativeAI:
    """
    Initialize and configure the Gemini language model.

    Args:
        temperature: Model temperature for creativity control
        max_tokens: Maximum tokens for model output

    Returns:
        Configured ChatGoogleGenerativeAI instance

    Raises:
        ConfigurationError: If model initialization fails
    """
    current_date = datetime.now().strftime("%B %d, %Y")

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite-preview-06-17",
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            max_output_tokens=max_tokens,
            verbose=False,
            model_kwargs={
                "system_instruction": (
                    f"Current date: {current_date}. Always prioritize the most "
                    "recent information when available. Provide accurate, "
                    "well-structured, and comprehensive responses."
                )
            }, 
        )

        logger.info("Language model initialized successfully")
        return llm

    except Exception as e:
        logger.error(f"Failed to initialize language model: {str(e)}")
        raise ConfigurationError(f"Could not initialize language model: {str(e)}")
