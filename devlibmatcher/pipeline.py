"""
LibMatch Pipeline - Phase 3: DevLibMatcher
Section 3.4: Candidate Ranking
Section 3.5: Evaluation and Validation

Implements the third phase of the paper: DevLibMatcher.
This phase selects potential candidates using libraries identified by LibSelector:
- Identifies common elements ("overlap libraries") between libraries selected by LibSelector and libraries used by developers
- Selects potential candidates by counting shared libraries
- Classifies selected candidates using GitHub metrics (contributions, followers, etc.)
"""

import pickle
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libmatch.config import OUTPUT_DIR, USERS_PKL_PATH, DATA_DIR, PROJECT_ROOT
from libmatch.devlibmatcher.candidate_ranking import CandidateRanker
from libmatch.devlibmatcher.evaluation import Evaluator
from libmatch.devlibmatcher.label_loader import LabelLoader
from libmatch.devlibscraper.data_collection import GitHubDataCollector
import pandas as pd
import ast

# Intermediate result storage paths
DEVLIBSCRAPER_OUTPUT = OUTPUT_DIR / 'devlibscraper_output.pkl'
LIBSELECTOR_OUTPUT = OUTPUT_DIR / 'libselector_output.pkl'

def load_library_similarity_ranking(csv_path=None):
    """
    Load library_similarity_ranking.csv and convert to df_lib_matched format
    
    Parameters:
    -----------
    csv_path : str or Path, optional
        CSV file path (uses default path if not provided)
    
    Returns:
    --------
    pd.DataFrame : Library information DataFrame (includes name, keywords, cos_sim columns)
    """
    if csv_path is None:
        # Default path: libmatch/data/library_similarity_ranking.csv or project root
        csv_path = DATA_DIR / 'library_similarity_ranking.csv'
        if not csv_path.exists():
            csv_path = Path(__file__).parent.parent.parent / 'library_similarity_ranking.csv'
    
    print(f"Loading library similarity ranking CSV: {csv_path}")
    df_csv = pd.read_csv(csv_path)
    
    # Convert keywords column to list (parse string-stored list)
    if 'keywords' in df_csv.columns:
        df_csv['keywords'] = df_csv['keywords'].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
    
    # Select only required columns (same format as validation.py)
    required_columns = ['name', 'keywords', 'cos_sim']
    available_columns = [col for col in required_columns if col in df_csv.columns]
    df_lib_matched = df_csv[available_columns].copy()
    
    print(f"   ✅ Load complete: {len(df_lib_matched)} libraries")
    return df_lib_matched


def load_developer_data(developer_path=None, use_anonymized=False):
    """
    Load developer data file (includes library usage information like pkgs_used)
    Prefer CSV format.
    
    Parameters:
    -----------
    developer_path : Path, optional
        Developer data file path (auto-searches if not provided, CSV or pickle)
    use_anonymized : bool, default=False
        Use anonymized files if True (for public release)
    
    Returns:
    --------
    pd.DataFrame: Developer data (includes pkgs_used column)
    """
    if developer_path is None:
        # Possible paths (prefer anonymized files or regular files)
        if use_anonymized:
            possible_paths = [
                DATA_DIR / 'developer_pool_anonymized.csv',
                PROJECT_ROOT / 'developer_pool_anonymized.csv',
            ]
        else:
            possible_paths = [
                DATA_DIR / 'developer_pool.csv',
                PROJECT_ROOT / 'developer_pool.csv',
                USERS_PKL_PATH,
                DATA_DIR / 'developer_pool.pkl',
                PROJECT_ROOT / 'developer_pool.pkl',
            ]
        
        for path in possible_paths:
            if Path(path).exists():
                developer_path = path
                break
    
    if developer_path is None or not Path(developer_path).exists():
        raise FileNotFoundError(
            f"Developer data file not found.\n"
            f"Check the following paths:\n"
            f"  - {DATA_DIR / 'developer_pool.csv'}\n"
            f"  - {PROJECT_ROOT / 'developer_pool.csv'}\n"
            f"  - {USERS_PKL_PATH}\n"
            f"  - {DATA_DIR / 'developer_pool.pkl'}\n"
            f"  - {PROJECT_ROOT / 'developer_pool.pkl'}"
        )
    
    # Load CSV or pickle
    if Path(developer_path).suffix == '.csv':
        users = pd.read_csv(developer_path)
        # Convert pkgs_used to list if stored as string
        if 'pkgs_used' in users.columns and users['pkgs_used'].dtype == 'object':
            import ast
            users['pkgs_used'] = users['pkgs_used'].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('{') else x
            )
    else:
        # Pickle file
        collector = GitHubDataCollector(github_tokens=[])
        users = collector.load_users(developer_path)
    
    # Check required columns (pkgs_used is required, is_NLP loaded from label file)
    if 'pkgs_used' not in users.columns:
            raise ValueError(
                f"pkgs_used column not found in developer data.\n"
                f"File: {developer_path}\n"
                f"Columns: {list(users.columns)}"
            )
    
    print(f"✅ Developer data loaded: {len(users)} users (from {developer_path})")
    return users


