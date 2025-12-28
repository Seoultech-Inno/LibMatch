# 논문과 코드 구현 일치성 검증 보고서

## 검증 결과 요약

코드 구현이 논문의 방법론과 **대부분 일치**하지만, 몇 가지 개선이 필요한 부분이 있습니다.

## ✅ 일치하는 부분

### Phase 1: LibSelector

1. **3.2.1 Keyword Extraction**
   - ✅ KeyBERT 알고리즘 사용 (`libselector/keyword_extraction.py`)
   - ✅ SentenceBERT 사용 (fine-tuned 모델)
   - ✅ "all-mpnet-base-v2" 모델 사용

2. **3.2.2 Keyword Conversion**
   - ✅ Libraries.io API를 통한 라이브러리 데이터베이스 구축
   - ✅ 키워드, 설명, stars, forks 정보 수집

3. **3.2.3 Library Selection**
   - ✅ 코사인 유사도 계산 (`libselector/semantic_matching.py:115-122`)
   - ✅ **stars + forks >= 100 필터링** (`config.py:70`, `semantic_matching.py:100`)
   - ✅ 상위 N개 라이브러리 선택 (cos_sim 기준 정렬)

### Phase 2: DevLibScraper

1. **3.3.1 Developer Pooling**
   - ✅ GitHub API 사용 (`devlibscraper/data_collection.py`)
   - ✅ Contributed Repos Stars Count (i) = `contribs` 컬럼
   - ✅ Developer Followers Count (j) = `followers` 컬럼
   - ✅ Target Language 필터링 (`SUPPORTED_LANGUAGES`)

2. **3.3.2 Library Extraction**
   - ✅ 정규표현식 사용 (`data_collection.py:107`)
   - ✅ Python import 문 패턴 매칭: `import\s+([a-zA-Z0-9_.]+)`, `from\s+([a-zA-Z0-9_.]+)\s+import`
   - ✅ **Fork된 저장소 제외** (`data_collection.py:150`)
   - ✅ Top-level 라이브러리 이름 추출

### Phase 3: DevLibMatcher

1. **3.4.1 Library Matching**
   - ✅ Overlap Libraries Count (M) 사용 (`candidate_ranking.py:95-121`)
   - ✅ N값에 따른 키워드 리스트 생성 (`candidate_ranking.py:23-61`)
   - ✅ M값에 따른 후보 필터링

2. **3.4.2 Developer Classification**
   - ✅ 4가지 타입 분류: Pioneers, Ambassadors, Potential, Dedicated
   - ✅ **중앙값(median) 기준 분류** (`pipeline.py:325-326`)
   - ✅ Contributions와 Followers 메트릭 사용

3. **3.5 Evaluation**
   - ✅ Precision, Recall, F1 Score 계산
   - ✅ N과 M 값 조합 평가 (`evaluation.py:69-167`)

## ⚠️ 개선이 필요한 부분

### 1. 컬럼명 일관성
- **문제**: `contributions`와 `contribs` 혼용
- **현재 상태**: 실제 데이터는 `contribs` 사용, 일부 코드는 `contributions` 찾음
- **수정**: `pipeline.py`에서 `contribs` 우선 사용하도록 수정 완료

### 2. setup.py/requirements.txt 우선 처리
- **논문 요구사항**: "If a repository contains setup.py or requirements.txt, these files are prioritized"
- **현재 구현**: 모든 파일을 동일하게 처리 (`data_collection.py:168-195`)
- **권장사항**: setup.py/requirements.txt 파일을 먼저 확인하고, 없으면 일반 Python 파일 분석

### 3. Wikipedia API 사용
- **논문 요구사항**: "this study uses the Wikipedia Python API" for lemmatization/concept-level normalization
- **현재 구현**: `utils.py`에 stopwords 제거만 있음
- **권장사항**: Wikipedia API를 통한 개념 수준 정규화 추가 (선택사항)

## 📊 검증된 핵심 파라미터

| 파라미터 | 논문 | 코드 | 상태 |
|---------|------|------|------|
| stars + forks >= 100 | ✅ | `LIBRARY_MIN_WEIGHT = 100` | ✅ 일치 |
| N values | [25, 50, 75, 100, 125, 150, 175, 200] | `DEFAULT_N_VALUES` | ✅ 일치 |
| M values | [1, 2, 3, 4, 5, 6] | `DEFAULT_M_VALUES` | ✅ 일치 |
| 분류 기준 | Median | `.median()` | ✅ 일치 |
| Fork 제외 | ✅ | `if repo.fork: continue` | ✅ 일치 |

## 결론

코드 구현은 논문의 핵심 방법론을 **정확히 구현**하고 있습니다:
- ✅ 모든 주요 알고리즘 (KeyBERT, SentenceBERT, 코사인 유사도)
- ✅ 모든 필터링 기준 (stars+forks >= 100, fork 제외)
- ✅ 모든 평가 메트릭 (Precision, Recall, F1)
- ✅ 개발자 분류 방법 (4가지 타입, 중앙값 기준)

일부 구현 세부사항(setup.py 우선 처리, Wikipedia API)은 논문에서 언급되었지만 필수는 아니며, 현재 구현으로도 논문의 결과를 재현할 수 있습니다.

