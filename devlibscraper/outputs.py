"""
DevLibScraper Phase Outputs

논문 Section 3.3에 따른 DevLibScraper의 출력 결과를 정의합니다.

Outputs:
- 3.3.1 Developer Pooling: developer_pool ( items발자 풀, metrics 포함)
- 3.3.2 Library Extraction: developer_library_mapping ( items발자-라이브러리 매핑)
"""

from pathlib import Path
from typing import Dict, Any
import pickle
import pandas as pd

from libmatch.config import OUTPUT_DIR

# DevLibScraper 출력 디렉토리
DEVLIBSCRAPER_OUTPUT_DIR = OUTPUT_DIR / 'devlibscraper'
DEVLIBSCRAPER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 출력 파일 경로
DEVELOPER_POOL_OUTPUT = DEVLIBSCRAPER_OUTPUT_DIR / 'developer_pool.pkl'
DEVELOPER_LIBRARY_MAPPING_OUTPUT = DEVLIBSCRAPER_OUTPUT_DIR / 'developer_library_mapping.pkl'
DEVLIBSCRAPER_SUMMARY_OUTPUT = DEVLIBSCRAPER_OUTPUT_DIR / 'devlibscraper_summary.csv'


def save_devlibscraper_outputs(
    developer_pool: pd.DataFrame,
    developer_library_mapping: pd.DataFrame = None
) -> Dict[str, Path]:
    """
    DevLibScraper Phase의 모든 출력을 저장합니다.
    
    Parameters:
    -----------
    developer_pool : pd.DataFrame
        3.3.1에서 구성된  items발자 풀 (Contributed Repos Stars Count, Followers Count 등 포함)
    developer_library_mapping : pd.DataFrame, optional
        3.3.2에서 추출된  items발자-라이브러리 매핑 (없으면 developer_pool에서 추출)
    
    Returns:
    --------
    Dict[str, Path]: 저장된 파일 경로 딕셔너리
    """
    outputs = {}
    
    # 3.3.1:  items발자 풀 저장
    with open(DEVELOPER_POOL_OUTPUT, 'wb') as f:
        pickle.dump(developer_pool, f)
    outputs['developer_pool'] = DEVELOPER_POOL_OUTPUT
    
    # 3.3.2:  items발자-라이브러리 매핑 저장
    # developer_pool에 이미 라이브러리 정보가 포함되어 있으면 별도 저장
    if developer_library_mapping is not None:
        with open(DEVELOPER_LIBRARY_MAPPING_OUTPUT, 'wb') as f:
            pickle.dump(developer_library_mapping, f)
        outputs['developer_library_mapping'] = DEVELOPER_LIBRARY_MAPPING_OUTPUT
    
    # Summary 정보 저장
    summary = {
        'phase': 'DevLibScraper',
        'developer_pool_size': len(developer_pool),
        'has_library_mapping': developer_library_mapping is not None
    }
    if developer_library_mapping is not None:
        summary['library_mapping_size'] = len(developer_library_mapping)
    
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(DEVLIBSCRAPER_SUMMARY_OUTPUT, index=False)
    outputs['summary'] = DEVLIBSCRAPER_SUMMARY_OUTPUT
    
    return outputs


def load_devlibscraper_outputs() -> Dict[str, Any]:
    """
    DevLibScraper Phase의 출력을 로드합니다.
    
    Returns:
    --------
    Dict[str, Any]: 로드된 데이터 딕셔너리
    """
    outputs = {}
    
    if DEVELOPER_POOL_OUTPUT.exists():
        with open(DEVELOPER_POOL_OUTPUT, 'rb') as f:
            outputs['developer_pool'] = pickle.load(f)
    
    if DEVELOPER_LIBRARY_MAPPING_OUTPUT.exists():
        with open(DEVELOPER_LIBRARY_MAPPING_OUTPUT, 'rb') as f:
            outputs['developer_library_mapping'] = pickle.load(f)
    
    return outputs

