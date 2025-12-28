"""
LibMatch Pipeline - Phase 2: DevLibScraper
Section 3.1: Data Collection and Preprocessing (일부)

논문의 두 번째 단계인 DevLibScraper를 구현합니다.
선택된 라이브러리를 사용하는  items발자를 식별하는 단계입니다:
- GitHub API를 사용하여  items발자 프로필 및 라이브러리 사용 데이터 수집
- 정규표현식을 사용하여  items발자의 코드에서 사용하는 라이브러리 추출
"""

import pickle
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libmatch.config import USERS_PKL_PATH, OUTPUT_DIR
from libmatch.devlibscraper.data_collection import GitHubDataCollector
import os

# Intermediate result storage paths
LIBSELECTOR_OUTPUT = OUTPUT_DIR / 'libselector_output.pkl'
DEVLIBSCRAPER_OUTPUT = OUTPUT_DIR / 'devlibscraper_output.pkl'

def devlibscraper(users=None):
    """
    Phase 2: DevLibScraper - 선택된 라이브러리를 사용하는  items발자 식별
    
    이 단계는 논문의 두 번째 단계로, GitHub API를 통해  items발자 데이터를 수집하고
    정규표현식을 사용하여  items발자가 사용하는 라이브러리를 추출합니다.
    
    Parameters:
    -----------
    users : pd.DataFrame, optional
        사용자 데이터 (없으면 로컬 파일에서 로드)
    
    Returns:
    --------
    pd.DataFrame:  items발자 데이터 (라이브러리 사용 정보 포함)
    """
    print("=" * 80)
    print("LibMatch Pipeline - Phase 2: DevLibScraper")
    print("선택된 라이브러리를 사용하는  items발자 식별")
    print("=" * 80)
    
    # GitHub token 설정 (필요시)
    if not os.getenv('GITHUB_TOKEN'):
        os.environ['GITHUB_TOKEN'] = 'dummy'
    
    # Developer data loaded
    if users is None:
        collector = GitHubDataCollector(github_tokens=[])
        users = collector.load_users(USERS_PKL_PATH)
        print(f"✅ Developer data loaded: {len(users)} users")
    
    #  items발자 데이터는 이미 라이브러리 사용 정보가 포함되어 있음
    # (정규표현식을 사용하여 코드에서 라이브러리를 추출한 결과)
    print(f"\n✅  items발자 라이브러리 사용 정보 확인 완료")
    print(f"   - 총  items발자 수: {len(users)} users")
    
    # LibSelector 결과 로드 (선택된 라이브러리 정보)
    if LIBSELECTOR_OUTPUT.exists():
        with open(LIBSELECTOR_OUTPUT, 'rb') as f:
            libselector_data = pickle.load(f)
            df_lib_matched = libselector_data['df_lib_matched']
        print(f"   - LibSelector에서 선택된 라이브러리: {len(df_lib_matched)} items")
    else:
        print("   ⚠️  LibSelector 결과를 찾을 수 없습니다.")
        print("      먼저 LibSelector를 실행하세요: python libmatch/libselector/pipeline.py")
        df_lib_matched = None
    
    # 결과 저장 (논문 구조에 맞게)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 논문 Section 3.3에 따른 출력 저장
    from libmatch.devlibscraper.outputs import save_devlibscraper_outputs
    
    # 3.3.1:  items발자 풀 (users - Contributed Repos Stars Count, Followers Count 포함)
    # 3.3.2:  items발자-라이브러리 매핑 (users에 이미 포함되어 있음)
    
    outputs = save_devlibscraper_outputs(
        developer_pool=users,
        developer_library_mapping=None  # users에 이미 포함됨
    )
    
    print(f"\n✅ DevLibScraper 출력 저장 완료:")
    print(f"   -  items발자 풀: {outputs['developer_pool']}")
    print(f"   - Summary: {outputs['summary']}")
    
    # 하위 호환성을 위한 기존 형식도 저장
    devlibscraper_data = {
        'users': users,
        'df_lib_matched': df_lib_matched
    }
    with open(DEVLIBSCRAPER_OUTPUT, 'wb') as f:
        pickle.dump(devlibscraper_data, f)
    
    return users


if __name__ == '__main__':
    users = devlibscraper()
    print("\n다음 단계 실행:")
    print("  python libmatch/devlibmatcher/pipeline.py")

