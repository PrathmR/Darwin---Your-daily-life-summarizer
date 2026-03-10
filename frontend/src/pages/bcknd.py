import sys
import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import logging
from groq import Groq
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Load environment variables from .env file
load_dotenv()

# Add archon_v1 directory to sys.path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)e

app = FastAPI()

# Configure CORS
origins = ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ResearchRequest(BaseModel):
    query: str

# Initialize Groq client with API key from environment
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logger.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY environment variable is required")

client = Groq(api_key=groq_api_key)

async def get_paper_summary(papers):
    try:
        # Format papers for Groq
        papers_text = "\n\n".join([
            f"Title: {paper['title']}\nAbstract: {paper.get('abstract', 'No abstract available')}\nAuthors: {', '.join(paper.get('authors', ['Unknown']))}\nYear: {paper.get('year', 'N/A')}\nVenue: {paper.get('venue', 'N/A')}\nCitations: {paper.get('citation_count', 'N/A')}"
            for paper in papers
        ])
        
        # Create a detailed prompt for Groq
        prompt = f"""You are a research assistant specializing in academic paper analysis and summarization.
        Please analyze the following research papers and provide a comprehensive response in proper markdown format that includes:

        # Research Analysis Report

        ## 1. Background Information
        - Provide a general overview of the research field
        - Explain key concepts and terminology
        - Describe the historical context and evolution of the field
        - Highlight the significance of this research area

        ## 2. Research Analysis
        - Identify the main research questions and objectives
        - Summarize key findings and methodologies
        - Highlight common themes and patterns across papers
        - Discuss implications and future research directions

        ## 3. Practical Applications
        - Explain how this research can be applied in real-world scenarios
        - Discuss potential impact on industry and society
        - Identify challenges and limitations
        - Suggest areas for further investigation

        ## 4. Key Insights
        - List the most important findings and their implications
        - Highlight any surprising or unexpected results
        - Note any gaps in current research
        - Suggest potential areas for future research

        ## 5. Follow-up Questions
        - Suggest relevant follow-up questions for deeper understanding
        - Identify areas that need further investigation
        - Recommend related research topics
        
        Papers to analyze:
        {papers_text}
        
        Please provide a detailed analysis that connects these papers and their findings.
        Focus on synthesizing the information rather than just listing paper details.
        Use proper markdown formatting with headers, bullet points, and emphasis where appropriate.
        """
        
        # Get summary from Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant specializing in academic paper analysis and summarization. Your responses should be comprehensive, well-structured in markdown format, and highlight key insights while providing necessary background context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.3,
            max_tokens=2000,
            top_p=0.9
        )
        summary = chat_completion.choices[0].message.content
        logger.info("Successfully generated markdown-formatted summary using Groq")
        return summary
    except Exception as e:
        logger.error(f"Error getting paper summary from Groq: {e}")
        # Fallback: simple concatenated summary in markdown
        fallback = "# Research Summary\n\n"
        for paper in papers:
            fallback += f"## {paper.get('title', 'Untitled')}\n\n"
            fallback += f"**Authors:** {', '.join(paper.get('authors', ['Unknown']))}\n\n"
            fallback += f"**Abstract:** {paper.get('abstract', 'No abstract available.')}\n\n"
            fallback += f"**Year:** {paper.get('year', 'N/A')}\n\n"
            fallback += f"**Venue:** {paper.get('venue', 'N/A')}\n\n"
            fallback += "---\n\n"
        return fallback

@app.post("/research")
async def research_papers(request: ResearchRequest):
    try:
        logger.info(f"[API] /research endpoint called with query: {request.query}")
        print_colored_message("api", "info", f"Processing research query: {request.query}")
        
        # First get papers from your existing pipeline
        try:
            from scrapers.research_scraper import fetch_research_papers
            print_colored_message("api", "process", "Fetching research papers...")
            papers = await fetch_research_papers(request.query)
            
            if not papers:
                logger.warning("No papers found for the query")
                print_colored_message("api", "warning", "No papers found for the query")
                return {
                    "summary": "No relevant papers found for your query. Please try a different search term.",
                    "papers": []
                }
            
            logger.info(f"Found {len(papers)} papers for analysis")
            print_colored_message("api", "success", f"Found {len(papers)} papers for analysis")
            
            # Log paper sources
            sources = {}
            for paper in papers:
                source = paper.get("source", "Unknown")
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sources.items():
                print_colored_message("scraper", "info", f"Retrieved {count} papers from {source}")
            
        except ImportError as e:
            logger.error(f"Import error: {e}")
            print_colored_message("api", "error", f"Import error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        except Exception as e:
            logger.error(f"Error getting papers: {e}")
            print_colored_message("api", "error", f"Error getting papers: {e}")
            raise HTTPException(status_code=500, detail="Error getting research papers")

        # Get detailed summary using Groq
        print_colored_message("api", "process", "Generating comprehensive summary...")
        summary = await get_paper_summary(papers)
        print_colored_message("api", "success", "Summary generated successfully")
        
        # Log the completion of the process
        print_colored_message("api", "completed", "Research analysis completed successfully")
        
        return {
            "summary": summary,
            "papers": papers
        }
    except Exception as e:
        logger.error(f"Error processing research request: {e}")
        print_colored_message("api", "error", f"Error processing research request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def print_colored_message(agent: str, status: str, message: str):
    """Print colored messages for different agents and statuses"""
    colors = {
        "api": {
            "info": "\033[94m",  # Blue
            "process": "\033[93m",  # Yellow
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "completed": "\033[92m"  # Green
        },
        "scraper": {
            "info": "\033[96m",  # Cyan
            "process": "\033[93m",  # Yellow
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "completed": "\033[92m"  # Green
        },
        "llm": {
            "info": "\033[97m",  # White
            "process": "\033[93m",  # Yellow
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "completed": "\033[92m"  # Green
        },
        "supervisor": {
            "info": "\033[93m",  # Yellow
            "process": "\033[93m",  # Yellow
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "completed": "\033[92m"  # Green
        },
        "agents": { # New category for AGENTS
            "info": "\033[94m",    # Blue
            "process": "\033[96m", # Cyan (using cyan for process, as yellow is taken by supervisor)
            "success": "\033[92m", # Green
            "warning": "\033[93m", # Yellow
            "error": "\033[91m",   # Red
            "completed": "\033[92m" # Green
        }
    }
    
    agent_colors = {
        "api": "\033[95m",         # Magenta
        "scraper": "\033[96m",     # Cyan
        "llm": "\033[97m",         # White (example, if you use it)
        "supervisor": "\033[93m",  # Yellow
        "agents": "\033[94m",      # Blue (for general agent messages)
        # Add other specific agent types here if they have dedicated colors
    }
    
    reset = "\033[0m"
    # Ensure agent_color gets a string, not a dict.
    # The .get(agent) should point to a flat dict entry for agent_colors.
    # The status_color correctly uses the nested 'colors' dict.
    agent_name_color = agent_colors.get(agent.lower(), "\033[97m") # Use lower() for case-insensitivity
    status_display_color = colors.get(agent.lower(), {}).get(status.lower(), "\033[97m") # Also use lower()
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{agent_name_color}[{agent.upper()}]{reset} {status_display_color}[{status.upper()}]{reset} [{timestamp}] {message}")

print("🚀 backend_api.py loaded")





from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend port!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
