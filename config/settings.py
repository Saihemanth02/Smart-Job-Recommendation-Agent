import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ML_DIR = BASE_DIR / "ml"
MODEL_DIR = ML_DIR / "models"
DB_PATH = BASE_DIR / "jobs_agent.db"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
ML_DIR.mkdir(exist_ok=True, parents=True)
MODEL_DIR.mkdir(exist_ok=True, parents=True)

# LLM Models Configuration
# Task sizes and their corresponding Groq and Gemini models
MODEL_CONFIGS = {
    "small": {
        "groq": "openai/gpt-oss-20b",
        "gemini": "gemini-2.5-flash-lite"
    },
    "large": {
        "groq": "openai/gpt-oss-120b",
        "gemini": "gemini-2.5-flash"
    }
}

# Theme
THEME_ACCENT_COLOR = "#6366f1"  # Indigo accent
