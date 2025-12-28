"""
validation.py를 실행하기 위해 필요한 데이터 파일 확인 스크립트

이 스크립트는 validation.py와 동일한 결과를 얻기 위해 필요한 모든 데이터가
있는지 확인합니다.
"""

import pickle
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libmatch.config import (
    USERS_PKL_PATH, 
    DATA_DIR, 
    PROJECT_ROOT,
    JOB_POSTING_CSV_PATH
)


def check_users_file():
    """ items발자 데이터 파일 확인 (CSV 우선)"""
    print("=" * 80)
    print(" items발자 데이터 파일 확인")
    print("=" * 80)
    
    # 가능한 경로들 (CSV 우선)
    possible_paths = [
        DATA_DIR / 'developer_pool.csv',
        PROJECT_ROOT / 'developer_pool.csv',
        USERS_PKL_PATH,
        PROJECT_ROOT / 'updated_users.pkl',
    ]
    
    users_path = None
    for path in possible_paths:
        if Path(path).exists():
            users_path = path
            print(f"✅ {users_path} 발견")
            break
    
    if users_path is None:
        print(f"❌ Developer data file not found:")
        for path in possible_paths:
            print(f"   - {path}")
        return None, None
    
    # 파일 로드 및 컬럼 확인
    try:
        if users_path.suffix == '.csv':
            users = pd.read_csv(users_path)
        else:
            with open(users_path, 'rb') as f:
                users = pickle.load(f)
        
        print(f"\n📊 데이터 정보:")
        print(f"   - 총 사용자 수: {len(users)}")
        print(f"   - 컬럼 수: {len(users.columns)}")
        print(f"   - 컬럼 목록: {list(users.columns)}")
        
        # 필수 컬럼 확인 (pkgs_used는 필수, is_NLP는 label 파일에서 확인)
        required_columns = ['pkgs_used']
        missing_columns = [col for col in required_columns if col not in users.columns]
        
        if missing_columns:
            print(f"\n❌ 필수 컬럼 not found: {missing_columns}")
            return users_path, None
        
        print(f"\n✅ 필수 컬럼 확인:")
        print(f"   - pkgs_used: {'pkgs_used' in users.columns}")
        print(f"   - is_NLP: {'is_NLP' in users.columns} (라벨 파일에서 별도 관리)")
        
        return users_path, users
        
    except Exception as e:
        print(f"\n❌ 파일 로드 실패: {e}")
        return users_path, None


def check_label_file():
    """라벨 파일 확인"""
    print("\n" + "=" * 80)
    print("라벨 파일 확인 (is_NLP)")
    print("=" * 80)
    
    from libmatch.devlibmatcher.label_loader import LabelLoader
    
    label_path, labels = LabelLoader.load_labels()
    
    if label_path and labels is not None:
        print(f"✅ 라벨 파일 발견: {label_path}")
        print(f"   - 총 라벨 수: {len(labels)}")
        print(f"   - is_NLP True: {labels['is_NLP'].sum()}")
        print(f"   - is_NLP False: {(~labels['is_NLP']).sum()}")
        return label_path, labels
    else:
        print("❌ 라벨 파일을 찾을 수 없습니다.")
        print("\nSolution:")
        print("  python libmatch/devlibmatcher/label_loader.py --extract developer_pool.csv")
        return None, None


