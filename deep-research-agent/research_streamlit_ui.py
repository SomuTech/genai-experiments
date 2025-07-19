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
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# ENHANCED CSS FOR BETTER STYLING
# ================================================================

st.markdown("""
<style>
  .main-header {
  text-align: center;
  color: #1f77b4;
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
}

.research-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1.5rem;
  border-radius: 15px;
  color: white;
  margin: 1rem 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.task-progress {
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 8px;
  margin: 0.5rem 0;
  border-left: 4px solid #28a745;
}

.blog-content {
  background: rgb(255, 255, 255);
  color: black;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  line-height: 1.8;
  max-width: 100%;
  word-wrap: break-word;
}

.blog-content h1 {
  color: #2174c6;
  border-bottom: 3px solid #3498db;
  padding-bottom: 0.5rem;
  margin-top: 0;
}

.blog-content h2 {
  color: #223d58;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.blog-content h3 {
  color: #18222e;
  margin-top: 1.2rem;
  margin-bottom: 0.8rem;
}

.blog-content p {
  margin-bottom: 1rem;
  text-align: justify;
}

.blog-content ul,
.blog-content ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.blog-content li {
  margin-bottom: 0.5rem;
}

.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.6rem 1.5rem;
    border-radius: 25px;
    font-weight: bold;
    transition: all 0.3s ease;
    width: 100%;
    height: 2rem; /* Fixed height to match input */
    margin-top: 1.1rem; /* Adjust this value to align with input */
}

/* Fix for input field alignment */
.stTextInput > div > div > input {
    height: 2.5rem;
}

.stButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.sidebar-content {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 10px;
  margin: 1rem 0;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
  border-left: 4px solid #28a745;
}

</style>
""", unsafe_allow_html=True)

# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def format_blog_content(content: str) -> str:
    """Enhanced blog content formatter with comprehensive markdown support"""
    if not content:
        return "<p>No content available.</p>"
    
    # Handle markdown formatting
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)  # Bold
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)  # Italic
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)  # Inline code
    
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
            continue
            
        # Headers
        if stripped_line.startswith('### '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h3>{stripped_line[4:]}</h3>')
        elif stripped_line.startswith('## '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h2>{stripped_line[3:]}</h2>')
        elif stripped_line.startswith('# '):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h1>{stripped_line[2:]}</h1>')
        # List items
        elif stripped_line.startswith('* ') or stripped_line.startswith('- '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{stripped_line[2:]}</li>')
        # Regular paragraphs
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            if stripped_line and not stripped_line.startswith('<'):
                formatted_lines.append(f'<p>{stripped_line}</p>')
            else:
                formatted_lines.append(stripped_line)
    
    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)


# ================================================================
# STREAMLIT UI COMPONENTS
# ================================================================

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">🔍 AI Research Assistant</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; color: #7f8c8d;">
            Powered by Advanced AI Agents | Get comprehensive research reports in minutes
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with controls and information"""
    st.sidebar.markdown("## 🎛️ Research Controls")
    
    # Research settings
    st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.sidebar.markdown("### Research Settings")
    
    research_depth = st.sidebar.selectbox(
        "Research Depth",
        ["Standard", "Deep", "Quick"],
        index=0,
        help="Choose the depth of research"
    )
    
    # ENHANCED FOCUS AREAS
    focus_areas = st.sidebar.multiselect(
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
        help="Select specific areas to focus on during research"
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # System information
    st.sidebar.markdown("### 📊 System Information")
    st.sidebar.markdown(f"**Current Date:** {datetime.now().strftime('%B %d, %Y')}")
    st.sidebar.markdown("**AI Model:** Gemini 2.0 Flash")
    st.sidebar.markdown("**Search Engine:** Google (Serper)")
    
    # Research tips
    st.sidebar.markdown("### 💡 Research Tips")
    st.sidebar.markdown("""
    - Be specific with your topic
    - Use current company/product names
    - Include relevant keywords
    - Ask for comparisons when needed
    - Select 3-5 focus areas for best results
    """)
    
    return research_depth, focus_areas

def render_research_input():
    """Render the research input section with fixed button alignment"""
    st.markdown('<div class="research-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 What would you like to research?")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Get current value from session state if available
        current_topic = st.session_state.get('research_topic', '')
        research_topic = st.text_input(
            "",
            value=current_topic,
            placeholder="Enter your research topic (e.g., 'AI in Healthcare 2025', 'Electric Vehicle Market Trends')",
            key="topic_input",
            label_visibility="collapsed"  # Hide the empty label
        )
    
    with col2:
        # Add empty space to align button with input field
        st.markdown("<div style='height: 0rem;'></div>", unsafe_allow_html=True)
        start_research = st.button("🚀 Start Research", key="start_btn", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Example topics
    st.markdown("### 🔥 Popular Research Topics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    example_topics = [
        "Artificial Intelligence in 2025",
        "Sustainable Energy Solutions", 
        "Remote Work Technologies",
        "Cryptocurrency Trends"
    ]
    
    # Handle example topic clicks
    for i, topic in enumerate(example_topics):
        with [col1, col2, col3, col4][i]:
            if st.button(f"📌 {topic}", key=f"example_{i}"):
                st.session_state.research_topic = topic
                st.session_state.topic_input = topic
                st.rerun()
    
    # Use the input value or session state value
    final_topic = research_topic or st.session_state.get('research_topic', '')
    
    return final_topic, start_research


def render_research_progress(current_task: str, completed_tasks: int, total_tasks: int):
    """Render research progress section"""
    st.markdown('<div class="section-header">📊 Research Progress</div>', unsafe_allow_html=True)
    
    # Progress bar
    progress_percentage = completed_tasks / total_tasks if total_tasks > 0 else 0
    st.progress(progress_percentage)
    
    # Current task info
    st.markdown(f"""
    <div class="task-progress">
        <strong>Current Task:</strong> {current_task}<br>
        <strong>Progress:</strong> {completed_tasks}/{total_tasks} tasks completed ({progress_percentage:.1%})
    </div>
    """, unsafe_allow_html=True)
    
    # Progress metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tasks Completed", completed_tasks)
    
    with col2:
        st.metric("Total Tasks", total_tasks)
    
    with col3:
        st.metric("Progress", f"{progress_percentage:.1%}")

def render_blog_report(blog_content: str, research_topic: str):
    """Render the final blog report"""
    st.markdown('<div class="section-header">📝 Research Report</div>', unsafe_allow_html=True)
    
    # Success message
    st.markdown(f"""
    <div class="success-message">
        <strong>✅ Research Complete!</strong><br>
        Generated comprehensive report on: <strong>{research_topic}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Blog content with better formatting
    if blog_content:
        formatted_content = format_blog_content(blog_content)
        st.markdown(f'<div class="blog-content">{formatted_content}</div>', unsafe_allow_html=True)
    else:
        st.error("No content generated. Please try again.")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if blog_content:
            st.download_button(
                label="📥 Download Report",
                data=blog_content,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📋 Copy Content", key="copy_btn"):
            st.info("💡 Select and copy the text from the report above")
    
    with col3:
        if st.button("🔄 New Research", key="new_research_btn"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ================================================================
# MAIN APPLICATION
# ================================================================
def main():
    """Main Streamlit application"""
    # Initialize session state
    if 'research_complete' not in st.session_state:
        st.session_state.research_complete = False
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = ""
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    
    # Render header
    render_header()
    
    # Render sidebar
    research_depth, focus_areas = render_sidebar()
    
    # Main content area
    if not st.session_state.research_complete:
        # Research input section
        research_topic, start_research = render_research_input()
        
        # Handle research execution
        if start_research and research_topic:
            # Validate environment
            if not os.getenv("SERPER_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
                st.error("❌ API keys not configured. Please add them to your .env file.")
                st.info("💡 Make sure your .env file contains:\nSERPER_API_KEY=your_key\nGOOGLE_API_KEY=your_key")
                return
            
            # Initialize research system
            try:
                st.session_state.current_topic = research_topic
                st.session_state.focus_areas = focus_areas  # Store focus areas
                
                llm = get_llm()
                coordinator = StreamlinedCoordinator(llm)
                
                # Progress tracking
                progress_placeholder = st.empty()
                
                # Start research with progress updates
                start_time = time.time()
                
                # Create plan
                with st.spinner("🔍 Initializing research..."):
                    tasks = coordinator.planner.create_research_plan(research_topic)
                    total_tasks = len(tasks)
                
                # Execute tasks with progress updates
                research_results = {}
                
                for i, task in enumerate(tasks):
                    # Show progress
                    with progress_placeholder.container():
                        render_research_progress(
                            task.description,
                            i,
                            total_tasks
                        )
                    
                    # Execute task with focus areas
                    with st.spinner(f"🔍 Executing: {task.description}"):
                        result = coordinator.researcher.execute_task(task, focus_areas)  # Pass focus areas
                        research_results[task.task_type.value] = result
                    
                    # Update progress
                    with progress_placeholder.container():
                        render_research_progress(
                            f"Completed: {task.description}",
                            i + 1,
                            total_tasks
                        )
                    
                    time.sleep(0.3)  # Small delay for visual effect
                
                # Clear progress placeholder
                progress_placeholder.empty()
                
                # Analysis phase
                with st.spinner("🧮 Analyzing research findings..."):
                    analysis = coordinator.analyzer.analyze(research_results)
                
                # Report generation
                with st.spinner("📝 Generating comprehensive report..."):
                    blog_content = coordinator.reporter.generate_blog_report(
                        research_topic,
                        research_results,
                        analysis
                    )
                    st.session_state.blog_content = blog_content
                
                # Mark research as complete
                st.session_state.research_complete = True
                
                end_time = time.time()
                st.success(f"✅ Research completed in {end_time - start_time:.1f} seconds!")
                
                # Auto-refresh to show results
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during research: {str(e)}")
                st.info("💡 Try a simpler topic or check your API configuration")
    
    else:
        # Display blog report (no progress bar or internal metrics)
        render_blog_report(st.session_state.blog_content, st.session_state.current_topic)

if __name__ == "__main__":
    main()
