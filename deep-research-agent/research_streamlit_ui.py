import os
import streamlit as st
import time
from datetime import datetime
import re
import pandas as pd
from typing import Dict, Any

# Import your existing research system
from research_agentv2 import StreamlinedCoordinator, get_llm

# ================================================================
# STREAMLIT CONFIGURATION
# ================================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# PROFESSIONAL CSS STYLING
# ================================================================

st.markdown("""
<style>
   .main-header {
  text-align: center;
  color: #ffffff;
  font-size: 2.2rem;
  margin-bottom: 1.5rem;
  font-weight: 300;
  letter-spacing: -0.5px;
}

.subtitle {
  text-align: center;
  color: #c3c4c8;
  font-size: 1rem;
  margin-bottom: 2rem;
  font-weight: 400;
}

.section-header {
  color: #dee0e2;
  font-size: 1.2rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #bdc3c7;
  padding-bottom: 0.5rem;
  font-weight: 500;
}

.research-input-card {
  background: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  margin: 1.5rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8e8e8;
}

.research-input-header {
  color: #dae8f6;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

.task-progress {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  border-left: 3px solid #3498db;
}

.blog-content {
  background: #ffffff;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  line-height: 1.7;
  max-width: 100%;
  word-wrap: break-word;
  border: 1px solid #e8e8e8;
  margin: 2rem 0;
}

.blog-content h1 {
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.8rem;
  margin-top: 0;
  font-weight: 600;
  font-size: 2rem;
}

.blog-content h2 {
  color: #34495e;
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 500;
  font-size: 1.5rem;
}

.blog-content h3 {
  color: #5d6d7e;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
  font-size: 1.2rem;
}

.blog-content p {
  margin-bottom: 1.2rem;
  text-align: justify;
  color: #2c3e50;
  font-size: 1rem;
}

.blog-content ul,
.blog-content ol {
  margin-left: 2rem;
  margin-bottom: 1.2rem;
}

.blog-content li {
  margin-bottom: 0.6rem;
  color: #2c3e50;
}

.blog-content strong {
  color: #2c3e50;
  font-weight: 600;
}

/* Fixed button alignment CSS */
.stButton > button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s ease;
  height: 2.5rem !important;
  font-size: 0.9rem;
  margin-top: 0 !important;
  vertical-align: top !important;
}

.stButton > button:hover {
  background: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stTextInput > div > div > input {
  height: 2.5rem !important;
  border: 1px solid #bdc3c7;
  border-radius: 6px;
  font-size: 1rem;
}

/* Force column alignment */
div[data-testid="column"] {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

div[data-testid="column"]:has(.stButton) {
  padding-top: 1.7rem;
}

.sidebar-section {
  background: #ffffff;
  padding: 1.2rem;
  border-radius: 6px;
  margin: 1rem 0;
  border: 1px solid #e8e8e8;
}

.success-alert {
  background: #d5f4e6;
  color: #27ae60;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0;
  border-left: 3px solid #27ae60;
  font-weight: 500;
}

.example-topic-btn {
  background: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #bdc3c7;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.example-topic-btn:hover {
  background: #d5dbdb;
  border-color: #95a5a6;
}

</style>
""", unsafe_allow_html=True)

# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def format_blog_content(content: str) -> str:
    """Professional blog content formatter with enhanced markdown support"""
    if not content:
        return "<p>No content available.</p>"
    
    # Handle markdown formatting with improved regex patterns
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)  # Bold
    content = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', content)  # Italic
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)  # Inline code
    
    # Split content into lines
    lines = content.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('')
            continue
            
        # Headers with improved hierarchy
        if stripped_line.startswith('### '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h3>{stripped_line[4:].strip()}</h3>')
        elif stripped_line.startswith('## '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h2>{stripped_line[3:].strip()}</h2>')
        elif stripped_line.startswith('# '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h1>{stripped_line[2:].strip()}</h1>')
        # Numbered lists
        elif re.match(r'^\d+\.\s', stripped_line):
            if in_list and not formatted_lines[-1].startswith('<ol>'):
                formatted_lines.append('</ul>')
                formatted_lines.append('<ol>')
            elif not in_list:
                formatted_lines.append('<ol>')
                in_list = True
            formatted_lines.append(f'<li>{re.sub(r"^\d+\.\s", "", stripped_line)}</li>')
        # Bullet lists
        elif stripped_line.startswith(('* ', '- ', '• ')):
            if in_list and formatted_lines[-1].startswith('<ol>'):
                formatted_lines.append('</ol>')
                formatted_lines.append('<ul>')
            elif not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{stripped_line[2:].strip()}</li>')
        # Regular paragraphs
        else:
            if in_list:
                if formatted_lines[-1].startswith('<ol>'):
                    formatted_lines.append('</ol>')
                else:
                    formatted_lines.append('</ul>')
                in_list = False
            if stripped_line and not stripped_line.startswith('<'):
                formatted_lines.append(f'<p>{stripped_line}</p>')
            else:
                formatted_lines.append(stripped_line)
    
    # Close any open lists
    if in_list:
        if formatted_lines[-1].startswith('<ol>'):
            formatted_lines.append('</ol>')
        else:
            formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

# ================================================================
# UI COMPONENTS
# ================================================================

def render_header():
    """Render professional header"""
    st.markdown('<h1 class="main-header">AI Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Generate comprehensive research reports using advanced AI agents</p>', unsafe_allow_html=True)

def render_sidebar():
    """Render professional sidebar with dropdown sections"""
    st.sidebar.header("Research Configuration")
    
    # Research Settings
    with st.sidebar.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        
        research_depth = st.selectbox(
            "Research Depth",
            ["Standard", "Deep", "Quick"],
            index=0,
            help="Standard: Balanced speed and depth | Deep: Comprehensive analysis | Quick: Fast overview"
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
                "Industry Standards & Benchmarks"
            ],
            default=["Current Trends & Developments", "Expert Opinions & Insights", "Market Analysis & Statistics"],
            help="Select 3-5 areas for optimal results"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # System Information Dropdown
    with st.sidebar.expander("System Information", expanded=False):
        st.markdown(f"**Date:** {datetime.now().strftime('%B %d, %Y')}")
        st.markdown("**AI Model:** Gemini 2.0 Flash")
        st.markdown("**Search Engine:** Google (Serper API)")
        st.markdown("**Version:** 2.1.0")
    
    # Research Tips Dropdown
    with st.sidebar.expander("Research Tips", expanded=False):
        st.markdown("""
        **For Best Results:**
        - Be specific with your research topic
        - Include current company or product names
        - Use relevant industry keywords
        - Specify time periods if needed
        - Select 3-5 focus areas maximum
        
        **Topic Examples:**
        - "Electric vehicle market trends 2025"
        - "AI adoption in healthcare institutions"
        - "Sustainable packaging innovations"
        """)
    
    return research_depth, focus_areas

def render_research_input():
    """Render professional research input section with proper alignment"""
    st.markdown('<div class="research-input-card">', unsafe_allow_html=True)
    st.markdown('<div class="research-input-header">Research Topic</div>', unsafe_allow_html=True)
    
    # Use form for better control
    with st.form("research_form"):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            current_topic = st.session_state.get('research_topic', '')
            research_topic = st.text_input(
                "",
                value=current_topic,
                placeholder="Enter your research topic (e.g., 'AI in Healthcare 2025', 'Electric Vehicle Market Analysis')",
                key="topic_input_form",
                label_visibility="collapsed"
            )
        
        with col2:
            start_research = st.form_submit_button(
                "Start Research",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle form submission
    if start_research and research_topic:
        st.session_state.research_topic = research_topic
        st.session_state.topic_input = research_topic
    
    # Professional example topics
    st.markdown('<div class="section-header">Popular Research Topics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    example_topics = [
        "Artificial Intelligence in 2025",
        "Sustainable Energy Solutions", 
        "Remote Work Technologies",
        "Cryptocurrency Market Trends"
    ]
    
    for i, topic in enumerate(example_topics):
        with [col1, col2, col3, col4][i]:
            if st.button(topic, key=f"example_{i}", help=f"Research: {topic}"):
                st.session_state.research_topic = topic
                st.session_state.topic_input = topic
                st.rerun()
    
    final_topic = research_topic or st.session_state.get('research_topic', '')
    return final_topic, start_research


def render_research_progress(current_task: str, completed_tasks: int, total_tasks: int):
    """Render professional progress section"""
    st.markdown('<div class="section-header">Research Progress</div>', unsafe_allow_html=True)
    
    progress_percentage = completed_tasks / total_tasks if total_tasks > 0 else 0
    st.progress(progress_percentage)
    
    st.markdown(f"""
    <div class="task-progress">
        <strong>Current Task:</strong> {current_task}<br>
        <strong>Progress:</strong> {completed_tasks}/{total_tasks} tasks completed ({progress_percentage:.1%})
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completed", completed_tasks)
    with col2:
        st.metric("Total Tasks", total_tasks)
    with col3:
        st.metric("Progress", f"{progress_percentage:.1%}")

def render_blog_report(blog_content: str, research_topic: str):
    """Render professional research report"""
    st.markdown('<div class="section-header">Research Report</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="success-alert">
        Research completed successfully for: <strong>{research_topic}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if blog_content:
        formatted_content = format_blog_content(blog_content)
        st.markdown(f'<div class="blog-content">{formatted_content}</div>', unsafe_allow_html=True)
    else:
        st.error("No content generated. Please try again.")
    
    # Professional action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if blog_content:
            st.download_button(
                label="Download Report",
                data=blog_content,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("Copy Content", key="copy_btn"):
            st.info("Select and copy the text from the report above")
    
    with col3:
        if st.button("New Research", key="new_research_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ================================================================
# MAIN APPLICATION
# ================================================================

def main():
    """Main application with professional interface"""
    # Initialize session state
    if 'research_complete' not in st.session_state:
        st.session_state.research_complete = False
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    
    render_header()
    research_depth, focus_areas = render_sidebar()
    
    if not st.session_state.research_complete:
        research_topic, start_research = render_research_input()
        
        if start_research and research_topic:
            if not os.getenv("SERPER_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
                st.error("API keys not configured. Please add them to your .env file.")
                st.info("Required: SERPER_API_KEY and GOOGLE_API_KEY")
                return
            
            try:
                st.session_state.current_topic = research_topic
                st.session_state.focus_areas = focus_areas
                
                llm = get_llm()
                coordinator = StreamlinedCoordinator(llm)
                progress_placeholder = st.empty()
                
                start_time = time.time()
                
                with st.spinner("Initializing research..."):
                    tasks = coordinator.planner.create_research_plan(research_topic)
                    total_tasks = len(tasks)
                
                research_results = {}
                
                for i, task in enumerate(tasks):
                    with progress_placeholder.container():
                        render_research_progress(task.description, i, total_tasks)
                    
                    with st.spinner(f"Executing: {task.description}"):
                        result = coordinator.researcher.execute_task(task, focus_areas)
                        research_results[task.task_type.value] = result
                    
                    with progress_placeholder.container():
                        render_research_progress(f"Completed: {task.description}", i + 1, total_tasks)
                    
                    time.sleep(0.3)
                
                progress_placeholder.empty()
                
                with st.spinner("Analyzing research findings..."):
                    analysis = coordinator.analyzer.analyze(research_results)
                
                with st.spinner("Generating comprehensive report..."):
                    blog_content = coordinator.reporter.generate_blog_report(
                        research_topic, research_results, analysis
                    )
                    st.session_state.blog_content = blog_content
                
                st.session_state.research_complete = True
                end_time = time.time()
                st.success(f"Research completed in {end_time - start_time:.1f} seconds")
                
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error during research: {str(e)}")
                st.info("Try a simpler topic or check your API configuration")
    
    else:
        render_blog_report(st.session_state.blog_content, st.session_state.current_topic)

if __name__ == "__main__":
    main()