def check_library_ranking_csv():
    """라이브러리 유사도 랭킹 CSV 파일 확인"""
    print("\n" + "=" * 80)
    print("라이브러리 유사도 랭킹 CSV 파일 확인")
    print("=" * 80)
    
    # 가능한 경로들
    possible_paths = [
        DATA_DIR / 'library_similarity_ranking.csv',
        PROJECT_ROOT / 'library_similarity_ranking.csv',
    ]
    
    csv_path = None
    for path in possible_paths:
        if path.exists():
            csv_path = path
            print(f"✅ {csv_path} 발견")
            break
    
    if csv_path is None:
        print(f"❌ library_similarity_ranking.csv 파일을 찾을 수 없습니다:")
        for path in possible_paths:
            print(f"   - {path}")
        return None, None
    
    # 파일 로드 및 컬럼 확인
    try:
        df_csv = pd.read_csv(csv_path)
        
        print(f"\n📊 데이터 정보:")
        print(f"   - 총 라이브러리 수: {len(df_csv)}")
        print(f"   - 컬럼 수: {len(df_csv.columns)}")
        print(f"   - 컬럼 목록: {list(df_csv.columns)}")
        
        # 필수 컬럼 확인
        required_columns = ['name', 'keywords', 'cos_sim']
        missing_columns = [col for col in required_columns if col not in df_csv.columns]
        
        if missing_columns:
            print(f"\n❌ 필수 컬럼 not found: {missing_columns}")
            return csv_path, None
        
        print(f"\n✅ 필수 컬럼 확인:")
        for col in required_columns:
            print(f"   - {col}: {'있음' if col in df_csv.columns else '없음'}")
        
        # 데이터 샘플 확인
        print(f"\n📋 데이터 샘플 (상위 5 items):")
        print(df_csv.head(5).to_string())
        
        return csv_path, df_csv
        
    except Exception as e:
        print(f"\n❌ 파일 로드 실패: {e}")
        return csv_path, None


def check_job_posting_csv():
    """Job posting CSV 파일 확인 (참고용)"""
    print("\n" + "=" * 80)
    print("Job Posting CSV 파일 확인 (참고용)")
    print("=" * 80)
    
    if Path(JOB_POSTING_CSV_PATH).exists():
        print(f"✅ {JOB_POSTING_CSV_PATH} 발견")
        try:
            df = pd.read_csv(JOB_POSTING_CSV_PATH, index_col=0)
            print(f"   - 총 job posting 수: {len(df)}")
            if 'keyword_rd' in df.columns:
                print(f"   - keyword_rd 컬럼 있음")
            else:
                print(f"   ⚠️  keyword_rd 컬럼 없음 (필요할 수 있음)")
        except Exception as e:
            print(f"   ⚠️  파일 읽기 실패: {e}")
    else:
        print(f"⚠️  {JOB_POSTING_CSV_PATH} 없음 (library_similarity_ranking.csv가 있으면 선택사항)")


def main():
    """메인 함수"""
    print("=" * 80)
    print("validation.py 실행을 위한 데이터 요구사항 확인")
    print("=" * 80)
    
    # 1.  items발자 데이터 확인
    users_path, users = check_users_file()
    
    # 2. 라벨 파일 확인
    label_path, labels = check_label_file()
    
    # 3. 라이브러리 랭킹 CSV 확인
    csv_path, df_csv = check_library_ranking_csv()
    
    # 4. Job posting CSV 확인 (참고용)
    check_job_posting_csv()
    
    # 최종 Summary
    print("\n" + "=" * 80)
    print("최종 Summary")
    print("=" * 80)
    
    all_ok = True
    
    if users_path and users is not None:
        print(f"✅  items발자 데이터: {users_path}")
    else:
        print(f"❌  items발자 데이터: 없음")
        all_ok = False
    
    if label_path and labels is not None:
        print(f"✅ 라벨 파일: {label_path}")
    else:
        print(f"❌ 라벨 파일: 없음")
        all_ok = False
    
    if csv_path and df_csv is not None:
        print(f"✅ 라이브러리 랭킹 CSV: {csv_path}")
    else:
        print(f"❌ 라이브러리 랭킹 CSV: 없음")
        all_ok = False
    
    if all_ok:
        print("\n✅ 모든 필수 데이터가 준비되었습니다!")
        print("\n다음  users령어로 validation을 실행할 수 있습니다:")
        print("  python libmatch/devlibmatcher/pipeline.py --use-library-ranking-csv")
    else:
        print("\n❌ 일부 필수 데이터가 없습니다. 위의 오류를 확인하세요.")


if __name__ == '__main__':
    main()

