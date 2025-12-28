"""
Configuration file for LibMatch
Manages configuration values used in the Method section of the paper.
"""

import os
from pathlib import Path

# Project root directory (libmatch package root)
LIBMATCH_ROOT = Path(__file__).parent
# Project root (parent directory of libmatch) - maintained for backward compatibility
PROJECT_ROOT = LIBMATCH_ROOT.parent

# ============================================================================
# Section 3.1: Data Collection and Preprocessing Configuration
# ============================================================================

# GitHub API configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_TOKENS = [token.strip() for token in GITHUB_TOKEN.split(',')] if GITHUB_TOKEN else []

# Supported programming languages
SUPPORTED_LANGUAGES = ['Python', 'Jupyter Notebook']

# MongoDB configuration
# NOTE: MongoDB URI must be set via environment variable. Sensitive information is removed when uploading to GitHub.
# Usage: export MONGO_URI="your_mongodb_uri" or use .env file
# .env file example:
#   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
#   MONGO_DB_NAME=research
#   MONGO_COLLECTION_NAME=library
MONGO_URI = os.getenv('MONGO_URI', '')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'research')
MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME', 'library')

# Data file paths
# Prefer files inside libmatch/data/, fallback to project root
DATA_DIR = LIBMATCH_ROOT / 'data'
# Developer Pool (Phase 2: DevLibScraper output) - Paper Section 3.3.1
DEVELOPER_POOL_PKL_PATH = DATA_DIR / 'developer_pool.pkl' if (DATA_DIR / 'developer_pool.pkl').exists() else PROJECT_ROOT / 'developer_pool.pkl'
# Maintain USERS_PKL_PATH for backward compatibility (deprecated)
USERS_PKL_PATH = DEVELOPER_POOL_PKL_PATH
JOB_POSTING_CSV_PATH = DATA_DIR / 'job_posting_update.csv' if (DATA_DIR / 'job_posting_update.csv').exists() else PROJECT_ROOT / 'job_posting_update.csv'

# ============================================================================
# Section 3.2: Keyword Extraction Configuration
# ============================================================================

# KeyBERT model path
# Prefer model inside libmatch/model/, fallback to output/ in project root
MODEL_DIR = LIBMATCH_ROOT / 'model' / 'all-mpnet-base-v2-finetuned-stackwiki-accelerate'
KEYBERT_MODEL_PATH = MODEL_DIR if MODEL_DIR.exists() else PROJECT_ROOT / 'output' / 'all-mpnet-base-v2-finetuned-stackwiki-accelerate'

# KeyBERT parameters
KEYBERT_TOP_N = 50  # Number of keywords to extract
KEYBERT_USE_MMR = False  # Whether to use MMR (Maximal Marginal Relevance)

# Stopwords configuration
STOPWORDS = {'python', 'jupyter', 'notebook', 'artificial', 'intelligence', 'ai', 'learning'}

# ============================================================================
# Section 3.3: Semantic Matching Configuration
# ============================================================================

# SentenceBERT model path
# Prefer model inside libmatch/model/, fallback to output/ in project root
SENTENCE_BERT_MODEL_PATH = MODEL_DIR if MODEL_DIR.exists() else PROJECT_ROOT / 'output' / 'all-mpnet-base-v2-finetuned-stackwiki-accelerate'

# Library filtering thresholds
LIBRARY_MIN_WEIGHT = 100  # Minimum sum of stars + forks
LIBRARY_MIN_STARS = 0  # Minimum number of stars
LIBRARY_MIN_FORKS = 0  # Minimum number of forks

# ============================================================================
# Section 3.4: Candidate Ranking Configuration
# ============================================================================

# N value: Minimum number of libraries to have more than n unique keywords after deduplication
DEFAULT_N_VALUES = [25, 50, 75, 100, 125, 150, 175, 200]

# M value: Minimum number of matching libraries
DEFAULT_M_VALUES = [1, 2, 3, 4, 5, 6]

# ============================================================================
# Section 3.5: Evaluation and Validation Configuration
# ============================================================================

# Output directory path
OUTPUT_DIR = PROJECT_ROOT / 'results'
OUTPUT_DIR.mkdir(exist_ok=True)

VALIDATION_RESULTS_PATH = OUTPUT_DIR / 'validation_results.csv'

# ============================================================================
# Local Data Directory
# ============================================================================

# Local data directory (for downloaded MongoDB data)
# DATA_DIR is already defined above (LIBMATCH_ROOT / 'data')
DATA_DIR.mkdir(exist_ok=True)

# Local library data file path (pickle format only)
LIBRARIES_PKL_PATH = DATA_DIR / 'libraries.pkl'

# Use local data if available (set to True to prefer local files over MongoDB)
USE_LOCAL_DATA = True

