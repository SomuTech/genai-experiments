"""
AI agents for research planning, execution, analysis, and reporting.

Author: SomuTech
Date: July 2025
License: MIT
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.tools import BaseTool, Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_google_genai import ChatGoogleGenerativeAI

from config import ResearchError, APIError
from models import CompactMemory, ResearchTask, TaskType

logger = logging.getLogger(__name__)


class SmartPlanner:
    """
    Intelligent research task planner that creates focused research strategies.

    This class analyzes research topics and creates optimized task sequences
    that balance comprehensiveness with efficiency.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize the planner with an LLM instance.

        Args:
            llm: Language model for planning operations
        """
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")

        self.llm = llm
        self.memory = CompactMemory()
        logger.info("Smart planner initialized")

    def create_research_plan(self, topic: str) -> List[ResearchTask]:
        """
        Create a strategic research plan for the given topic.

        Args:
            topic: Research topic to plan for

        Returns:
            List of research tasks to execute

        Raises:
            ValueError: If topic is empty or invalid
        """
        if not topic or not topic.strip():
            raise ValueError("Research topic cannot be empty")

        topic = topic.strip()
        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year

        logger.info(f"Creating research plan for: {topic}")

        try:
            tasks = [
                ResearchTask(
                    task_type=TaskType.OVERVIEW_RESEARCH,
                    description=f"Research fundamental concepts and latest {current_year} developments about {topic}",
                    max_tokens=2000,
                ),
                ResearchTask(
                    task_type=TaskType.CURRENT_TRENDS,
                    description=f"Find {current_year} trends, recent news, and latest statistics about {topic}",
                    max_tokens=1000,
                ),
                ResearchTask(
                    task_type=TaskType.DETAILED_ANALYSIS,
                    description=f"Gather {current_year} expert insights and current analysis of {topic}",
                    max_tokens=1000,
                ),
            ]

            logger.info(f"Created {len(tasks)} research tasks for {current_date}")
            return tasks

        except Exception as e:
            logger.error(f"Failed to create research plan: {str(e)}")
            raise ResearchError(f"Could not create research plan: {str(e)}")


class WebsiteSearchTool(BaseTool):
    """
    Custom tool for extracting and processing website content.

    This tool safely extracts content from web pages while handling
    errors gracefully and limiting content size to prevent token overflow.
    """

    name: str = "website_search"
    description: str = "Extract content from websites. Input should be a URL."

    _MAX_CONTENT_LENGTH = 2000

    def _run(
        self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Extract content from the specified URL.

        Args:
            url: URL to extract content from
            run_manager: Callback manager for the tool run

        Returns:
            Extracted and processed content
        """
        if not url or not url.strip():
            return "Error: Empty URL provided"

        url = url.strip()

        # Basic URL validation
        if not (url.startswith("http://") or url.startswith("https://")):
            return f"Error: Invalid URL format: {url}"

        try:
            logger.debug(f"Extracting content from: {url}")
            loader = WebBaseLoader(url)
            documents = loader.load()

            if not documents:
                return f"No content found at {url}"

            content = documents[0].page_content

            # Limit content length to prevent token overflow
            if len(content) > self._MAX_CONTENT_LENGTH:
                content = content[: self._MAX_CONTENT_LENGTH] + "..."
                logger.debug(
                    f"Content truncated to {self._MAX_CONTENT_LENGTH} characters"
                )

            return content

        except Exception as e:
            error_msg = f"Error accessing {url}: {str(e)}"
            logger.warning(error_msg)
            return error_msg


