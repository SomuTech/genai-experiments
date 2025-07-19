import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Core LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManagerForToolRun

# Tool imports
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import Tool, BaseTool
from langchain_community.document_loaders import WebBaseLoader

# Load environment variables
load_dotenv()
os.environ["USER_AGENT"] = "Streamlined Research Agent"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# ================================================================
# SIMPLIFIED CORE COMPONENTS
# ================================================================

class TaskType(Enum):
    OVERVIEW_RESEARCH = "overview_research"
    DETAILED_ANALYSIS = "detailed_analysis"
    CURRENT_TRENDS = "current_trends"
    BLOG_SYNTHESIS = "blog_synthesis"

@dataclass
class ResearchTask:
    task_type: TaskType
    description: str
    max_tokens: int
    results: Dict[str, Any] = None

class CompactMemory:
    """Lightweight memory system"""
    def __init__(self):
        self.successful_queries = []
        self.source_quality = {}
    
    def remember_success(self, query_type: str, approach: str):
        self.successful_queries.append({
            "type": query_type,
            "approach": approach,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 20 entries
        if len(self.successful_queries) > 20:
            self.successful_queries = self.successful_queries[-20:]

# ================================================================
# STREAMLINED AGENTS
# ================================================================

class SmartPlanner:
    """Intelligent task planner - creates exactly 3-4 focused tasks"""
    
    def __init__(self, llm):
        self.llm = llm
        self.memory = CompactMemory()
    
    def create_research_plan(self, topic: str) -> List[ResearchTask]:
        """Create 3-4 strategic research tasks with date awareness"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        current_year = datetime.now().year
        
        tasks = [
            ResearchTask(
                task_type=TaskType.OVERVIEW_RESEARCH,
                description=f"Research fundamental concepts and latest {current_year} developments about {topic}",
                max_tokens=1000
            ),
            ResearchTask(
                task_type=TaskType.CURRENT_TRENDS,
                description=f"Find {current_year} trends, recent news, and latest statistics about {topic}",
                max_tokens=800
            ),
            ResearchTask(
                task_type=TaskType.DETAILED_ANALYSIS,
                description=f"Gather {current_year} expert insights and current analysis of {topic}",
                max_tokens=800
            )
        ]
        
        print(f"📋 Created {len(tasks)} focused research tasks for {current_date}")
        return tasks

class EfficientResearcher:
    """Token-optimized research agent"""
    
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5,  # Reduced from 20
            handle_parsing_errors=True
        )
    
    def execute_task(self, task: ResearchTask, focus_areas: list = None) -> Dict[str, Any]:
        """Execute research task with focus areas and token limits"""
        
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
        
        # Task-specific prompts with focus areas integration
        task_prompts = {
            TaskType.OVERVIEW_RESEARCH: f"""
            Research the fundamentals of: {task.description}
            
            TODAY'S DATE: {current_date}. Prioritize {current_year} information.
            {focus_context}
            
            Focus on:
            - Core definitions and concepts (latest understanding)
            - Recent background and developments
            - Current key facts and statistics
            - Latest categories or types
            
            Search for: "{task.description.split()[-1]} {current_year}" AND "{task.description.split()[-1]} latest news"
            
            Provide comprehensive but concise information. Target 800-1000 words of valuable content.
            """,
            
            TaskType.CURRENT_TRENDS: f"""
            Research LATEST trends and developments: {task.description}
            
            CRITICAL: Today is {current_date}. Focus ONLY on {current_year} and late 2024 information.
            {focus_context}
            
            Search specifically for:
            - "{task.description.split()[-1]} {current_year} news"
            - "{task.description.split()[-1]} latest developments {current_year}"
            - "{task.description.split()[-1]} recent trends {current_year}"
            
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
            
            Search for:
            - "{task.description.split()[-1]} expert analysis {current_year}"
            - "{task.description.split()[-1]} predictions {current_year}"
            - "{task.description.split()[-1]} outlook {current_year}"
            
            Focus on:
            - {current_year} expert opinions and analysis
            - Latest practical applications
            - Most recent future predictions
            - Current challenges and opportunities
            
            Provide analytical depth. Target 600-800 words.
            """
        }
        
        try:
            prompt = task_prompts.get(task.task_type, task.description)
            results = self.agent.run(prompt)
            
            return {
                "status": "completed",
                "content": results,
                "word_count": len(results.split()),
                "quality_score": self._assess_quality(results)
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "content": "",
                "word_count": 0,
                "quality_score": 0.0
            }


    def _assess_quality(self, content: str) -> float:
        """Quick quality assessment"""
        score = 0.0
        
        # Length check
        word_count = len(content.split())
        if word_count > 300:
            score += 0.3
        
        # Source indicators
        if any(indicator in content.lower() for indicator in ["according to", "study", "research", "report"]):
            score += 0.3
        
        # Specific information
        if any(char.isdigit() for char in content):
            score += 0.2
        
        # Structure indicators
        if content.count('\n') > 3:
            score += 0.2
        
        return min(score, 1.0)

class QuickAnalyzer:
    """Fast analysis for blog synthesis"""
    
    def __init__(self, llm):
        self.llm = llm
        self.analysis_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
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
                """
            )
        )
    
    def analyze(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Quick analysis of research results"""
        
        # Combine all research content
        combined_content = ""
        for task_result in research_results.values():
            if task_result.get("content"):
                combined_content += task_result["content"] + "\n\n"
        
        # Truncate if too long (token management)
        if len(combined_content) > 8000:
            combined_content = combined_content[:8000] + "..."
        
        analysis = self.analysis_chain.run({"research_content": combined_content})
        
        return {
            "key_insights": analysis,
            "total_words": sum(result.get("word_count", 0) for result in research_results.values()),
            "average_quality": sum(result.get("quality_score", 0) for result in research_results.values()) / len(research_results)
        }

class BlogReportGenerator:
    """Generates blog-ready reports"""
    
    def __init__(self, llm):
        self.llm = llm
        self.report_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
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
                """
            )
        )
    
    def generate_blog_report(self, topic: str, research_results: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate comprehensive blog post"""
        
        # Prepare research content summary
        research_summary = ""
        for task_type, result in research_results.items():
            if result.get("content"):
                research_summary += f"**{task_type}:**\n{result['content'][:1500]}...\n\n"
        
        report = self.report_chain.run({
            "topic": topic,
            "research_content": research_summary,
            "analysis": analysis.get("key_insights", "")
        })
        
        return report

# ================================================================
# STREAMLINED COORDINATOR
# ================================================================

class StreamlinedCoordinator:
    """Efficient research coordinator"""
    
    def __init__(self, llm):
        self.llm = llm
        self.tools = self._initialize_tools()
        self.planner = SmartPlanner(llm)
        self.researcher = EfficientResearcher(llm, self.tools)
        self.analyzer = QuickAnalyzer(llm)
        self.reporter = BlogReportGenerator(llm)
    
    def _initialize_tools(self):
        """Initialize essential tools only"""
        serper_search = GoogleSerperAPIWrapper()
        
        class WebsiteSearchTool(BaseTool):
            name: str = "website_search"
            description: str = "Extract content from websites. Input should be a URL."
            
            def _run(self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
                try:
                    loader = WebBaseLoader(url)
                    documents = loader.load()
                    content = documents[0].page_content if documents else ""
                    # Limit content to prevent token overflow
                    return content[:2000] + "..." if len(content) > 2000 else content
                except Exception as e:
                    return f"Error accessing {url}: {str(e)}"
        
        return [
            Tool(
                name="Google Search",
                func=serper_search.run,
                description="Search Google for current information and comprehensive results."
            ),
            WebsiteSearchTool()
        ]
    
    def conduct_research(self, topic: str) -> str:
        """Main research orchestration - streamlined"""
        
        print(f"🚀 Starting streamlined research on: {topic}")
        
        # Step 1: Create focused plan (3-4 tasks max)
        print("📋 Creating focused research plan...")
        tasks = self.planner.create_research_plan(topic)
        
        # Step 2: Execute tasks efficiently
        print("🔍 Executing research tasks...")
        research_results = {}
        
        for i, task in enumerate(tasks, 1):
            print(f"📝 Task {i}/{len(tasks)}: {task.task_type.value}")
            result = self.researcher.execute_task(task)
            research_results[task.task_type.value] = result
            
            print(f"✅ Completed - {result['word_count']} words, Quality: {result['quality_score']:.2f}")
        
        # Step 3: Quick analysis
        print("🧮 Analyzing research findings...")
        analysis = self.analyzer.analyze(research_results)
        
        # Step 4: Generate blog report
        print("📊 Generating comprehensive blog report...")
        final_report = self.reporter.generate_blog_report(topic, research_results, analysis)
        
        return final_report

# ================================================================
# MAIN EXECUTION
# ================================================================

def get_llm():
    """Initialize Gemini with current date context"""
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite-preview-06-17",
        temperature=0.3,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_output_tokens=8000,
        verbose=False,
        # Add system message with current date
        model_kwargs={
            "system_instruction": f"Current date: {current_date}. Always prioritize the most recent information from 2025 when available."
        }
    )


def main():
    """Main execution - streamlined"""
    print("🤖 Streamlined Agentic Research System")
    print("=" * 50)
    
    # Validate environment
    if not os.getenv("SERPER_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: Missing API keys in environment variables")
        return
    
    # Get topic from user
    topic = input("\n🎯 Enter your research topic: ").strip()
    
    if not topic:
        print("❌ Please provide a valid topic")
        return
    
    try:
        # Initialize coordinator
        llm = get_llm()
        coordinator = StreamlinedCoordinator(llm)
        
        # Conduct research
        start_time = datetime.now()
        blog_report = coordinator.conduct_research(topic)
        end_time = datetime.now()
        
        # Display results
        print("\n" + "=" * 60)
        print("📝 BLOG-READY RESEARCH REPORT")
        print("=" * 60)
        print(blog_report)
        
        print(f"\n⏱️ Research completed in: {end_time - start_time}")
        print(f"📊 Estimated word count: {len(blog_report.split())} words")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("💡 Try a simpler topic or check your API keys")

if __name__ == "__main__":
    main()