def devlibmatcher(
    users=None, 
    labels=None,
    df_lib_matched=None, 
    use_library_ranking_csv=False,
    developer_path=None,
    label_path=None,
    use_anonymized=False
):
    """
    Phase 3: DevLibMatcher - Candidate Selection and Classification
    
    This is the third phase of the paper that identifies overlap libraries
    between libraries selected by LibSelector and libraries used by developers,
    and classifies candidates using GitHub metrics.
    
    Uses 3 files to get the same results as validation.py:
    1. Label file: is_NLP labels (validation_labels.pkl)
    2. Library ranking file: library_similarity_ranking.csv
    3. Developer data file: developer and library usage information (developer_pool.pkl)
    
    Parameters:
    -----------
    users : pd.DataFrame, optional
        Developer data (includes pkgs_used column, auto-loaded if not provided)
    labels : pd.DataFrame, optional
        Label data (includes is_NLP column, auto-loaded if not provided)
    df_lib_matched : pd.DataFrame, optional
        Matched library data (auto-loaded if not provided)
    use_library_ranking_csv : bool, default=False
        Use library_similarity_ranking.csv if True (same results as validation.py)
    developer_path : Path, optional
        Developer data file path (CSV or pickle)
    label_path : Path, optional
        Label file path (CSV or pickle)
    use_anonymized : bool, default=False
        Use anonymized files if True (for public data)
    
    Returns:
    --------
    dict: evaluation results and ranked candidates
    """
    print("=" * 80)
    print("LibMatch Pipeline - Phase 3: DevLibMatcher")
    print("Candidate Selection and Classification")
    if use_anonymized:
        print("(using anonymized data)")
    print("=" * 80)
    
    # 1. Load developer data (includes pkgs_used)
    if users is None:
        users = load_developer_data(developer_path, use_anonymized=use_anonymized)
    
    # 2. Load and merge label data (includes is_NLP)
    # Use is_NLP from developer_pool.csv if present, otherwise load from label file
    if 'is_NLP' not in users.columns:
        label_file_path, labels = LabelLoader.load_labels(label_path)
        if labels is None:
            raise FileNotFoundError(
                f"is_NLP column not found in developer data and label file not found.\n"
                f"is_NLP column is required to run validation.py.\n"
                f"\nSolution:\n"
                f"  python libmatch/devlibmatcher/label_loader.py --extract developer_pool.csv\n"
                f"\nOr create label file at the following paths:\n"
                f"  - {DATA_DIR / 'validation_labels.csv'}\n"
                f"  - {PROJECT_ROOT / 'validation_labels.csv'}"
            )
        print(f"✅ Label data loaded: {len(labels)} items (from {label_file_path})")
        print(f"   is_NLP statistics: True={labels['is_NLP'].sum()}, False={(~labels['is_NLP']).sum()}")
        
        # Merge developer data and labels
        user_id_column = 'users'  # default
        if user_id_column not in users.columns:
            # Find other possible ID columns
            possible_id_columns = ['user', 'username', 'login', 'id']
            for col in possible_id_columns:
                if col in users.columns:
                    user_id_column = col
                    break
        
        if user_id_column not in labels.columns:
            raise ValueError(
                f"User ID column not found in label file '{user_id_column}' not found.\n"
                f"Label file columns: {list(labels.columns)}"
            )
        
        # Merge
        users_with_labels = users.merge(
            labels[[user_id_column, 'is_NLP']],
            on=user_id_column,
            how='inner'
        )
        
        if len(users_with_labels) == 0:
            raise ValueError(
                f" items발자 데이터와 라벨을 Merge할 수 없습니다.\n"
                f"User ID column: {user_id_column}\n"
                f" items발자 데이터 ID 샘플: {users[user_id_column].head(3).tolist() if user_id_column in users.columns else 'N/A'}\n"
                f"Label data ID sample: {labels[user_id_column].head(3).tolist()}"
            )
        
        print(f"✅ Data merge complete: {len(users_with_labels)} users (developer data and labels merged)")
        users = users_with_labels
    else:
        print(f"✅ is_NLP column already exists in developer data.")
        print(f"   is_NLP statistics: True={users['is_NLP'].sum()}, False={(~users['is_NLP']).sum()}")
    
    if df_lib_matched is None:
        if use_library_ranking_csv:
            # Use library_similarity_ranking.csv (same results as validation.py)
            df_lib_matched = load_library_similarity_ranking()
        else:
            # Method 1: Load from DevLibScraper output (priority)
            if DEVLIBSCRAPER_OUTPUT.exists():
                print(f"\nLoading DevLibScraper results: {DEVLIBSCRAPER_OUTPUT}")
                with open(DEVLIBSCRAPER_OUTPUT, 'rb') as f:
                    scraper_data = pickle.load(f)
                    df_lib_matched = scraper_data['df_lib_matched']
                print(f"   ✅ Matched libraries: {len(df_lib_matched)} items (from {DEVLIBSCRAPER_OUTPUT})")
            else:
                # Method 2: Load from LibSelector output
                if LIBSELECTOR_OUTPUT.exists():
                    with open(LIBSELECTOR_OUTPUT, 'rb') as f:
                        libselector_data = pickle.load(f)
                        df_lib_matched = libselector_data['df_lib_matched']
                    print(f"   ✅ Matched libraries: {len(df_lib_matched)} items (from {LIBSELECTOR_OUTPUT})")
                else:
                    # Method 3: Automatically use library_similarity_ranking.csv
                    print(f"\nLibSelector 결과 파일 not found. library_similarity_ranking.csv를 사용합니다...")
                    df_lib_matched = load_library_similarity_ranking()
    
    # Step 1: Identify and count overlap libraries
    print("\n[Step 1] Identify Overlap Libraries and Select Candidates")
    print("-" * 80)
    ranker = CandidateRanker()
    
    # Generate keyword list based on N value (based on libraries selected by LibSelector)
    keyword_list = ranker.get_keyword_list(df_lib_matched, n=100)
    print(f"✅ Keyword list generated: {len(keyword_list)} items 그룹")
    
    # Filter candidates based on M value (based on number of overlap libraries)
    filtered_users = ranker.filter_candidates(users, keyword_list, m_val=3)
    print(f"✅ Filtered candidates: {len(filtered_users[filtered_users['P'] == True])} users")
    
    # Step 2: Classify and Rank Candidates Using GitHub Metrics
    print("\n[Step 2] Classify and Rank Candidates Using GitHub Metrics")
    print("-" * 80)
    ranked_candidates = ranker.rank_candidates(filtered_users)
    top_candidates = ranker.get_top_n_candidates(ranked_candidates, n=100)
    print(f"✅ Top candidates: {len(top_candidates)} users")
    
    # Step 3: Evaluation and Validation
    print("\n[Step 3] Evaluation and Validation")
    print("-" * 80)
    
    # Check is_NLP column (required)
    if 'is_NLP' not in users.columns:
        raise ValueError(
            f"users 데이터에 is_NLP 컬럼 not found.\n"
            f"Current columns: {list(users.columns)}\n"
            f"라벨과 Merge이 제대로 되지 않았습니다."
        )
    
    evaluator = Evaluator()
    df_results = evaluator.evaluate_nm_combinations(
        users.copy(),  # Use copy to protect original
        df_lib_matched
    )
    
    # Output and save results
    evaluator.print_results(df_results)
    evaluator.save_results(df_results)
    
    # Save outputs according to paper Section 3.4-3.5
    from libmatch.devlibmatcher.outputs import save_devlibmatcher_outputs
    
    # 3.4.1: Filtered candidates (M items 이상 overlap)
    # 3.4.2: Classified candidates (classification info included in ranked_candidates)
    # 3.5: Evaluation results
    
    # Extract developer classification info (Pioneers, Ambassadors, Potential, Dedicated)
    classified_candidates = None
    # Use 'contribs' column (matches paper's "Contributed Repos Stars Count (i)")
    # Fallback to 'contributions' if 'contribs' not available
    contrib_col = 'contribs' if 'contribs' in ranked_candidates.columns else 'contributions'
    followers_col = 'followers'
    
    if contrib_col in ranked_candidates.columns and followers_col in ranked_candidates.columns:
        # Classify based on median (as per paper Section 3.4.2)
        median_contributions = ranked_candidates[contrib_col].median()
        median_followers = ranked_candidates[followers_col].median()
        
        classified_candidates = ranked_candidates.copy()
        classified_candidates['developer_type'] = classified_candidates.apply(
            lambda row: 'Pioneers' if row[contrib_col] >= median_contributions and row[followers_col] >= median_followers
            else 'Ambassadors' if row[contrib_col] < median_contributions and row[followers_col] >= median_followers
            else 'Dedicated' if row[contrib_col] >= median_contributions and row[followers_col] < median_followers
            else 'Potential',
            axis=1
        )
    
    outputs = save_devlibmatcher_outputs(
        filtered_candidates=filtered_users,
        classified_candidates=classified_candidates if classified_candidates is not None else ranked_candidates,
        evaluation_results=df_results,
        m_value=3  # M value used
    )
    
    print("\n" + "=" * 80)
    print("✅ DevLibMatcher complete!")
    print(f"   Filtered candidates: {outputs['filtered_candidates']}")
    if 'classified_candidates' in outputs:
        print(f"   Classified candidates: {outputs['classified_candidates']}")
    from libmatch.config import VALIDATION_RESULTS_PATH
    print(f"   Evaluation results: {outputs.get('evaluation_results', VALIDATION_RESULTS_PATH)}")
    print(f"   Summary: {outputs['summary']}")
    print("=" * 80)
    
    return {
        'keyword_list': keyword_list,
        'filtered_users': filtered_users,
        'ranked_candidates': ranked_candidates,
        'top_candidates': top_candidates,
        'classified_candidates': classified_candidates,
        'evaluation_results': df_results,
        'outputs': outputs
    }


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='DevLibMatcher Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Validation을 실행하기 위해 3 items 파일이 필요합니다:
  1. Label 파일: validation_labels.pkl (is_NLP 라벨)
  2. Library ranking file: library_similarity_ranking.csv
  3. Developer data 파일: developer_pool.pkl (pkgs_used 포함)

자세한 내용은 libmatch/devlibmatcher/VALIDATION_DATA_STRUCTURE.md 참조
        """
    )
    parser.add_argument(
        '--use-library-ranking-csv',
        action='store_true',
        help='Use library_similarity_ranking.csv instead of LibSelector output (same as validation.py)'
    )
    parser.add_argument(
        '--use-anonymized',
        action='store_true',
        help='Use anonymized data files (for public release)'
    )
    parser.add_argument(
        '--developer-data',
        type=str,
        help=' items발자 데이터 파일 경로 (CSV 또는 pickle, 기본: 자동 검색)'
    )
    parser.add_argument(
        '--label-data',
        type=str,
        help='Label file path (CSV or pickle, default: auto-search)'
    )
    
    args = parser.parse_args()
    
    results = devlibmatcher(
        use_library_ranking_csv=args.use_library_ranking_csv,
        use_anonymized=args.use_anonymized,
        developer_path=Path(args.developer_data) if args.developer_data else None,
        label_path=Path(args.label_data) if args.label_data else None
    )
    print("\n✅ Complete LibMatch pipeline finished!")

