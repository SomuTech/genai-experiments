"""
AI Research Assistant - Streamlit Web Interface

A modern web interface for the AI Research Assistant that provides
an intuitive way to conduct comprehensive research and generate reports.

Author: SomuTech
Date: July 2025
License: MIT
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple, List
import re
import markdown

import streamlit as st

# Import the research system
from config import (
    load_environment_variables,
    get_llm,
    ConfigurationError,
    ResearchError,
)
from main import StreamlinedCoordinator

# ================================================================
# STREAMLIT CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# PROFESSIONAL CSS STYLING
# ================================================================

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .main-header {
        text-align: center;
        color: #ffffff !important;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        text-align: center;
        color: #a0aec0 !important;
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    .section-header {
        color: #e2e8f0 !important;
        font-size: 1.3rem;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    .research-input-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        padding: 2.0rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .research-input-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .research-input-header {
        color: #ffffff !important;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
        height: 50px !important;
        min-width: 140px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    .stTextInput > div > div > input {
        height: 40px !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
        padding: 0 1.5rem !important;
        transition: all 0.3s ease !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0aec0 !important;
        opacity: 0.7;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    .stForm {
        background: transparent !important;
        border: none !important;
    }
    
    div[data-testid="column"]:has(.stButton) {
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Topic links styling */
    .topic-link {
        color: #667eea !important;
        text-decoration: none !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        display: block !important;
        cursor: pointer !important;
    }
    
    .topic-link:hover {
        color: #ffffff !important;
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        transform: translateX(4px) !important;
        text-decoration: none !important;
    }
    
    .sidebar-section {
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .task-progress-minimal {
        margin: 2rem 0;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    .progress-text {
        color: #e2e8f0 !important;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .stProgress > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    .blog-content {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e2e8f0 !important;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        line-height: 1.8;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin: 2rem 0 3rem 0;
    }
    
    .blog-content h1 {
        color: #ffffff !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 1rem;
        margin-bottom: 2rem;
        font-weight: 700;
        font-size: 2.25rem;
    }
    
    .blog-content h2 {
        color: #f7fafc !important;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        font-weight: 600;
        font-size: 1.6rem;
    }
    
    .blog-content h3 {
        color: #e2e8f0 !important;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: 600;
        font-size: 1.3rem;
    }
    
    .blog-content p {
        color: #cbd5e0 !important;
        margin-bottom: 1.5rem;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    
    .blog-content li {
        color: #cbd5e0 !important;
        margin-bottom: 0.75rem;
        line-height: 1.6;
    }
    
    .blog-content strong {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .success-alert {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%) !important;
        color: white !important;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        box-shadow: 0 4px 20px rgba(72, 187, 120, 0.3);
    }
    
    /* Action buttons container */
    .action-buttons {
        margin-top: 2.5rem !important;
        padding-top: 2rem !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4) !important;
        height: 50px !important;
        min-width: 140px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stMultiSelect [data-baseweb="tag"]:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    
    .stMarkdown, .stText {
        color: #e2e8f0 !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Updated topic links styling for vertical list */
.stButton[data-testid="baseButton-secondary"] > button {
    background: transparent !important;
    color: #667eea !important;
    border: none !important;
    padding: 1rem 0 !important;
    border-radius: 0 !important;
    font-weight: 400 !important;
    font-size: 1rem !important;
    text-align: left !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    line-height: 1.5 !important;
    transition: all 0.2s ease !important;
    border-bottom: 1px solid rgba(102, 126, 234, 0.1) !important;
    box-shadow: none !important;
    transform: none !important;
}

.stButton[data-testid="baseButton-secondary"] > button:hover {
    color: #ffffff !important;
    background: rgba(102, 126, 234, 0.1) !important;
    border-bottom-color: rgba(102, 126, 234, 0.3) !important;
    transform: none !important;
    box-shadow: none !important;
    padding-left: 1rem !important;
}

/* Hide the secondary button styling for topic links */
div[data-testid="baseButton-secondary"] {
    width: 100% !important;
    margin-bottom: 0.5rem !important;
}


</style>
""",
    unsafe_allow_html=True,
)

# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def format_blog_content(content: str) -> str:
    """
    Convert markdown content to HTML using the markdown library.
    
    Args:
        content: Raw markdown content string
        
    Returns:
        Formatted HTML content string
    """
    if not content:
        return "<p>No content available.</p>"
    
    # Configure markdown with extensions for better formatting
    md = markdown.Markdown(
        extensions=[
            'extra',          # Tables, fenced code blocks, etc.
            'codehilite',     # Syntax highlighting
            'toc',            # Table of contents
            'nl2br',          # Convert newlines to <br>
            'sane_lists'      # Better list handling
        ]
    )
    
    # Convert markdown to HTML
    html_content = md.convert(content)
    
    return html_content

# ================================================================
# UI COMPONENTS
# ================================================================

def render_header() -> None:
    """Render the application header."""
    st.markdown(
        '<h1 class="main-header">AI Research Assistant</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="subtitle">Generate comprehensive research reports using advanced AI agents</p>',
        unsafe_allow_html=True,
    )

def render_sidebar() -> Tuple[str, List[str]]:
    """
    Render the sidebar with research configuration options.

    Returns:
        Tuple containing research depth and focus areas
    """
    st.sidebar.header("Research Configuration")

    # Research Settings
    with st.sidebar.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)

        research_depth = st.selectbox(
            "Research Depth",
            ["Standard", "Deep", "Quick"],
            index=0,
            help="Standard: Balanced speed and depth | Deep: Comprehensive analysis | Quick: Fast overview",
        )

        focus_areas = st.multiselect(
            "Focus Areas",
            [
                "Current Trends & Developments",
                "Market Analysis & Statistics",
                "Expert Opinions & Insights",
                "Historical Context & Background",
                "Case Studies & Examples",
                "Technology & Innovation",
                "Financial & Business Impact",
                "Future Predictions & Outlook",
                "Competitive Landscape",
                "Regulatory & Legal Aspects",
                "Global Perspective & Regional Differences",
                "Challenges & Opportunities",
                "Best Practices & Guidelines",
                "Industry Standards & Benchmarks",
            ],
            default=[
                "Current Trends & Developments",
                "Expert Opinions & Insights",
                "Market Analysis & Statistics",
            ],
            help="Select 3-5 areas for optimal results",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # System Information Dropdown
    with st.sidebar.expander("System Information", expanded=False):
        st.markdown(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        st.markdown("**AI Model:** Gemini 2.5 Flash Lite")
        st.markdown("**Search Engine:** Google (Serper API)")
        st.markdown("**Version:** 2.1.0")

    # Research Tips Dropdown
    with st.sidebar.expander("Research Tips", expanded=False):
        st.markdown(
            """
        **For Best Results:**
        - Be specific with your research topic
        - Use relevant industry keywords
        - Specify time periods if needed
        - Select 3-5 focus areas maximum
        
        **Topic Examples:**
        - "Electric vehicle market trends 2025"
        - "AI adoption in healthcare institutions"
        - "Sustainable packaging innovations"
        """
        )

    return research_depth, focus_areas

def render_research_input() -> Tuple[str, bool]:
    """Render the research input form."""
    st.markdown('<div class="research-input-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="research-input-header">Research Topic</div>',
        unsafe_allow_html=True,
    )

    # Disable form if research is in progress
    with st.form("research_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])

        with col1:
            current_topic = st.session_state.get("research_topic", "")
            research_topic = st.text_input(
                "",
                value=current_topic,
                placeholder="Enter your research topic..." if not st.session_state.get("research_in_progress", False) else "Research in progress...",
                key="topic_input_form",
                label_visibility="collapsed",
                disabled=st.session_state.get("research_in_progress", False)  # Disable during research
            )

        with col2:
            start_research = st.form_submit_button(
                "Research", 
                use_container_width=True,
                disabled=st.session_state.get("research_in_progress", False)  # Disable during research
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # Handle form submission only if not already researching
    if start_research and research_topic and not st.session_state.get("research_in_progress", False):
        st.session_state.research_topic = research_topic
        st.session_state.topic_input = research_topic

    final_topic = research_topic or st.session_state.get("research_topic", "")
    return final_topic, start_research

def render_popular_topics() -> None:
    """Render popular research topics as clickable text links listed vertically."""
    # Hide topics if research has started OR is in progress OR is complete
    if (not st.session_state.get("research_in_progress", False) and 
        not st.session_state.get("research_complete", False)):
        st.markdown(
            '<div class="section-header">Popular Research Topics</div>',
            unsafe_allow_html=True,
        )

        example_topics = [
            "Artificial Intelligence Applications in Healthcare Diagnosis and Treatment Systems for 2025",
            "Sustainable Energy Solutions and Renewable Technology Adoption in Developing Countries",
            "Cryptocurrency Market Analysis and Blockchain Technology Integration in Financial Systems",
            "Climate Change Mitigation Strategies and Environmental Policy Implementation Worldwide",
            "Quantum Computing Advancements and Their Applications in Scientific Research",
            "Cybersecurity Threats and Data Protection Measures in Digital Transformation Era",
        ]

        for i, topic in enumerate(example_topics):
            if st.button(topic, key=f"topic_link_{i}", help=f"Click to research: {topic}"):
                st.session_state.research_topic = topic
                st.session_state.topic_input = topic
                st.rerun()


def render_research_progress_minimal(completed_tasks: int, total_tasks: int) -> None:
    """
    Render minimal progress indicator.

    Args:
        completed_tasks: Number of completed tasks
        total_tasks: Total number of tasks
    """
    progress_percentage = completed_tasks / total_tasks if total_tasks > 0 else 0

    st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="progress-text">Research in progress... {progress_percentage:.0%} complete</div>',
        unsafe_allow_html=True,
    )
    st.progress(progress_percentage)
    st.markdown("</div>", unsafe_allow_html=True)

def render_blog_report(blog_content: str, research_topic: str) -> None:
    """
    Render the final research report.

    Args:
        blog_content: Generated blog content
        research_topic: Original research topic
    """
    st.markdown(
        '<div class="section-header">Research Report</div>', unsafe_allow_html=True
    )

    st.markdown(
        f"""
    <div class="success-alert">
        Research completed successfully for: <strong>{research_topic}</strong>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if blog_content:
        formatted_content = format_blog_content(blog_content)
        st.markdown(
            f'<div class="blog-content">{formatted_content}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.error("No content generated. Please try again.")

    # Action buttons with proper spacing and styling
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        if blog_content:
            st.download_button(
                label="Download Report",
                data=blog_content,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )

    with col2:
        if st.button("Copy Content", key="copy_btn"):
            st.info("Select and copy the text from the report above")

    with col3:
        if st.button("New Research", key="new_research_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# MAIN APPLICATION
# ================================================================

def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "research_complete" not in st.session_state:
        st.session_state.research_complete = False
    if "research_in_progress" not in st.session_state:
        st.session_state.research_in_progress = False
    if "blog_content" not in st.session_state:
        st.session_state.blog_content = ""
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = ""


def validate_environment() -> bool:
    """
    Load and validate that required environment variables are set.

    Returns:
        True if environment is valid, False otherwise
    """
    try:
        # Load environment variables first
        load_environment_variables()
        return True
    except ConfigurationError as e:
        st.error(f"Configuration error: {str(e)}")
        st.info("Required: SERPER_API_KEY and GOOGLE_API_KEY in your .env file")
        return False

def execute_research_workflow(research_topic: str, focus_areas: List[str]) -> bool:
    """
    Execute the main research workflow with continuous progress tracking.

    Args:
        research_topic: Topic to research
        focus_areas: Areas to focus the research on

    Returns:
        True if research completed successfully, False otherwise
    """
    try:
        # Set research in progress flag
        st.session_state.research_in_progress = True
        st.session_state.current_topic = research_topic
        st.session_state.focus_areas = focus_areas

        # Environment already loaded in validate_environment()
        llm = get_llm()
        coordinator = StreamlinedCoordinator(llm)
        progress_placeholder = st.empty()

        start_time = time.time()

        # Phase 1: Initialize research (0-10%)
        with progress_placeholder.container():
            st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
            st.markdown('<div class="progress-text">Initializing research... 0% complete</div>', unsafe_allow_html=True)
            st.progress(0.0)
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Initializing research..."):
            tasks = coordinator.planner.create_research_plan(research_topic)
            total_tasks = len(tasks)

        # Phase 2: Execute research tasks (10-70%)
        research_results = {}
        base_progress = 0.1  # 10% for initialization
        research_progress_range = 0.6  # 60% for research tasks
        
        for i, task in enumerate(tasks):
            # Calculate progress within research phase
            task_progress = base_progress + (i / total_tasks) * research_progress_range
            
            with progress_placeholder.container():
                st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
                st.markdown(f'<div class="progress-text">Executing research tasks... {task_progress:.0%} complete</div>', unsafe_allow_html=True)
                st.progress(task_progress)
                st.markdown('</div>', unsafe_allow_html=True)

            with st.spinner(f"Executing: {task.description}"):
                result = coordinator.researcher.execute_task(task, focus_areas)
                research_results[task.task_type.value] = result

            time.sleep(0.2)

        # Phase 3: Analysis (70-85%)
        with progress_placeholder.container():
            st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
            st.markdown('<div class="progress-text">Analyzing research findings... 70% complete</div>', unsafe_allow_html=True)
            st.progress(0.7)
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Analyzing research findings..."):
            analysis = coordinator.analyzer.analyze(research_results)

        # Phase 4: Report generation (85-100%)
        with progress_placeholder.container():
            st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
            st.markdown('<div class="progress-text">Generating comprehensive report... 85% complete</div>', unsafe_allow_html=True)
            st.progress(0.85)
            st.markdown('</div>', unsafe_allow_html=True)

        with st.spinner("Generating comprehensive report..."):
            blog_content = coordinator.reporter.generate_blog_report(
                research_topic, research_results, analysis
            )
            st.session_state.blog_content = blog_content

        # Final completion (100%)
        with progress_placeholder.container():
            st.markdown('<div class="task-progress-minimal">', unsafe_allow_html=True)
            st.markdown('<div class="progress-text">Research completed! 100% complete</div>', unsafe_allow_html=True)
            st.progress(1.0)
            st.markdown('</div>', unsafe_allow_html=True)

        time.sleep(1)
        progress_placeholder.empty()

        # Clear research in progress flag and set completion
        st.session_state.research_in_progress = False
        st.session_state.research_complete = True
        
        end_time = time.time()
        st.success(f"Research completed in {end_time - start_time:.1f} seconds")

        time.sleep(1)
        st.rerun()

        return True

    except (ConfigurationError, ResearchError) as e:
        st.session_state.research_in_progress = False
        st.error(f"Error during research: {str(e)}")
        st.info("Try a simpler topic or check your API configuration")
        return False
    except Exception as e:
        st.session_state.research_in_progress = False
        st.error(f"Unexpected error: {str(e)}")
        st.info("Please check your configuration and try again")
        return False

def main() -> None:
    """Main application entry point."""
    initialize_session_state()
    render_header()
    research_depth, focus_areas = render_sidebar()

    if not st.session_state.research_complete:
        research_topic, start_research = render_research_input()
        
        # Only show popular topics if research hasn't started
        render_popular_topics()

        if start_research and research_topic:
            if validate_environment():
                execute_research_workflow(research_topic, focus_areas)
    else:
        render_blog_report(
            st.session_state.blog_content, st.session_state.current_topic
        )

if __name__ == "__main__":
    main()
