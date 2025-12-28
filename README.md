# LibMatch: Automating Talent Acquisition for Competent Developers

Python package implementing the LibMatch approach for proactive talent acquisition by matching job descriptions with developer libraries using KeyBERT and SentenceBERT.

## Structure

This package is organized according to the Method section structure of the paper, which is divided into 3 main steps:

```
libmatch/
├── __init__.py                          # Package initialization
├── config.py                             # Configuration file
├── utils.py                              # Common utility functions
├── visualization.py                      # Visualization utilities
├── run_pipeline.py                       # Full pipeline runner (3 phases)
├── check_data_requirements.py           # Script to verify data availability
├── libselector/                          # Phase 1: LibSelector (Section 3.2)
│   ├── __init__.py
│   ├── pipeline.py                        # Phase 1 pipeline
│   ├── keyword_extraction.py             # Section 3.2.1: Keyword Extraction (KeyBERT)
│   ├── semantic_matching.py              # Section 3.2.3: Library Selection (SentenceBERT)
│   └── outputs.py                         # Phase 1 output definitions
├── devlibscraper/                        # Phase 2: DevLibScraper (Section 3.3)
│   ├── __init__.py
│   ├── pipeline.py                        # Phase 2 pipeline
│   ├── data_collection.py                # Section 3.3.1-3.3.2: Developer Pooling & Library Extraction
│   └── outputs.py                         # Phase 2 output definitions
├── devlibmatcher/                        # Phase 3: DevLibMatcher (Section 3.4-3.5)
│   ├── __init__.py
│   ├── pipeline.py                        # Phase 3 pipeline
│   ├── candidate_ranking.py              # Section 3.4.1: Library Matching
│   ├── evaluation.py                     # Section 3.5: Evaluation and Validation
│   ├── label_loader.py                   # Label loading utilities
│   ├── check_validation_requirements.py  # Validation data checker
│   └── outputs.py                         # Phase 3 output definitions
├── data/                                 # Local data directory
│   ├── README.md                         # Data directory documentation
│   ├── library_similarity_ranking.csv   # Pre-computed library similarity ranking
│   ├── developer_pool_anonymized.csv     # Anonymized developer pool data
│   └── validation_labels_anonymized.csv  # Anonymized validation labels
├── README.md                             # This file
├── REPRODUCTION_GUIDE.md                 # Paper reproduction guide
└── VERIFICATION_REPORT.md                # Code-paper alignment verification report
```

### Pipeline Structure

The Method section is organized into 3 phases according to the paper (Section 3.1 Overall framework):

1. **Phase 1: LibSelector** - Library selection relevant to job postings
   - KeyBERT algorithm extracts essential keywords from job postings
   - Libraries.io API gathers information about related libraries
   - SentenceBERT selects libraries highly related to job postings

2. **Phase 2: DevLibScraper** - Developer identification using selected libraries
   - GitHub API collects developer profiles and library usage data
   - Regular expressions extract libraries developers use from their code

3. **Phase 3: DevLibMatcher** - Candidate selection and classification
   - Identifies "overlap libraries" between LibSelector's libraries and developer's libraries
   - Counts shared libraries to select potential candidates
   - Classifies candidates using GitHub metrics (contributions, followers, etc.)

## GitHub Repository Setup

This package is ready for GitHub upload.

### Important Notes for GitHub Upload

1. **Sensitive Information Removed**: MongoDB URI in `config.py` is only set via environment variables.
2. **Large Files Excluded**: The following files are excluded by `.gitignore`:
   - `data/*.pkl`, `data/*.json`, `data/*.csv` (data files)
   - `model/` (model files)
   - `results/` (execution results)
   - `__pycache__/` (Python cache)

3. **Required Files**: The following files are included in GitHub:
   - All Python source code (`.py` files)
   - Documentation files (`README.md`, `REPRODUCTION_GUIDE.md`, etc.)
   - `data/README.md` (data directory documentation)

### Environment Setup for Users

For validation, no environment variables are required. The included data files are sufficient.

If you need to run the full pipeline from scratch (Phase 1-3), you may need:

```bash
# MongoDB connection (only if running LibSelector from scratch)
export MONGO_URI="your_mongodb_uri"
export MONGO_DB_NAME="research"
export MONGO_COLLECTION_NAME="library"

# GitHub API token (only if running DevLibScraper from scratch)
export GITHUB_TOKEN="your_github_token"
```

Or create a `.env` file (`.env` is included in `.gitignore`).

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Data Files

The package includes pre-computed data files in `libmatch/data/`:
- `library_similarity_ranking.csv` - Library similarity ranking (required for validation)
- `developer_pool_anonymized.csv` - Anonymized developer pool data
- `validation_labels_anonymized.csv` - Anonymized validation labels

