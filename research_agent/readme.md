# AI Research Assistant

A sophisticated multi-agent research system that leverages Google's Gemini AI and Serper search API to conduct comprehensive research, analysis, and generate detailed blog-ready reports.

## Overview

The AI Research Assistant is a professional-grade research automation tool that combines multiple AI agents to perform complex research tasks. The system uses advanced prompt engineering, intelligent task planning, and comprehensive analysis to produce high-quality research reports on any given topic.

## Architecture

The system employs a multi-agent architecture with specialized components:

- **Smart Planner**: Creates strategic research plans with optimized task sequences
- **Efficient Researcher**: Executes research tasks using web search and content extraction
- **Quick Analyzer**: Synthesizes research findings into actionable insights
- **Blog Report Generator**: Creates comprehensive, well-structured reports
- **Streamlined Coordinator**: Orchestrates the entire research pipeline

## Technology Stack

### Core Dependencies

- **Python 3.8+**: Primary programming language
- **LangChain**: AI agent framework and orchestration
- **Google Gemini 2.5**: Large language model for reasoning and content generation
- **Serper API**: Google search integration for current information retrieval
- **Streamlit**: Web interface for user interaction

### Supporting Libraries

- **BeautifulSoup4**: Web content extraction and parsing
- **Pydantic**: Data validation and serialization
- **Python-dotenv**: Environment variable management
- **Logging**: Comprehensive system monitoring and debugging

## Features

### Research Capabilities

- Intelligent topic analysis and research planning
- Multi-source information gathering from web search and websites
- Current trend analysis with 2025-focused content prioritization
- Expert opinion aggregation and synthesis
- Quality assessment and content scoring

### Analysis Features

- Automated insight extraction from research data
- Pattern recognition and trend identification
- Source credibility evaluation
- Statistical analysis and fact verification

### Report Generation

- Professional blog-format reports (1500-2000 words)
- Structured content with clear sections and hierarchy
- Citation integration and source attribution
- Customizable focus areas for targeted research

### User Interface

- Modern web interface built with Streamlit
- Real-time progress tracking during research
- Interactive configuration options
- Professional dark theme design
- Download and sharing capabilities

## Installation

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini access
- Serper API key for search functionality

### Setup Instructions

1. **Clone the Repository**

```

git clone <repository-url>
cd research_agent

```

2. **Create Virtual Environment**

```

python -m venv .venv

```

3. **Activate Virtual Environment**

Windows:

```

.venv\Scripts\activate

```

macOS/Linux:

```

source .venv/bin/activate

```

4. **Install Dependencies**

```

pip install -r requirements.txt

```

5. **Environment Configuration**

Create a `.env` file in the project root:

```

SERPER_API_KEY=your_serper_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

```

### API Key Setup

#### Google API Key (Gemini)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini access
3. Copy the key to your `.env` file

#### Serper API Key

