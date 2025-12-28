"""
LibMatch: Automating talent acquisition for competent developers from GitHub

This package implements the LibMatch approach for proactive talent acquisition
by matching job descriptions with developer libraries using KeyBERT and SentenceBERT.
"""

__version__ = "1.0.0"

from libmatch.devlibscraper.data_collection import GitHubDataCollector
from libmatch.libselector.keyword_extraction import KeywordExtractor
from libmatch.libselector.semantic_matching import SemanticMatcher
from libmatch.devlibmatcher.candidate_ranking import CandidateRanker
from libmatch.devlibmatcher.evaluation import Evaluator
from libmatch.run_pipeline import run_full_pipeline

__all__ = [
    'GitHubDataCollector',
    'KeywordExtractor',
    'SemanticMatcher',
    'CandidateRanker',
    'Evaluator',
    'run_full_pipeline',
]
