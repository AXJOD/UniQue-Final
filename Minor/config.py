"""
Configuration file for College AI Portal
Centralized configuration management
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CHROMA_DB_DIR = DATA_DIR / "chroma"

# Database
DB_PATH = DATA_DIR / "college_ai.db"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Convert to strings for compatibility
DB_PATH = str(DB_PATH)
UPLOADS_DIR = str(UPLOADS_DIR)
CHROMA_DB_DIR = str(CHROMA_DB_DIR)

# HuggingFace settings
HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Application settings
MAX_UPLOAD_SIZE_MB = 50
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200