class EfficientResearcher:
    """
    Token-optimized research agent that executes research tasks efficiently.

    This class manages the research process, including prompt generation,
    agent execution, and result quality assessment.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI, tools: List[Tool]):
        """
        Initialize the researcher with LLM and tools.

        Args:
            llm: Language model for research operations
            tools: List of tools available for research
        """
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")
        if not tools:
            raise ValueError("At least one tool must be provided")

        self.llm = llm
        self.tools = tools

        try:
            self.agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=5,
                handle_parsing_errors=True,
            )
            logger.info("Research agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize research agent: {str(e)}")
            raise ResearchError(f"Could not initialize research agent: {str(e)}")

    def execute_task(
        self, task: ResearchTask, focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a research task with optional focus areas.

        Args:
            task: Research task to execute
            focus_areas: Optional list of areas to focus on

        Returns:
            Dictionary containing task results and metadata
        """
        if not isinstance(task, ResearchTask):
            raise TypeError("task must be a ResearchTask instance")

        logger.info(f"Executing task: {task.task_type}")

        try:
            prompt = self._generate_task_prompt(task, focus_areas)
            start_time = datetime.now()

            results = self.agent.run(prompt)

            execution_time = (datetime.now() - start_time).total_seconds()

            result_data = {
                "status": "completed",
                "content": results,
                "word_count": len(results.split()),
                "quality_score": self._assess_quality(results),
                "execution_time": execution_time,
            }

            logger.info(
                f"Task completed - Words: {result_data['word_count']}, "
                f"Quality: {result_data['quality_score']:.2f}"
            )

            return result_data

        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)

            return {
                "status": "failed",
                "error": str(e),
                "content": "",
                "word_count": 0,
                "quality_score": 0.0,
                "execution_time": 0.0,
            }

    def _generate_task_prompt(
        self, task: ResearchTask, focus_areas: Optional[List[str]]
    ) -> str:
        """
        Generate an optimized prompt for the research task.

        Args:
            task: Task to generate prompt for
            focus_areas: Optional focus areas to include

        Returns:
            Generated prompt string
        """
        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year

        # Create focus areas context
        focus_context = ""
        if focus_areas:
            focus_context = f"""
            SPECIFIC FOCUS AREAS to emphasize in your research:
            {' | '.join(focus_areas)}
            
            Pay special attention to these aspects during your research.
            """

        # Task-specific prompt templates
        prompt_templates = {
            TaskType.OVERVIEW_RESEARCH: f"""
            Research the fundamentals of: {task.description}
            
            TODAY'S DATE: {current_date}. Prioritize {current_year} information.
            {focus_context}
            
            Focus on:
            - Core definitions and concepts (latest understanding)
            - Recent background and developments
            - Current key facts and statistics
            - Latest categories or types
            
            Provide comprehensive but concise information. Target 800-1000 words of valuable content.
            """,
            TaskType.CURRENT_TRENDS: f"""
            Research LATEST trends and developments: {task.description}
            
            CRITICAL: Today is {current_date}. Focus ONLY on {current_year} and late 2024 information.
            {focus_context}
            
            Focus on:
            - News from the last 3-6 months
            - {current_year} statistics and data
            - Current market developments
            - Latest industry updates
            
            Provide specific, up-to-date information. Target 600-800 words.
            """,
            TaskType.DETAILED_ANALYSIS: f"""
            Research expert insights and analysis: {task.description}
            
            TODAY'S DATE: {current_date}. Find the most recent expert opinions from {current_year}.
            {focus_context}
            
            Focus on:
            - {current_year} expert opinions and analysis
            - Latest practical applications
            - Most recent future predictions
            - Current challenges and opportunities
            
            Provide analytical depth. Target 600-800 words.
            """,
        }

        return prompt_templates.get(task.task_type, task.description)

    def _assess_quality(self, content: str) -> float:
        """
        Assess the quality of research content.

        Args:
            content: Content to assess

        Returns:
            Quality score between 0.0 and 1.0
        """
        if not content:
            return 0.0

        score = 0.0

        # Length assessment
        word_count = len(content.split())
        if word_count > 300:
            score += 0.3

        # Source credibility indicators
        credibility_indicators = [
            "according to",
            "study",
            "research",
            "report",
            "survey",
            "analysis",
            "data shows",
            "statistics",
        ]
        if any(indicator in content.lower() for indicator in credibility_indicators):
            score += 0.3

        # Specific information (numbers, dates)
        if any(char.isdigit() for char in content):
            score += 0.2

        # Structure indicators
        if content.count("\n") > 3:
            score += 0.2

        return min(score, 1.0)