1. Sign up at [Serper.dev](https://serper.dev)
2. Access your dashboard to find the API key
3. Copy the key to your `.env` file
4. Free tier includes 2,500 searches per month

## Usage

### Command Line Interface

Run the research system directly from the command line:

```

python research_agent/main.py

```

Follow the prompts to enter your research topic and view results in the terminal.

### Web Interface

Launch the Streamlit web application:

```

streamlit run research_streamlit_app.py

```

Access the interface at `http://localhost:8501` in your web browser.

### Programmatic Usage

Import and use the research system in your own Python code:

```

from research_agent.config import load_environment_variables, get_llm
from research_agent.main import StreamlinedCoordinator

# Initialize the system

load_environment_variables()
llm = get_llm()
coordinator = StreamlinedCoordinator(llm)

# Conduct research

topic = "Artificial Intelligence in Healthcare 2025"
focus_areas = ["Current Trends", "Expert Opinions", "Market Analysis"]
report = coordinator.conduct_research(topic, focus_areas)

print(report)

```

## Project Structure

```

research_agent/
├── config.py              \# Configuration and environment management
├── models.py              \# Data models and memory systems
├── agents.py              \# AI agent implementations
├── main.py               \# Main coordination and CLI interface
├── __init__.py           \# Package initialization
├── requirements.txt      \# Python dependencies
├── research_streamlit_app.py     \# Web interface
├── .env                 \# Environment variables (create this)
└── README.md           \# Project documentation

```

## Configuration Options

### Research Parameters

- **Temperature**: Controls creativity in AI responses (0.0-1.0)
- **Max Tokens**: Maximum response length from AI model
- **Focus Areas**: Specific aspects to emphasize during research
- **Research Depth**: Standard, Deep, or Quick research modes

### Focus Areas Available

- Current Trends & Developments
- Market Analysis & Statistics
- Expert Opinions & Insights
- Historical Context & Background
- Case Studies & Examples
- Technology & Innovation
- Financial & Business Impact
- Future Predictions & Outlook
- Competitive Landscape
- Regulatory & Legal Aspects
- Global Perspective & Regional Differences
- Challenges & Opportunities
- Best Practices & Guidelines
- Industry Standards & Benchmarks

## How It Works

### Research Process Flow

1. **Topic Analysis**: The Smart Planner analyzes the research topic and creates an optimized research strategy
2. **Task Generation**: Three specialized research tasks are created focusing on overview, current trends, and detailed analysis
3. **Information Gathering**: The Efficient Researcher executes tasks using Google search and website content extraction
4. **Quality Assessment**: Each research result is evaluated for quality, relevance, and credibility
5. **Synthesis**: The Quick Analyzer combines and analyzes all research findings to extract key insights
6. **Report Generation**: The Blog Report Generator creates a comprehensive, well-structured report

### AI Agent Coordination

The system uses a coordinator pattern where the StreamlinedCoordinator manages the interaction between specialized agents:

- Agents operate independently with their own specialized prompts and logic
- Results are passed between agents through structured data formats
- Error handling and retry logic ensure robust operation
- Progress tracking provides real-time feedback to users

### Data Flow

```

User Input → Smart Planner → Research Tasks → Efficient Researcher →
Web Search Results → Content Analysis → Quick Analyzer →
Insights Generation → Blog Report Generator → Final Report

```

## Performance Characteristics

### Typical Execution Times

- Research Planning: 2-5 seconds
- Information Gathering: 30-90 seconds (varies by topic complexity)
- Analysis: 10-20 seconds
- Report Generation: 15-30 seconds
- Total Time: 1-3 minutes for comprehensive research

### Quality Metrics

- Research quality scoring based on source credibility and content depth
- Word count tracking for comprehensive coverage
- Execution time monitoring for performance optimization
- Success rate tracking for reliability assessment

## Error Handling

The system includes comprehensive error handling for common scenarios:

- **API Rate Limits**: Automatic retry logic with exponential backoff
- **Network Issues**: Graceful degradation and error reporting
- **Invalid Inputs**: Input validation and user-friendly error messages
- **Missing Configuration**: Clear guidance for setup requirements

## Logging and Monitoring

Comprehensive logging system provides:

- Execution progress tracking
- Performance metrics collection
- Error diagnosis and debugging information
- Research quality assessment data

Log files are stored as `research_agent.log` in the project directory.

## Limitations

### Current Constraints

- Research limited to publicly available web content
- Dependent on external API availability and rate limits
- Processing time varies based on topic complexity and search results
- Language support primarily optimized for English content

### Rate Limits

- Serper API: 2,500 free searches per month
- Google Gemini: Varies by subscription plan
- Recommended for moderate usage patterns

## Troubleshooting

### Common Issues

**Import Errors**

- Ensure virtual environment is activated
- Verify all dependencies are installed
- Check Python version compatibility

**API Key Errors**

- Verify API keys are correctly set in `.env` file
- Ensure API keys have proper permissions
- Check for any account restrictions or billing issues

**Search Limitations**

- Monitor Serper API usage to avoid rate limits
- Consider upgrading to paid plans for higher volume usage
- Implement caching for repeated research topics

**Performance Issues**

- Reduce research scope for faster execution
- Check internet connection stability
- Monitor system resources during execution

## Contributing

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Include comprehensive docstrings for all functions and classes
- Add type hints for improved code clarity
- Write unit tests for new functionality
- Update documentation for any changes

### Code Quality Standards

- Use meaningful variable and function names
- Implement proper error handling
- Follow the existing architectural patterns
- Maintain separation of concerns between components

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For questions, issues, or contributions, please refer to the project's issue tracking system or contact the development team.

## Version History

- **v1.0.0**: Initial release with core research functionality
- **v1.1.0**: Added Streamlit web interface
- **v1.2.0**: Enhanced error handling and logging
- **v2.0.0**: Multi-agent architecture implementation
- **v2.1.0**: Current version with improved focus areas and quality assessment
