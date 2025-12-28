"""
LibSelector Phase Outputs

논문 Section 3.2에 따른 LibSelector의 출력 결과를 정의합니다.

Outputs:
- 3.2.1 Keyword Extraction: extracted_keywords (채용공고에서 추출된 키워드)
- 3.2.2 Keyword Conversion: library_database (구조화된 라이브러리 데이터베이스)
- 3.2.3 Library Selection: selected_libraries (상위 N items 선택된 라이브러리, stars+forks >= 100)
"""

from pathlib import Path
from typing import Dict, Any
import pickle
import pandas as pd

from libmatch.config import OUTPUT_DIR

# LibSelector 출력 디렉토리
LIBSELECTOR_OUTPUT_DIR = OUTPUT_DIR / 'libselector'
LIBSELECTOR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 출력 파일 경로
KEYWORDS_OUTPUT = LIBSELECTOR_OUTPUT_DIR / 'extracted_keywords.pkl'
LIBRARY_DATABASE_OUTPUT = LIBSELECTOR_OUTPUT_DIR / 'library_database.pkl'
SELECTED_LIBRARIES_OUTPUT = LIBSELECTOR_OUTPUT_DIR / 'selected_libraries.pkl'
SELECTED_LIBRARIES_CSV_OUTPUT = LIBSELECTOR_OUTPUT_DIR / 'selected_libraries.csv'  # CSV 형식 출력
LIBSELECTOR_SUMMARY_OUTPUT = LIBSELECTOR_OUTPUT_DIR / 'libselector_summary.csv'


def save_libselector_outputs(
    extracted_keywords: list,
    library_database: pd.DataFrame,
    selected_libraries: pd.DataFrame,
    n_value: int = None
) -> Dict[str, Path]:
    """
    LibSelector Phase의 모든 출력을 저장합니다.
    
    Parameters:
    -----------
    extracted_keywords : list
        3.2.1에서 추출된 키워드 리스트
    library_database : pd.DataFrame
        3.2.2에서 구조화된 라이브러리 데이터베이스
    selected_libraries : pd.DataFrame
        3.2.3에서 선택된 상위 N libraries (stars+forks >= 100)
    n_value : int, optional
        선택된 라이브러리 수 (N)
    
    Returns:
    --------
    Dict[str, Path]: 저장된 파일 경로 딕셔너리
    """
    outputs = {}
    
    # 3.2.1: 추출된 키워드 저장
    with open(KEYWORDS_OUTPUT, 'wb') as f:
        pickle.dump(extracted_keywords, f)
    outputs['keywords'] = KEYWORDS_OUTPUT
    
    # 3.2.2: 라이브러리 데이터베이스 저장
    with open(LIBRARY_DATABASE_OUTPUT, 'wb') as f:
        pickle.dump(library_database, f)
    outputs['library_database'] = LIBRARY_DATABASE_OUTPUT
    
    # 3.2.3: 선택된 라이브러리 저장 (pickle 형식)
    with open(SELECTED_LIBRARIES_OUTPUT, 'wb') as f:
        pickle.dump(selected_libraries, f)
    outputs['selected_libraries'] = SELECTED_LIBRARIES_OUTPUT
    
    # 3.2.3: 선택된 라이브러리 저장 (CSV 형식 - library_similarity_ranking.csv와 동일한 형식)
    df_lib_csv = selected_libraries.copy()
    
    # rank 컬럼 추가 (cos_sim 기준으로 이미 정렬되어 있음)
    df_lib_csv.insert(0, 'rank', range(1, len(df_lib_csv) + 1))
    
    # 컬럼 순서 정리: rank, name, cos_sim, keywords, stars, forks, weight
    csv_columns = ['rank', 'name', 'cos_sim', 'keywords']
    for col in ['stars', 'forks', 'weight']:
        if col in df_lib_csv.columns:
            csv_columns.append(col)
    
    # 존재하는 컬럼만 선택
    available_columns = [col for col in csv_columns if col in df_lib_csv.columns]
    df_lib_csv = df_lib_csv[available_columns]
    
    # CSV 저장
    df_lib_csv.to_csv(SELECTED_LIBRARIES_CSV_OUTPUT, index=False, encoding='utf-8-sig')
    outputs['selected_libraries_csv'] = SELECTED_LIBRARIES_CSV_OUTPUT
    
    # Summary 정보 저장 (CSV)
    summary = {
        'phase': 'LibSelector',
        'extracted_keywords_count': len(extracted_keywords),
        'library_database_size': len(library_database),
        'selected_libraries_count': len(selected_libraries),
        'n_value': n_value if n_value else len(selected_libraries)
    }
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(LIBSELECTOR_SUMMARY_OUTPUT, index=False)
    outputs['summary'] = LIBSELECTOR_SUMMARY_OUTPUT
    
    return outputs


def load_libselector_outputs() -> Dict[str, Any]:
    """
    LibSelector Phase의 출력을 로드합니다.
    
    Returns:
    --------
    Dict[str, Any]: 로드된 데이터 딕셔너리
    """
    outputs = {}
    
    if KEYWORDS_OUTPUT.exists():
        with open(KEYWORDS_OUTPUT, 'rb') as f:
            outputs['keywords'] = pickle.load(f)
    
    if LIBRARY_DATABASE_OUTPUT.exists():
        with open(LIBRARY_DATABASE_OUTPUT, 'rb') as f:
            outputs['library_database'] = pickle.load(f)
    
    if SELECTED_LIBRARIES_OUTPUT.exists():
        with open(SELECTED_LIBRARIES_OUTPUT, 'rb') as f:
            outputs['selected_libraries'] = pickle.load(f)
    
    return outputs