These files are sufficient to run the validation pipeline.

### 3. Run the Pipeline

**Option 1: Run full pipeline (all 3 steps)**
```python
from libmatch.run_pipeline import run_full_pipeline
results = run_full_pipeline()
```

**Option 2: Run step by step**
```bash
# Phase 1: LibSelector
python libmatch/libselector/pipeline.py

# Phase 2: DevLibScraper
python libmatch/devlibscraper/pipeline.py

# Phase 3: DevLibMatcher
python libmatch/devlibmatcher/pipeline.py
```

**Option 3: Import and use**
```python
from libmatch.libselector.pipeline import libselector
from libmatch.devlibscraper.pipeline import devlibscraper
from libmatch.devlibmatcher.pipeline import devlibmatcher

# Phase 1
df_lib_matched = libselector()

# Phase 2
users = devlibscraper()

# Phase 3
results = devlibmatcher(users=users, df_lib_matched=df_lib_matched)
```

**Option 3: Import and run**
```python
from libmatch.run_pipeline import run_full_pipeline
results = run_full_pipeline()
```

## Phase Outputs

Output results from each phase are saved in the `results/` directory. For detailed information, see [OUTPUTS_DOCUMENTATION.md](OUTPUTS_DOCUMENTATION.md).

### Phase 1: LibSelector Outputs
- **3.2.1 Keyword Extraction**: `results/libselector/extracted_keywords.pkl` - Extracted keyword list
- **3.2.2 Keyword Conversion**: `results/libselector/library_database.pkl` - Structured library database
- **3.2.3 Library Selection**: `results/libselector/selected_libraries.pkl` - Top N selected libraries (stars+forks >= 100)

### Phase 2: DevLibScraper Outputs
- **3.3.1 Developer Pooling**: `results/devlibscraper/developer_pool.pkl` - Developer pool (with metrics)
- **3.3.2 Library Extraction**: `results/devlibscraper/developer_library_mapping.pkl` - Developer-library mapping

### Phase 3: DevLibMatcher Outputs
- **3.4.1 Library Matching**: `results/devlibmatcher/filtered_candidates.pkl` - Candidates with M or more overlap libraries
- **3.4.2 Developer Classification**: `results/devlibmatcher/classified_candidates.pkl` - Classified candidates (Pioneers, Ambassadors, Potential, Dedicated)
- **3.5 Evaluation**: `results/devlibmatcher/evaluation_results.csv` - Evaluation results

## Module Descriptions

### Phase 1: LibSelector (Section 3.2)

#### Section 3.2.1: Keyword Extraction (`libselector/keyword_extraction.py`)
- **KeywordExtractor**: Extracts key keywords from job postings using KeyBERT
  - Uses fine-tuned "all-mpnet-base-v2" model
  - Applies stopwords filtering

#### Section 3.2.2: Keyword Conversion
- Library database construction (handled via `library_similarity_ranking.csv`)
- Libraries.io API integration (data pre-computed)

#### Section 3.2.3: Library Selection (`libselector/semantic_matching.py`)
- **SemanticMatcher**: Selects libraries using SentenceBERT cosine similarity
  - Filters libraries with stars + forks >= 100
  - Selects top N libraries based on similarity scores

### Phase 2: DevLibScraper (Section 3.3)

#### Section 3.3.1: Developer Pooling (`devlibscraper/data_collection.py`)
- **GitHubDataCollector**: Collects developer data from GitHub
  - Uses GitHub API to find developers
  - Filters by Contributed Repos Stars Count (i) and Followers Count (j)
  - Supports Target Language filtering

#### Section 3.3.2: Library Extraction (`devlibscraper/data_collection.py`)
- **GitHubDataCollector**: Extracts libraries from developer code
  - Prioritizes setup.py and requirements.txt files
  - Uses regex patterns to extract Python import statements
  - Excludes forked repositories

### Phase 3: DevLibMatcher (Section 3.4-3.5)

#### Section 3.4.1: Library Matching (`devlibmatcher/candidate_ranking.py`)
- **CandidateRanker**: Matches developers based on overlap libraries
  - Counts overlap libraries (M value)
  - Filters candidates with M or more matching libraries

#### Section 3.4.2: Developer Classification (`devlibmatcher/pipeline.py`)
- Classifies candidates into 4 types using median values:
  - **Pioneers**: High contributions + High followers
  - **Ambassadors**: Low contributions + High followers
  - **Potential**: Low contributions + Low followers
  - **Dedicated**: High contributions + Low followers

