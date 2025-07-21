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
from langchain_google_genai import ChatGoogleGenerativeAI

from config import ResearchError
from models import CompactMemory, ResearchTask, TaskType

logger = logging.getLogger(__name__)


class SmartPlanner:
    """Intelligent research task planner with focus area optimization."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")
        
        self.llm = llm
        self.memory = CompactMemory()
        logger.info("Smart planner initialized")
    
    def create_research_plan(self, topic: str) -> List[ResearchTask]:
        """Create focused research plan with reduced token usage."""
        if not topic or not topic.strip():
            raise ValueError("Research topic cannot be empty")
        
        topic = topic.strip()
        current_year = datetime.now().year
        
        logger.info(f"Creating research plan for: {topic}")
        
        try:
            tasks = [
                ResearchTask(
                    task_type=TaskType.OVERVIEW_RESEARCH,
                    description=f"Core concepts and {current_year} basics of {topic}",
                    max_tokens=800
                ),
                ResearchTask(
                    task_type=TaskType.CURRENT_TRENDS,
                    description=f"{current_year} trends and news about {topic}",
                    max_tokens=600
                ),
                ResearchTask(
                    task_type=TaskType.DETAILED_ANALYSIS,
                    description=f"Expert insights and practical info on {topic}",
                    max_tokens=600
                )
            ]
            
            logger.info(f"Created {len(tasks)} optimized research tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to create research plan: {str(e)}")
            raise ResearchError(f"Could not create research plan: {str(e)}")


class WebsiteSearchTool(BaseTool):
    """Optimized website content extraction tool."""
    
    name: str = "website_search"
    description: str = "Get key info from websites. Input: URL"
    
    _MAX_CONTENT_LENGTH = 1000  # Reduced from 2000
    
    def _run(self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not url or not url.strip():
            return "Error: No URL provided"
        
        url = url.strip()
        
        if not (url.startswith("http://") or url.startswith("https://")):
            return f"Error: Invalid URL: {url}"
        
        try:
            loader = WebBaseLoader(url)
            documents = loader.load()
            
            if not documents:
                return f"No content found at {url}"
            
            content = documents[0].page_content
            
            if len(content) > self._MAX_CONTENT_LENGTH:
                content = content[:self._MAX_CONTENT_LENGTH] + "..."
            
            return content
            
        except Exception as e:
            return f"Error: {str(e)}"


class EfficientResearcher:
    """Token-optimized research agent with focus area integration."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI, tools: List[Tool]):
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
                max_iterations=3,  # Reduced from 5
                handle_parsing_errors=True
            )
            logger.info("Research agent initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize research agent: {str(e)}")
            raise ResearchError(f"Could not initialize research agent: {str(e)}")
    
    def execute_task(self, task: ResearchTask, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute research with focus area optimization."""
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
                "execution_time": execution_time
            }
            
            logger.info(f"Task completed - Words: {result_data['word_count']}")
            return result_data
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "content": "",
                "word_count": 0,
                "quality_score": 0.0,
                "execution_time": 0.0
            }
    
    def _generate_task_prompt(self, task: ResearchTask, focus_areas: Optional[List[str]]) -> str:
        """Generate optimized, focus-based prompts."""
        current_date = datetime.now().strftime("%B %Y")
        
        # Create focused search terms based on focus areas
        focus_search = ""
        if focus_areas:
            focus_keywords = []
            for area in focus_areas[:3]:  # Limit to top 3 areas
                if "trends" in area.lower():
                    focus_keywords.append("trends")
                elif "market" in area.lower():
                    focus_keywords.append("market data")
                elif "expert" in area.lower():
                    focus_keywords.append("expert opinion")
                elif "technology" in area.lower():
                    focus_keywords.append("technology")
                elif "financial" in area.lower():
                    focus_keywords.append("financial impact")
            
            if focus_keywords:
                focus_search = f"Focus on: {', '.join(focus_keywords[:2])}"
        
        # Streamlined prompts with token optimization
        prompts = {
            TaskType.OVERVIEW_RESEARCH: f"""
Find basic info about: {task.description}
Date: {current_date}
{focus_search}

Search for recent info and provide:
- What it is (simple explanation)
- Why it matters
- Current status in 2025
- Key facts and numbers

Keep it simple and clear. 300-500 words max.
""",
            
            TaskType.CURRENT_TRENDS: f"""
Find latest news about: {task.description}
Date: {current_date}
{focus_search}

Search for 2025 updates and provide:
- Recent developments
- New statistics or data
- Market changes
- What's happening now

Focus on current year only. 200-400 words max.
""",
            
            TaskType.DETAILED_ANALYSIS: f"""
Find expert views on: {task.description}
Date: {current_date}
{focus_search}

Search for analysis and provide:
- Expert opinions
- Real-world examples
- Benefits and challenges
- What it means for people

Use simple language. 200-400 words max.
"""
        }
        
        return prompts.get(task.task_type, task.description)
    
    def _assess_quality(self, content: str) -> float:
        """Simplified quality assessment."""
        if not content:
            return 0.0
        
        score = 0.0
        word_count = len(content.split())
        
        if word_count > 100:
            score += 0.4
        if any(indicator in content.lower() for indicator in ["study", "research", "according to"]):
            score += 0.3
        if any(char.isdigit() for char in content):
            score += 0.3
        
        return min(score, 1.0)


class QuickAnalyzer:
    """Streamlined analysis engine with focus area integration."""
    
    MAX_CONTENT_LENGTH = 4000  # Reduced from 8000
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")
        
        self.llm = llm
        self.analysis_chain = self._create_analysis_chain()
        logger.info("Quick analyzer initialized")
    
    def _create_analysis_chain(self) -> LLMChain:
        """Create streamlined analysis chain."""
        prompt_template = PromptTemplate(
            input_variables=["research_content", "focus_areas"],
            template="""
Analyze this research and extract key points:

{research_content}

Focus areas: {focus_areas}

Provide in simple language:
1. Top 3 key points
2. Important numbers or facts
3. Main trends
4. What this means for people

Keep it brief and easy to understand.
"""
        )
        
        return LLMChain(llm=self.llm, prompt=prompt_template)
    
    def analyze(self, research_results: Dict[str, Any], focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze with focus area consideration."""
        if not research_results:
            raise ValueError("research_results cannot be empty")
        
        logger.info("Starting focused analysis")
        
        try:
            combined_content = self._combine_research_content(research_results)
            focus_text = ", ".join(focus_areas[:3]) if focus_areas else "General overview"
            
            analysis = self.analysis_chain.run({
                "research_content": combined_content,
                "focus_areas": focus_text
            })
            
            total_words = sum(
                result.get("word_count", 0)
                for result in research_results.values()
                if isinstance(result, dict)
            )
            
            return {
                "key_insights": analysis,
                "total_words": total_words,
                "focus_areas": focus_areas or [],
                "successful_tasks": len([
                    r for r in research_results.values()
                    if isinstance(r, dict) and r.get("status") == "completed"
                ])
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise ResearchError(f"Could not analyze research results: {str(e)}")
    
    def _combine_research_content(self, research_results: Dict[str, Any]) -> str:
        """Combine content with token optimization."""
        combined_content = ""
        
        for task_type, result in research_results.items():
            if isinstance(result, dict) and result.get("content"):
                content = result["content"][:1000]  # Limit each section
                combined_content += f"{task_type}: {content}\n\n"
        
        if len(combined_content) > self.MAX_CONTENT_LENGTH:
            combined_content = combined_content[:self.MAX_CONTENT_LENGTH] + "..."
        
        return combined_content


class BlogReportGenerator:
    """Focus-driven, user-friendly report generator."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        if not isinstance(llm, ChatGoogleGenerativeAI):
            raise TypeError("llm must be a ChatGoogleGenerativeAI instance")
        
        self.llm = llm
        self.report_chain = self._create_report_chain()
        logger.info("Blog report generator initialized")
    
    def _create_report_chain(self) -> LLMChain:
        """Create adaptive report template that responds to content and focus."""
        prompt_template = PromptTemplate(
            input_variables=["topic", "research_content", "analysis", "focus_areas"],
            template="""
            Write a friendly, easy-to-read article about: {topic}

            Research: {research_content}
            Key insights: {analysis}
            Focus areas: {focus_areas}

            Based on the research content and focus areas provided, intelligently organize the information into relevant sections. Let the content guide the structure - create section headings that naturally emerge from what you discovered in the research.

            Structure:
            # {topic}: What You Need to Know

            ## Introduction
            Brief, friendly intro explaining what this is about and why it matters.

            [Analyze the research content and focus areas, then create 3-4 meaningful sections with headings that reflect the actual findings. Each section should cover the most important aspects discovered in the research.]

            ## What This Means for You
            Practical takeaways and real-world impact.

            ## Looking Ahead
            Simple summary of future trends and what to expect.

            Guidelines:
            - Let the research content determine the section headings and organization
            - Use simple words instead of complex terms
            - Explain technical concepts in everyday language
            - Include specific facts and numbers when available
            - Keep paragraphs short and readable
            - Target 2000-2500 words total
            - Make it conversational and engaging
            - Focus on what's most relevant and interesting from your research
            """
        )
            
        return LLMChain(llm=self.llm, prompt=prompt_template)

    
    def generate_blog_report(
        self, 
        topic: str, 
        research_results: Dict[str, Any], 
        analysis: Dict[str, Any], 
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Generate focus-driven, user-friendly report."""
        if not topic or not topic.strip():
            raise ValueError("topic cannot be empty")
        if not research_results:
            raise ValueError("research_results cannot be empty")
        if not analysis:
            raise ValueError("analysis cannot be empty")
        
        logger.info(f"Generating focused report for: {topic}")
        
        try:
            research_summary = self._prepare_research_summary(research_results)
            focus_text = ", ".join(focus_areas[:4]) if focus_areas else "General overview"
            
            report = self.report_chain.run({
                "topic": topic.strip(),
                "research_content": research_summary,
                "analysis": analysis.get("key_insights", ""),
                "focus_areas": focus_text
            })
            
            logger.info(f"User-friendly report generated - {len(report.split())} words")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise ResearchError(f"Could not generate blog report: {str(e)}")
    
    def _prepare_research_summary(self, research_results: Dict[str, Any]) -> str:
        """Prepare concise research summary."""
        research_summary = ""
        max_content_per_task = 800  # Reduced from 2000
        
        for task_type, result in research_results.items():
            if isinstance(result, dict) and result.get("content"):
                content = result["content"]
                
                if len(content) > max_content_per_task:
                    content = content[:max_content_per_task] + "..."
                
                research_summary += f"{task_type.replace('_', ' ')}: {content}\n\n"
        
        return research_summary
