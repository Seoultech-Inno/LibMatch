"""
LibMatch 전체 파이프라인 실행 스크립트

논문의 3단계 프레임워크를 순차적으로 실행합니다:
1. Phase 1: LibSelector - 채용공고와 관련된 라이브러리 선택
2. Phase 2: DevLibScraper - 선택된 라이브러리를 사용하는  items발자 식별
3. Phase 3: DevLibMatcher - Candidate Selection and Classification
"""

import sys
from pathlib import Path

# libmatch 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from libmatch.libselector.pipeline import libselector
from libmatch.devlibscraper.pipeline import devlibscraper
from libmatch.devlibmatcher.pipeline import devlibmatcher


def run_full_pipeline():
    """
    전체 파이프라인 실행
    """
    print("=" * 80)
    print("LibMatch 전체 파이프라인 실행")
    print("논문의 3단계 프레임워크 실행")
    print("=" * 80)
    
    try:
        # Phase 1: LibSelector - 채용공고와 관련된 라이브러리 선택
        df_lib_matched = libselector()
        
        # Phase 2: DevLibScraper - 선택된 라이브러리를 사용하는  items발자 식별
        # Note: developer_pool.pkl이 이미 있으면 DevLibScraper는 선택사항
        # DevLibMatcher가 자동으로 파일에서 로드함
        try:
            users = devlibscraper()
        except Exception as e:
            print(f"\n⚠️  DevLibScraper 실행 스킵: {e}")
            print("   DevLibMatcher가 직접 파일에서 로드합니다...")
            users = None
        
        # Phase 3: DevLibMatcher - Candidate Selection and Classification
        # users와 df_lib_matched가 None이면 자동으로 파일에서 로드
        results = devlibmatcher(users=users, df_lib_matched=df_lib_matched)
        
        print("\n" + "=" * 80)
        print("✅ 전체 파이프라인 실행 완료!")
        print("=" * 80)
        
        return {
            'users': users,
            'df_lib_matched': df_lib_matched,
            **results
        }
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    results = run_full_pipeline()

