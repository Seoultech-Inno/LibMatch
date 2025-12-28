"""
Data Requirements Checker
Verifies that all required data files and dependencies are available for reproducing paper results.
"""

import os
from pathlib import Path
from typing import List, Tuple

from libmatch.config import (
    USERS_PKL_PATH,
    JOB_POSTING_CSV_PATH,
    KEYBERT_MODEL_PATH,
    SENTENCE_BERT_MODEL_PATH,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,
    LIBRARIES_PKL_PATH,
    USE_LOCAL_DATA
)


def check_file_exists(file_path: Path, description: str) -> Tuple[bool, str]:
    """
    Check if a file exists
    
    Parameters:
    -----------
    file_path : Path
        Path to file
    description : str
        Description of the file
    
    Returns:
    --------
    Tuple[bool, str] : (exists, message)
    """
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return True, f"✅ {description}: Found ({size_mb:.2f} MB)"
    else:
        return False, f"❌ {description}: NOT FOUND at {file_path}"


def check_model_files(model_path: Path, model_name: str) -> Tuple[bool, List[str]]:
    """
    Check if model files exist
    
    Parameters:
    -----------
    model_path : Path
        Path to model directory
    model_name : str
        Name of the model
    
    Returns:
    --------
    Tuple[bool, List[str]] : (all_exist, messages)
    """
    required_files = [
        'config.json',
        'tokenizer.json',
        'vocab.txt',
        'special_tokens_map.json',
        'tokenizer_config.json'
    ]
    
    # Check for model weights (either safetensors or pytorch_model.bin)
    model_weights = ['model.safetensors', 'pytorch_model.bin']
    has_weights = any((model_path / w).exists() for w in model_weights)
    
    messages = []
    all_exist = True
    
    if not model_path.exists():
        messages.append(f"❌ {model_name}: Directory not found at {model_path}")
        return False, messages
    
    messages.append(f"📁 {model_name}: Directory found")
    
    for file in required_files:
        file_path = model_path / file
        if file_path.exists():
            messages.append(f"  ✅ {file}")
        else:
            messages.append(f"  ❌ {file} - MISSING")
            all_exist = False
    
    if has_weights:
        for w in model_weights:
            if (model_path / w).exists():
                size_mb = (model_path / w).stat().st_size / (1024 * 1024)
                messages.append(f"  ✅ Model weights: {w} ({size_mb:.2f} MB)")
                break
    else:
        messages.append(f"  ❌ Model weights: NOT FOUND (need model.safetensors or pytorch_model.bin)")
        all_exist = False
    
    return all_exist, messages


def check_mongodb_connection() -> Tuple[bool, str]:
    """
    Check MongoDB connection
    
    Returns:
    --------
    Tuple[bool, str] : (connected, message)
    """
    try:
        from pymongo.mongo_client import MongoClient
        from pymongo.server_api import ServerApi
        
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB_NAME]
        col = db[MONGO_COLLECTION_NAME]
        
        # Try to count documents
        count = col.count_documents({})
        client.close()
        
        return True, f"✅ MongoDB: Connected (Database: {MONGO_DB_NAME}, Collection: {MONGO_COLLECTION_NAME}, Documents: {count:,})"
    except Exception as e:
        return False, f"❌ MongoDB: Connection failed - {str(e)}"


def check_environment_variables() -> List[Tuple[bool, str]]:
    """
    Check required environment variables
    
    Returns:
    --------
    List[Tuple[bool, str]] : List of (set, message) tuples
    """
    results = []
    
    # Check MongoDB URI
    mongo_uri = os.getenv('MONGO_URI', '')
    if mongo_uri:
        results.append((True, f"✅ MONGO_URI: Set"))
    else:
        results.append((False, f"⚠️  MONGO_URI: Not set (using default from config.py)"))
    
    # Check GitHub token (optional)
    github_token = os.getenv('GITHUB_TOKEN', '')
    if github_token:
        results.append((True, f"✅ GITHUB_TOKEN: Set"))
    else:
        results.append((False, f"⚠️  GITHUB_TOKEN: Not set (only needed for data collection)"))
    
    return results


def check_data_requirements():
    """
    Check all data requirements for paper reproduction
    """
    print("=" * 80)
    print("LibMatch Data Requirements Check")
    print("=" * 80)
    print()
    
    all_ok = True
    
    # Check data files
    print("[1] Data Files")
    print("-" * 80)
    
    exists, msg = check_file_exists(USERS_PKL_PATH, "User Data (updated_users.pkl)")
    print(msg)
    if not exists:
        all_ok = False
    
    exists, msg = check_file_exists(JOB_POSTING_CSV_PATH, "Job Posting Data (job_posting_update.csv)")
    print(msg)
    if not exists:
        all_ok = False
    
    print()
    
    # Check model files
    print("[2] Model Files")
    print("-" * 80)
    
    all_exist, messages = check_model_files(KEYBERT_MODEL_PATH, "KeyBERT Model")
    for msg in messages:
        print(msg)
    if not all_exist:
        all_ok = False
    
    print()
    
    all_exist, messages = check_model_files(SENTENCE_BERT_MODEL_PATH, "SentenceBERT Model")
    for msg in messages:
        print(msg)
    if not all_exist:
        all_ok = False
    
    print()
    
    # Check local library data
    print("[3] Local Library Data")
    print("-" * 80)
    exists, msg = check_file_exists(LIBRARIES_PKL_PATH, "Library Data (libraries.pkl)")
    print(msg)
    # Check for library_similarity_ranking.csv instead
    ranking_csv_path = DATA_DIR / 'library_similarity_ranking.csv'
    if not exists and not ranking_csv_path.exists():
        print("  ⚠️  Library data not found.")
        print("  💡 For validation, library_similarity_ranking.csv should be in libmatch/data/")
        if USE_LOCAL_DATA:
            all_ok = False
    elif ranking_csv_path.exists():
        print("  ✅ Library similarity ranking CSV available (sufficient for validation).")
    else:
        print("  ✅ Local library data available. MongoDB connection not required.")
    
    print()
    
    # Check MongoDB connection (only if local data not available)
    print("[4] MongoDB Connection (Fallback)")
    print("-" * 80)
    if LIBRARIES_PKL_PATH.exists():
        print("  ℹ️  Skipped (local data available)")
    else:
        connected, msg = check_mongodb_connection()
        print(msg)
        if not connected:
            all_ok = False
    
    print()
    
    # Check environment variables
    print("[5] Environment Variables")
    print("-" * 80)
    env_results = check_environment_variables()
    for is_set, msg in env_results:
        print(msg)
        if not is_set and "MONGO_URI" in msg:
            all_ok = False
    
    print()
    print("=" * 80)
    
    if all_ok:
        print("✅ All requirements met! You can run the pipeline.")
    else:
        print("❌ Some requirements are missing. Please check the messages above.")
        print("\nFor more information, see REPRODUCTION_GUIDE.md")
    
    print("=" * 80)
    
    return all_ok


if __name__ == '__main__':
    check_data_requirements()

