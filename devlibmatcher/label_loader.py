"""
Label Loader Module

validation.py를 실행하기 위한 라벨 데이터를 로드하는 모듈입니다.
is_NLP 컬럼이 포함된 라벨 파일을 별도로 관리합니다.
"""

import pickle
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libmatch.config import DATA_DIR, PROJECT_ROOT


class LabelLoader:
    """
    Label 파일을 로드하는 클래스
    
    validation.py를 실행하기 위해 필요한 is_NLP 라벨을 관리합니다.
    Prefer CSV format.
    """
    
    # 가능한 라벨 파일 경로들 (익 users화된 파일 우선, CSV 우선, pickle은 하위 호환성)
    POSSIBLE_LABEL_PATHS = [
        DATA_DIR / 'validation_labels_anonymized.csv',  # 익 users화된 파일 (공 items용)
        PROJECT_ROOT / 'validation_labels_anonymized.csv',
        DATA_DIR / 'validation_labels.csv',
        PROJECT_ROOT / 'validation_labels.csv',
        DATA_DIR / 'validation_labels.pkl',
        PROJECT_ROOT / 'validation_labels.pkl',
        PROJECT_ROOT / 'updated_users.pkl',  # 하위 호환성
    ]
    
    @classmethod
    def find_label_file(cls) -> Optional[Path]:
        """
        라벨 파일을 찾습니다.
        
        Returns:
        --------
        Path or None: 라벨 파일 경로 (없으면 None)
        """
        for path in cls.POSSIBLE_LABEL_PATHS:
            if path.exists():
                return path
        return None
    
    @classmethod
    def load_labels(cls, label_path: Optional[Path] = None) -> Tuple[Optional[Path], Optional[pd.DataFrame]]:
        """
        라벨 파일을 로드합니다 (CSV 또는 pickle).
        
        Parameters:
        -----------
        label_path : Path, optional
            라벨 파일 경로 (없으면 자동으로 찾음)
        
        Returns:
        --------
        Tuple[Path or None, DataFrame or None]: (파일 경로, 라벨 데이터)
        """
        if label_path is None:
            label_path = cls.find_label_file()
        
        if label_path is None:
            return None, None
        
        try:
            # CSV 파일인지 확인
            if label_path.suffix == '.csv':
                labels = pd.read_csv(label_path)
            else:
                # Pickle file
                with open(label_path, 'rb') as f:
                    labels = pickle.load(f)
            
            # DataFrame이 아닌 경우 처리
            if not isinstance(labels, pd.DataFrame):
                raise ValueError(f"라벨 파일은 pandas DataFrame이어야 합니다.")
            
            # is_NLP 컬럼 확인
            if 'is_NLP' not in labels.columns:
                raise ValueError(
                    f"라벨 파일에 is_NLP 컬럼 not found.\n"
                    f"파일: {label_path}\n"
                    f"컬럼: {list(labels.columns)}"
                )
            
            # is_NLP를 boolean으로 변환 (CSV에서 로드한 경우)
            if labels['is_NLP'].dtype == 'object':
                labels['is_NLP'] = labels['is_NLP'].map(lambda x: str(x).lower() == 'true' if isinstance(x, str) else bool(x))
            
            return label_path, labels
            
        except Exception as e:
            print(f"라벨 파일 로드 실패: {e}")
            return label_path, None
    
    @classmethod
    def extract_labels(cls, users_df: pd.DataFrame, user_id_column: str = 'users') -> pd.DataFrame:
        """
        사용자 데이터에서 라벨만 추출합니다.
        
        Parameters:
        -----------
        users_df : pd.DataFrame
            사용자 데이터 (is_NLP 컬럼 포함)
        user_id_column : str, default='users'
            User ID column users
        
        Returns:
        --------
        pd.DataFrame: 라벨만 포함된 DataFrame (user_id, is_NLP)
        """
        if 'is_NLP' not in users_df.columns:
            raise ValueError("사용자 데이터에 is_NLP 컬럼 not found.")
        
        if user_id_column not in users_df.columns:
            raise ValueError(f"User ID column '{user_id_column}' not found.")
        
        # 라벨만 추출
        label_df = users_df[[user_id_column, 'is_NLP']].copy()
        
        return label_df
    
    @classmethod
    def save_labels(cls, labels_df: pd.DataFrame, output_path: Optional[Path] = None, format: str = 'csv') -> Path:
        """
        라벨을 별도 파일로 저장합니다 (CSV 형식 기본).
        
        Parameters:
        -----------
        labels_df : pd.DataFrame
            라벨 데이터 (user_id, is_NLP 컬럼 포함)
        output_path : Path, optional
            저장 경로 (없으면 기본 경로 사용)
        format : str, default='csv'
            저장 형식 ('csv' 또는 'pkl')
        
        Returns:
        --------
        Path: 저장된 파일 경로
        """
        if output_path is None:
            if format == 'csv':
                output_path = DATA_DIR / 'validation_labels.csv'
            else:
                output_path = DATA_DIR / 'validation_labels.pkl'
        
        # 디렉토리 생성
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 저장
        if format == 'csv':
            labels_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            with open(output_path, 'wb') as f:
                pickle.dump(labels_df, f)
        
        print(f"✅ 라벨 파일 저장 완료: {output_path}")
        print(f"   - 총 라벨 수: {len(labels_df)}")
        print(f"   - is_NLP True: {labels_df['is_NLP'].sum()}")
        print(f"   - is_NLP False: {(~labels_df['is_NLP']).sum()}")
        
        return output_path


