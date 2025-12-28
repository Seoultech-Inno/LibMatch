"""
DevLibMatcher Phase Outputs

Defines output results of DevLibMatcher according to Paper Section 3.4.

Outputs:
- 3.4.1 Library Matching: filtered_candidates (candidates with M or more overlap libraries)
- 3.4.2 Developer Classification: classified_candidates (4 types: Pioneers, Ambassadors, Potential, Dedicated)
- 3.5 Evaluation: evaluation_results (evaluation results)
"""

from pathlib import Path
from typing import Dict, Any, List
import pickle
import pandas as pd

from libmatch.config import OUTPUT_DIR

# DevLibMatcher output directory
DEVLIBMATCHER_OUTPUT_DIR = OUTPUT_DIR / 'devlibmatcher'
DEVLIBMATCHER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Output file paths
FILTERED_CANDIDATES_OUTPUT = DEVLIBMATCHER_OUTPUT_DIR / 'filtered_candidates.pkl'
CLASSIFIED_CANDIDATES_OUTPUT = DEVLIBMATCHER_OUTPUT_DIR / 'classified_candidates.pkl'
EVALUATION_RESULTS_OUTPUT = DEVLIBMATCHER_OUTPUT_DIR / 'evaluation_results.csv'
DEVLIBMATCHER_SUMMARY_OUTPUT = DEVLIBMATCHER_OUTPUT_DIR / 'devlibmatcher_summary.csv'


def save_devlibmatcher_outputs(
    filtered_candidates: pd.DataFrame,
    classified_candidates: pd.DataFrame = None,
    evaluation_results: pd.DataFrame = None,
    m_value: int = None,
    overlap_libraries_info: Dict[str, Any] = None
) -> Dict[str, Path]:
    """
    Save all outputs of DevLibMatcher Phase.
    
    Parameters:
    -----------
    filtered_candidates : pd.DataFrame
        Filtered candidates from 3.4.1 (M or more overlap libraries)
    classified_candidates : pd.DataFrame, optional
        Classified candidates from 3.4.2 (Pioneers, Ambassadors, Potential, Dedicated)
    evaluation_results : pd.DataFrame, optional
        Evaluation results from 3.5
    m_value : int, optional
        M value used (Overlap Libraries Count)
    overlap_libraries_info : Dict[str, Any], optional
        Overlap libraries information for each candidate
    
    Returns:
    --------
    Dict[str, Path]: Dictionary of saved file paths
    """
    outputs = {}
    
    # 3.4.1: Save filtered candidates
    with open(FILTERED_CANDIDATES_OUTPUT, 'wb') as f:
        pickle.dump(filtered_candidates, f)
    outputs['filtered_candidates'] = FILTERED_CANDIDATES_OUTPUT
    
    # 3.4.2: Save classified candidates
    if classified_candidates is not None:
        with open(CLASSIFIED_CANDIDATES_OUTPUT, 'wb') as f:
            pickle.dump(classified_candidates, f)
        outputs['classified_candidates'] = CLASSIFIED_CANDIDATES_OUTPUT
    
    # 3.5: Save evaluation results
    if evaluation_results is not None:
        evaluation_results.to_csv(EVALUATION_RESULTS_OUTPUT, index=False)
        outputs['evaluation_results'] = EVALUATION_RESULTS_OUTPUT
    
    # Save summary information
    summary = {
        'phase': 'DevLibMatcher',
        'filtered_candidates_count': len(filtered_candidates[filtered_candidates['P'] == True]) if 'P' in filtered_candidates.columns else len(filtered_candidates),
        'm_value': m_value,
        'has_classification': classified_candidates is not None,
        'has_evaluation': evaluation_results is not None
    }
    
    if classified_candidates is not None:
        if 'developer_type' in classified_candidates.columns:
            summary['pioneers_count'] = len(classified_candidates[classified_candidates['developer_type'] == 'Pioneers'])
            summary['ambassadors_count'] = len(classified_candidates[classified_candidates['developer_type'] == 'Ambassadors'])
            summary['potential_count'] = len(classified_candidates[classified_candidates['developer_type'] == 'Potential'])
            summary['dedicated_count'] = len(classified_candidates[classified_candidates['developer_type'] == 'Dedicated'])
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(DEVLIBMATCHER_SUMMARY_OUTPUT, index=False)
    outputs['summary'] = DEVLIBMATCHER_SUMMARY_OUTPUT
    
    return outputs


def load_devlibmatcher_outputs() -> Dict[str, Any]:
    """
    Load outputs of DevLibMatcher Phase.
    
    Returns:
    --------
    Dict[str, Any]: Dictionary of loaded data
    """
    outputs = {}
    
    if FILTERED_CANDIDATES_OUTPUT.exists():
        with open(FILTERED_CANDIDATES_OUTPUT, 'rb') as f:
            outputs['filtered_candidates'] = pickle.load(f)
    
    if CLASSIFIED_CANDIDATES_OUTPUT.exists():
        with open(CLASSIFIED_CANDIDATES_OUTPUT, 'rb') as f:
            outputs['classified_candidates'] = pickle.load(f)
    
    if EVALUATION_RESULTS_OUTPUT.exists():
        outputs['evaluation_results'] = pd.read_csv(EVALUATION_RESULTS_OUTPUT)
    
    return outputs