#### Section 3.5: Evaluation (`devlibmatcher/evaluation.py`)
- **Evaluator**: Evaluates system performance
  - Calculates Precision, Recall, F1 Score
  - Tests multiple N and M value combinations
  - `extract_keywords()`: Extract keywords from single text
  - `extract_keywords_batch()`: Extract keywords from multiple texts
  - `extract_keywords_from_job_posting()`: Extract keywords from job posting DataFrame

### Section 3.3: Semantic Matching (`semantic_matching.py`)

- **SemanticMatcher**: Calculates semantic similarity using SentenceBERT
  - `match_libraries_with_job_posting()`: Calculate similarity between libraries and job posting
  - `calculate_cosine_similarity()`: Calculate cosine similarity

### Section 3.4: Candidate Ranking (`candidate_ranking.py`)

- **CandidateRanker**: Filters and ranks developer candidates
  - `get_keyword_list()`: Generate library keyword list according to N value
  - `filter_candidates()`: Filter developer candidates
  - `rank_candidates()`: Rank filtered candidates

### Section 3.5: Evaluation and Validation (`evaluation.py`)

- **Evaluator**: Evaluates performance of developer candidate recommendation system
  - `calculate_metrics()`: Calculate performance metrics (Precision, Recall, F1 Score)
  - `evaluate_nm_combinations()`: Measure performance for N and M value combinations
  - `print_results()`: Print results

## Usage Examples

### Basic Usage

```python
from libmatch.devlibscraper.data_collection import GitHubDataCollector
from libmatch.libselector.keyword_extraction import KeywordExtractor
from libmatch.libselector.semantic_matching import SemanticMatcher
from libmatch.devlibmatcher.candidate_ranking import CandidateRanker
from libmatch.devlibmatcher.evaluation import Evaluator

# 1. Data collection
collector = GitHubDataCollector()
users = collector.load_users('updated_users.pkl')
df_lib = collector.load_libraries()  # Uses local data if available

# 2. Keyword extraction
extractor = KeywordExtractor()
kw_job = extractor.load_job_posting_keywords('job_posting_update.csv', index=1)

# 3. Semantic matching
matcher = SemanticMatcher()
df_lib_matched = matcher.match_libraries_with_job_posting(df_lib, kw_job)

# 4. Candidate ranking
ranker = CandidateRanker()
keyword_list = ranker.get_keyword_list(df_lib_matched, n=100)
filtered_users = ranker.filter_candidates(users, keyword_list, m_val=3)
top_candidates = ranker.get_top_n_candidates(
    ranker.rank_candidates(filtered_users), 
    n=100
)

# 5. Evaluation
evaluator = Evaluator()
results = evaluator.evaluate_nm_combinations(users, df_lib_matched)
evaluator.print_results(results)
```

### Check Data Requirements

```python
from libmatch.check_data_requirements import check_data_requirements

# Verify all required data is available
check_data_requirements()
```

## Configuration

Edit `config.py` to change settings:

- **GitHub API**: Set `GITHUB_TOKEN` environment variable
- **MongoDB**: Set `MONGO_URI`, `MONGO_DB_NAME`, `MONGO_COLLECTION_NAME` (only needed for initial download)
- **Model paths**: `KEYBERT_MODEL_PATH`, `SENTENCE_BERT_MODEL_PATH`
- **Parameters**: `KEYBERT_TOP_N`, `LIBRARY_MIN_WEIGHT`, `DEFAULT_N_VALUES`, `DEFAULT_M_VALUES`
- **Local data**: Set `USE_LOCAL_DATA=True` to prefer local files over MongoDB

## Data Files

### Required Files (in project root)

- `updated_users.pkl` - GitHub developer data
- `job_posting_update.csv` - Job posting data with keywords

### Optional Files (downloaded automatically)

- `libmatch/data/libraries.pkl` - Library data (downloaded from MongoDB)
- `libmatch/data/libraries.json` - Library data (JSON format)
- `libmatch/data/libraries.csv` - Library data (CSV format)

## Requirements

See `requirements.txt` for full list. Main dependencies:

- `sentence-transformers`: SentenceBERT model
- `keybert`: KeyBERT keyword extraction
- `pymongo`: MongoDB connection (only needed for initial download)
- `pandas`: Data processing
- `github`: GitHub API (only needed for data collection)

## Paper Reference

This implementation is based on the Method section of:

> Treasure hunting in the talent ocean: Automating talent acquisition for competent developers from GitHub

Each module implements the corresponding section:
- Section 3.1: Data collection and preprocessing
- Section 3.2: Keyword extraction (KeyBERT)
- Section 3.3: Semantic matching (SentenceBERT)
- Section 3.4: Candidate ranking
- Section 3.5: Evaluation and validation

## Documentation

- `REPRODUCTION_GUIDE.md` - Detailed guide for reproducing paper results
- `MIGRATION_CHECKLIST.md` - Checklist of migrated code from original notebooks