def create_label_file_from_users(users_path: Path, output_path: Optional[Path] = None, format: str = 'csv') -> Path:
    """
    사용자 데이터 파일에서 라벨만 추출하여 별도 파일로 저장합니다.
    
    Parameters:
    -----------
    users_path : Path
        사용자 데이터 파일 경로 (CSV 또는 pickle)
    output_path : Path, optional
        저장 경로 (없으면 기본 경로 사용)
    format : str, default='csv'
        저장 형식 ('csv' 또는 'pkl')
    
    Returns:
    --------
    Path: 저장된 라벨 파일 경로
    """
    # 사용자 데이터 로드 (CSV 또는 pickle)
    if users_path.suffix == '.csv':
        users = pd.read_csv(users_path)
    else:
        import pickle
        with open(users_path, 'rb') as f:
            users = pickle.load(f)
    
    # 라벨 추출
    labels = LabelLoader.extract_labels(users)
    
    # 저장
    return LabelLoader.save_labels(labels, output_path, format=format)


if __name__ == '__main__':
    """
    사용 예시:
    1. updated_users.pkl에서 라벨 추출하여 저장
    2. 라벨 파일 로드
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Label 파일 관리')
    parser.add_argument(
        '--extract',
        type=str,
        help='사용자 데이터 파일에서 라벨 추출 (예: developer_pool.pkl 또는 developer_pool.csv)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='출력 파일 경로 (기본: libmatch/data/validation_labels.csv)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['csv', 'pkl'],
        default='csv',
        help='저장 형식 (기본: csv)'
    )
    
    args = parser.parse_args()
    
    if args.extract:
        # 라벨 추출
        input_path = Path(args.extract)
        output_path = Path(args.output) if args.output else None
        
        if not input_path.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
            sys.exit(1)
        
        create_label_file_from_users(input_path, output_path, format=args.format)
    else:
        # 라벨 파일 찾기 및 정보 출력
        label_path, labels = LabelLoader.load_labels()
        
        if label_path and labels is not None:
            print(f"✅ 라벨 파일 발견: {label_path}")
            print(f"   - 총 라벨 수: {len(labels)}")
            print(f"   - is_NLP True: {labels['is_NLP'].sum()}")
            print(f"   - is_NLP False: {(~labels['is_NLP']).sum()}")
        else:
            print("❌ 라벨 파일을 찾을 수 없습니다.")
            print("\n사용 방법:")
            print("  python libmatch/devlibmatcher/label_loader.py --extract updated_users.pkl")

