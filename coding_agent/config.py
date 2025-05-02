import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_WORKING_DIR = os.getenv("WORKING_DIR", os.path.join(os.getcwd(), "project"))
LOG_DIR = os.getenv("LOG_DIR", os.path.join(PROJECT_ROOT, "logs"))
CACHE_FILE = os.getenv("CACHE_FILE", os.path.join(PROJECT_ROOT, "llm_cache.json"))

# LLM Configuration
ANTHROPIC_REGION = os.getenv("ANTHROPIC_REGION", "us-east5")
ANTHROPIC_PROJECT_ID = os.getenv("ANTHROPIC_PROJECT_ID")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet@20250219")