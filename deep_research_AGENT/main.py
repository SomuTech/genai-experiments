"""
AI Research Assistant - Main coordination and CLI interface.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain_community.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI

from config import (
    load_environment_variables,
    get_llm,
    ConfigurationError,
    ResearchError,
    APIError,
)
from agents import (
    SmartPlanner,
    EfficientResearcher,
    QuickAnalyzer,
    BlogReportGenerator,
    WebsiteSearchTool,
)

logger = logging.getLogger(__name__)


class StreamlinedCoordinator:
    """
    Main orchestration class that coordinates all research operations.

    This class manages the entire research pipeline from planning to
    final report generation, providing a simple interface for complex
    multi-agent research operations.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize coordinator with all necessary components.

        Args:
            llm: Language model for research operations
        """
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")

        self.llm = llm

        try:
            # Initialize tools
            self.tools = self._initialize_tools()

            # Initialize agents and components
            self.planner = SmartPlanner(llm)
            self.researcher = EfficientResearcher(llm, self.tools)
            self.analyzer = QuickAnalyzer(llm)
            self.reporter = BlogReportGenerator(llm)

            logger.info("Streamlined coordinator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize coordinator: {str(e)}")
            raise ResearchError(f"Could not initialize coordinator: {str(e)}")

    def _initialize_tools(self) -> List[Tool]:
        """
        Initialize research tools.

        Returns:
            List of initialized tools

        Raises:
            APIError: If tool initialization fails
        """
        try:
            serper_search = GoogleSerperAPIWrapper()

            tools = [
                Tool(
                    name="Google Search",
                    func=serper_search.run,
                    description="Search Google for current information and comprehensive results.",
                ),
                WebsiteSearchTool(),
            ]

            logger.info(f"Initialized {len(tools)} research tools")
            return tools

        except Exception as e:
            logger.error(f"Tool initialization failed: {str(e)}")
            raise APIError(f"Could not initialize research tools: {str(e)}")

    def conduct_research(
        self, topic: str, focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Conduct comprehensive research on the given topic.

        Args:
            topic: Research topic
            focus_areas: Optional list of areas to focus research on

        Returns:
            Generated blog report

        Raises:
            ResearchError: If research process fails
        """
        if not topic or not topic.strip():
            raise ValueError("Research topic cannot be empty")

        topic = topic.strip()
        logger.info(f"Starting comprehensive research on: {topic}")

        start_time = datetime.now()

        try:
            # Step 1: Create research plan
            logger.info("Creating focused research plan...")
            tasks = self.planner.create_research_plan(topic)

            # Step 2: Execute research tasks
            logger.info("Executing research tasks...")
            research_results = {}

            for i, task in enumerate(tasks, 1):
                logger.info(f"Task {i}/{len(tasks)}: {task.task_type}")

                result = self.researcher.execute_task(task, focus_areas)
                research_results[task.task_type.value] = result

                if result["status"] == "completed":
                    logger.info(
                        f"Task completed - {result['word_count']} words, "
                        f"Quality: {result['quality_score']:.2f}"
                    )
                else:
                    logger.warning(
                        f"Task failed: {result.get('error', 'Unknown error')}"
                    )

            # Step 3: Analyze findings
            logger.info("Analyzing research findings...")
            analysis = self.analyzer.analyze(research_results)

            # Step 4: Generate report
            logger.info("Generating comprehensive blog report...")
            final_report = self.reporter.generate_blog_report(
                topic, research_results, analysis
            )

            # Log completion metrics
            completion_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Research completed in {completion_time:.1f} seconds")
            logger.info(f"Generated report: {len(final_report.split())} words")

            return final_report

        except Exception as e:
            logger.error(f"Research process failed: {str(e)}")
            raise ResearchError(f"Could not complete research: {str(e)}")


def main() -> None:
    """
    Main execution function for command-line interface.

    Provides a simple CLI for testing and demonstration purposes.
    """
    print("AI Research Assistant v1.0")
    print("=" * 50)

    try:
        # Load configuration
        load_environment_variables()

        # Get user input
        topic = input("\nEnter your research topic: ").strip()

        if not topic:
            print("Please provide a valid research topic")
            return

        # Initialize system
        logger.info("Initializing research system...")
        llm = get_llm()
        coordinator = StreamlinedCoordinator(llm)

        # Conduct research
        print(f"\nStarting research on: {topic}")
        start_time = datetime.now()

        blog_report = coordinator.conduct_research(topic)

        end_time = datetime.now()
        duration = end_time - start_time

        # Display results
        print("\n" + "=" * 60)
        print("RESEARCH REPORT")
        print("=" * 60)
        print(blog_report)
        print("\n" + "=" * 60)
        print(f"Research completed in: {duration}")
        print(f"Report length: {len(blog_report.split())} words")

    except ConfigurationError as e:
        print(f"\nConfiguration Error: {e}")
        print("Please check your environment variables and API keys")

    except ResearchError as e:
        print(f"\nResearch Error: {e}")
        print("Please try a different topic or check your internet connection")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected Error: {e}")
        print("Please check the logs for more details")


if __name__ == "__main__":
    main()
