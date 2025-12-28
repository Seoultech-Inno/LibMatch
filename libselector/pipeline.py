"""
LibMatch Pipeline - Phase 1: LibSelector
Section 3.2: Keyword Extraction
Section 3.3: Semantic Matching

논문의 첫 번째 단계인 LibSelector를 구현합니다.
채용공고와 관련된 라이브러리를 선택하는 단계입니다:
- KeyBERT 알고리즘으로 채용공고에서 핵심 키워드 추출
- Libraries.io API를 사용하여 관련 라이브러리 정보 수집
- SentenceBERT를 사용하여 추출된 키워드를 기반으로 채용공고와 높은 관련성을 가진 라이브러리 선택
"""

import pickle
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libmatch.config import JOB_POSTING_CSV_PATH, OUTPUT_DIR
from libmatch.libselector.keyword_extraction import KeywordExtractor
from libmatch.libselector.semantic_matching import SemanticMatcher

# Intermediate result storage paths
LIBSELECTOR_OUTPUT = OUTPUT_DIR / 'libselector_output.pkl'

def libselector(df_lib=None):
    """
    Phase 1: LibSelector - 채용공고와 관련된 라이브러리 선택
    
    이 단계는 논문의 첫 번째 단계로, 채용공고에서 키워드를 추출하고
    관련 라이브러리를 선택합니다.
    
    Parameters:
    -----------
    df_lib : pd.DataFrame, optional
        라이브러리 데이터 (없으면 로컬 파일에서 로드)
    
    Returns:
    --------
    pd.DataFrame: 채용공고와 Matched libraries 데이터
    """
    print("=" * 80)
    print("LibMatch Pipeline - Phase 1: LibSelector")
    print("채용공고와 관련된 라이브러리 선택")
    print("=" * 80)
    
    # 라이브러리 데이터 로드 (없는 경우)
    if df_lib is None:
        from libmatch.devlibscraper.data_collection import GitHubDataCollector
        collector = GitHubDataCollector(github_tokens=[])
        df_lib = collector.load_libraries(use_local=True)
        print(f"✅ 라이브러리 데이터 로드: {len(df_lib)} items")
    
    # Step 1: KeyBERT로 채용공고에서 핵심 키워드 추출
    print("\n[Step 1] KeyBERT를 사용한 채용공고 키워드 추출")
    print("-" * 80)
    keyword_extractor = KeywordExtractor()
    kw_job = keyword_extractor.load_job_posting_keywords(
        str(JOB_POSTING_CSV_PATH),
        index=1
    )
    print(f"✅ 추출된 키워드: {len(kw_job)} items")
    
    # Step 2: SentenceBERT를 사용하여 채용공고와 관련된 라이브러리 선택
    print("\n[Step 2] SentenceBERT를 사용한 라이브러리 선택")
    print("-" * 80)
    semantic_matcher = SemanticMatcher()
    df_lib_matched = semantic_matcher.match_libraries_with_job_posting(
        df_lib,
        kw_job
    )
    print(f"✅ 선택된 라이브러리: {len(df_lib_matched)} items")
    
    # 결과 저장 (논문 구조에 맞게)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 논문 Section 3.2에 따른 출력 저장
    from libmatch.libselector.outputs import save_libselector_outputs
    
    # 3.2.1: 추출된 키워드
    # 3.2.2: 라이브러리 데이터베이스 (df_lib)
    # 3.2.3: 선택된 라이브러리 (df_lib_matched - stars+forks >= 100 필터링됨)
    
    # N값 계산 (선택된 라이브러리 수)
    n_value = len(df_lib_matched)
    
    outputs = save_libselector_outputs(
        extracted_keywords=kw_job,
        library_database=df_lib,
        selected_libraries=df_lib_matched,
        n_value=n_value
    )
    
    print(f"\n✅ LibSelector 출력 저장 완료:")
    print(f"   - 추출된 키워드: {outputs['keywords']}")
    print(f"   - 라이브러리 데이터베이스: {outputs['library_database']}")
    print(f"   - 선택된 라이브러리 (pickle): {outputs['selected_libraries']}")
    if 'selected_libraries_csv' in outputs:
        print(f"   - 선택된 라이브러리 (CSV): {outputs['selected_libraries_csv']}")
    print(f"   - Summary: {outputs['summary']}")
    
    # 하위 호환성을 위한 기존 형식도 저장
    libselector_data = {
        'df_lib_matched': df_lib_matched,
        'keywords': kw_job
    }
    with open(LIBSELECTOR_OUTPUT, 'wb') as f:
        pickle.dump(libselector_data, f)
    
    return df_lib_matched


if __name__ == '__main__':
    df_lib_matched = libselector()
    print("\n다음 단계 실행:")
    print("  python libmatch/devlibscraper/pipeline.py")

