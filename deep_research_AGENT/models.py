"""
Data models and memory system for AI Research Assistant.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Enumeration of available research task types."""

    OVERVIEW_RESEARCH = "overview_research"
    DETAILED_ANALYSIS = "detailed_analysis"
    CURRENT_TRENDS = "current_trends"
    BLOG_SYNTHESIS = "blog_synthesis"

    def __str__(self) -> str:
        return self.value


@dataclass
class ResearchTask:
    """
    Represents a research task with its configuration and results.

    Attributes:
        task_type: The type of research task to perform
        description: Human-readable description of the task
        max_tokens: Maximum tokens to use for this task
        results: Task execution results (populated after execution)
    """

    task_type: TaskType
    description: str
    max_tokens: int
    results: Optional[Dict[str, Any]] = field(default=None)

    def __post_init__(self):
        """Validate task configuration after initialization."""
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if not self.description.strip():
            raise ValueError("description cannot be empty")


@dataclass
class ResearchMetrics:
    """
    Contains quality metrics for research results.

    Attributes:
        total_words: Total words researched
        average_quality: Average quality score (0.0 to 1.0)
        completion_time: Time taken to complete research
        successful_tasks: Number of successfully completed tasks
    """

    total_words: int
    average_quality: float
    completion_time: float
    successful_tasks: int


class CompactMemory:
    """
    Lightweight memory system for storing research patterns and quality metrics.

    This class maintains a rolling cache of successful research strategies
    and source quality assessments to improve future research operations.
    """

    MAX_ENTRIES = 20

    def __init__(self):
        """Initialize empty memory collections."""
        self.successful_queries: List[Dict[str, Any]] = []
        self.source_quality: Dict[str, List[float]] = {}
        logger.debug("Memory system initialized")

    def remember_success(self, query_type: str, approach: str) -> None:
        """
        Store a successful research approach.

        Args:
            query_type: Category of the research query
            approach: Description of the successful approach
        """
        if not query_type or not approach:
            logger.warning("Empty query_type or approach provided to memory")
            return

        entry = {
            "type": query_type.strip(),
            "approach": approach.strip(),
            "timestamp": datetime.now().isoformat(),
        }

        self.successful_queries.append(entry)

        # Maintain rolling cache
        if len(self.successful_queries) > self.MAX_ENTRIES:
            self.successful_queries = self.successful_queries[-self.MAX_ENTRIES :]

        logger.debug(f"Stored successful approach for {query_type}")

    def get_success_patterns(self, query_type: str) -> List[Dict[str, Any]]:
        """
        Retrieve successful patterns for a given query type.

        Args:
            query_type: Type of query to retrieve patterns for

        Returns:
            List of successful patterns matching the query type
        """
        return [
            entry for entry in self.successful_queries if entry["type"] == query_type
        ]