class QuickAnalyzer:
    """
    Fast analysis engine for synthesizing research findings into insights.
    """

    MAX_CONTENT_LENGTH = 8000

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize analyzer with language model.

        Args:
            llm: Language model for analysis operations
        """
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")

        self.llm = llm
        self.analysis_chain = self._create_analysis_chain()
        logger.info("Quick analyzer initialized")

    def _create_analysis_chain(self) -> LLMChain:
        """Create the analysis chain with optimized prompts."""
        prompt_template = PromptTemplate(
            input_variables=["research_content"],
            template="""
            Analyze this research content and extract key insights for blog writing:
            
            {research_content}
            
            Provide:
            1. 3-5 key takeaways (bullet points)
            2. Most important statistics or facts
            3. Interesting insights or trends
            4. Practical implications
            
            Keep analysis concise and blog-focused.
            """,
        )

        return LLMChain(llm=self.llm, prompt=prompt_template)

    def analyze(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze research results and generate insights.

        Args:
            research_results: Dictionary of research task results

        Returns:
            Analysis results with insights and metadata

        Raises:
            ResearchError: If analysis fails
        """
        if not research_results:
            raise ValueError("research_results cannot be empty")

        logger.info("Starting research analysis")

        try:
            # Combine all research content
            combined_content = self._combine_research_content(research_results)

            # Generate analysis
            analysis = self.analysis_chain.run({"research_content": combined_content})

            # Calculate metadata
            total_words = sum(
                result.get("word_count", 0)
                for result in research_results.values()
                if isinstance(result, dict)
            )

            quality_scores = [
                result.get("quality_score", 0)
                for result in research_results.values()
                if isinstance(result, dict) and result.get("quality_score") is not None
            ]

            average_quality = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            )

            result = {
                "key_insights": analysis,
                "total_words": total_words,
                "average_quality": average_quality,
                "successful_tasks": len(
                    [
                        r
                        for r in research_results.values()
                        if isinstance(r, dict) and r.get("status") == "completed"
                    ]
                ),
            }

            logger.info(
                f"Analysis completed - {total_words} words, "
                f"quality: {average_quality:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise ResearchError(f"Could not analyze research results: {str(e)}")

    def _combine_research_content(self, research_results: Dict[str, Any]) -> str:
        """
        Combine research content from all tasks.

        Args:
            research_results: Dictionary of research results

        Returns:
            Combined content string
        """
        combined_content = ""

        for task_type, result in research_results.items():
            if isinstance(result, dict) and result.get("content"):
                combined_content += f"=== {task_type.upper()} ===\n"
                combined_content += result["content"] + "\n\n"

        # Truncate if too long for token management
        if len(combined_content) > self.MAX_CONTENT_LENGTH:
            combined_content = combined_content[: self.MAX_CONTENT_LENGTH] + "..."
            logger.debug(
                f"Combined content truncated to {self.MAX_CONTENT_LENGTH} characters"
            )

        return combined_content


class BlogReportGenerator:
    """
    Generates comprehensive, blog-ready reports from research data.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize report generator with language model.

        Args:
            llm: Language model for report generation
        """
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")

        self.llm = llm
        self.report_chain = self._create_report_chain()
        logger.info("Blog report generator initialized")

    def _create_report_chain(self) -> LLMChain:
        """Create the report generation chain with structured templates."""
        prompt_template = PromptTemplate(
            input_variables=["topic", "research_content", "analysis"],
            template="""
            Create a comprehensive blog post about: {topic}
            
            Research Content: {research_content}
            Analysis: {analysis}
            
            Write a detailed blog post with:
            
            # {topic}: A Comprehensive Guide
            
            ## Introduction
            [Engaging introduction with hook and overview]
            
            ## What is {topic}?
            [Core concepts and definitions]
            
            ## Current State and Trends
            [Recent developments and statistics]
            
            ## Key Insights and Analysis
            [Expert perspectives and implications]
            
            ## Practical Applications
            [Real-world uses and examples]
            
            ## Future Outlook
            [Trends and predictions]
            
            ## Conclusion
            [Summary and key takeaways]
            
            ---
            
            **Word Count Target: 1500-2000 words**
            **Style: Informative, engaging, well-structured**
            **Include specific facts, statistics, and examples**
            """,
        )

        return LLMChain(llm=self.llm, prompt=prompt_template)

    def generate_blog_report(
        self, topic: str, research_results: Dict[str, Any], analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive blog report.

        Args:
            topic: Research topic
            research_results: Research task results
            analysis: Analysis results

        Returns:
            Generated blog report

        Raises:
            ResearchError: If report generation fails
        """
        if not topic or not topic.strip():
            raise ValueError("topic cannot be empty")
        if not research_results:
            raise ValueError("research_results cannot be empty")
        if not analysis:
            raise ValueError("analysis cannot be empty")

        logger.info(f"Generating blog report for: {topic}")

        try:
            # Prepare research content summary
            research_summary = self._prepare_research_summary(research_results)

            # Generate report
            report = self.report_chain.run(
                {
                    "topic": topic.strip(),
                    "research_content": research_summary,
                    "analysis": analysis.get("key_insights", ""),
                }
            )

            logger.info(f"Blog report generated - {len(report.split())} words")
            return report

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ResearchError(f"Could not generate blog report: {str(e)}")

    def _prepare_research_summary(self, research_results: Dict[str, Any]) -> str:
        """
        Prepare a summary of research results for report generation.

        Args:
            research_results: Dictionary of research results

        Returns:
            Formatted research summary
        """
        research_summary = ""
        max_content_per_task = 2000

        for task_type, result in research_results.items():
            if isinstance(result, dict) and result.get("content"):
                content = result["content"]

                # Truncate long content
                if len(content) > max_content_per_task:
                    content = content[:max_content_per_task] + "..."

                research_summary += f"**{task_type.replace('_', ' ').title()}:**\n"
                research_summary += f"{content}\n\n"

        return research_summary
