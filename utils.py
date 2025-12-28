"""
Common utility functions
Defines functions commonly used across multiple sections of the paper.
"""

import re
from typing import List, Set


def in_stopwords(string: str, stopwords: Set[str] = None) -> bool:
    """
    Check if a specific stopword is contained in the string
    
    Parameters:
    -----------
    string : str
        String to check
    stopwords : Set[str], optional
        Set of stopwords (default: None, loaded from config)
    
    Returns:
    --------
    bool : True if stopword is contained, False otherwise
    """
    if stopwords is None:
        from libmatch.config import STOPWORDS
        stopwords = STOPWORDS
    
    if string == 'learning':
        return True
    
    # Check stopword inclusion using regex
    strings = '|'.join([r'\b\w*' + i + r'\w*\b' for i in stopwords])
    pattern = re.compile(strings, re.IGNORECASE)
    matches = re.findall(pattern, string)
    return len(matches) > 0


def remove_stopwords_from_keywords(keywords: List[str], stopwords: Set[str] = None) -> List[str]:
    """
    Remove stopwords from keywords list
    
    Parameters:
    -----------
    keywords : List[str]
        List of keywords
    stopwords : Set[str], optional
        Set of stopwords (default: None, loaded from config)
    
    Returns:
    --------
    List[str] : Keywords list with stopwords removed
    """
    if stopwords is None:
        from libmatch.config import STOPWORDS
        stopwords = STOPWORDS
    
    return [word for word in keywords if not in_stopwords(word, stopwords)]


def extract_library_name_from_import(import_statement: str) -> str:
    """
    Extract library name from import statement
    
    Parameters:
    -----------
    import_statement : str
        Import statement (e.g., "import numpy", "from sklearn import")
    
    Returns:
    --------
    str : Top-level package name (e.g., "numpy", "sklearn")
    """
    # Replace dots with spaces and extract the first word (top-level package)
    library_name = import_statement.replace('.', ' ').split()[1]
    return library_name.split('.')[0]  # tensorflow.keras -> tensorflow

