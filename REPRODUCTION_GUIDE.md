# Paper Reproduction Guide

This guide explains how to reproduce the results from the paper using the LibMatch package.

## Quick Start

### Step 1: Run Validation

The package includes pre-computed data files for validation. Run the validation pipeline:

```python
from libmatch.run_pipeline import run_full_pipeline

# Execute complete pipeline
results = run_full_pipeline()
```

That's it! The pipeline will automatically use local data files instead of MongoDB.

## Required Data Files

### 1. User Data (Section 3.1)
- **File**: `updated_users.pkl`
- **Location**: Project root directory
- **Description**: Pickle file containing GitHub developer data
- **Status**: ✅ Must be present

### 2. Job Posting Data (Section 3.2)
- **File**: `job_posting_update.csv`
- **Location**: Project root directory
- **Description**: CSV file containing job postings with extracted keywords
- **Status**: ✅ Must be present

### 3. Library Similarity Ranking (Section 3.2, 3.3)
- **File**: `libmatch/data/library_similarity_ranking.csv`
- **Location**: `libmatch/data/` directory
- **Description**: Pre-computed library similarity ranking (cosine similarity scores)
- **Status**: ✅ Included in package (no download needed)

### 4. Pre-trained Models (Section 3.2, 3.3)
- **Model Path**: `output/all-mpnet-base-v2-finetuned-stackwiki-accelerate/`
- **Description**: Fine-tuned models for keyword extraction and semantic matching
- **Status**: ✅ Must be present

## Environment Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables (Optional)

Create a `.env` file in the project root (only needed for initial data download):

```bash
# MongoDB Connection (only needed for downloading library data)
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=research
MONGO_COLLECTION_NAME=library

# GitHub API Token (optional, only needed for data collection)
GITHUB_TOKEN=your_github_token_here
```

### 3. Verify Data Files

Run the data verification script:

```python
from libmatch.check_data_requirements import check_data_requirements
check_data_requirements()
```

## Running the Pipeline

### Option 1: Run Full Pipeline

```python
from libmatch.run_pipeline import run_full_pipeline

# Execute complete pipeline
results = run_full_pipeline()
```

This will:
1. Load user data from `updated_users.pkl`
2. Load library data from `libmatch/data/libraries.pkl` (or MongoDB if not available)
3. Load job posting keywords from `job_posting_update.csv`
4. Extract keywords from job postings (if needed)
5. Match libraries with job postings using semantic similarity
6. Rank developer candidates
7. Evaluate performance metrics for all N and M combinations
8. Save results to `results/validation_results.csv`

### Option 2: Run Individual Steps

```python
from libmatch.devlibscraper.data_collection import GitHubDataCollector
from libmatch.libselector.keyword_extraction import KeywordExtractor
from libmatch.libselector.semantic_matching import SemanticMatcher
from libmatch.devlibmatcher.candidate_ranking import CandidateRanker
from libmatch.devlibmatcher.evaluation import Evaluator

# Step 1: Load data
collector = GitHubDataCollector()
users = collector.load_users('updated_users.pkl')
df_lib = collector.load_libraries()  # Automatically uses local data if available

# Step 2: Extract keywords
extractor = KeywordExtractor()
kw_job = extractor.load_job_posting_keywords('job_posting_update.csv', index=1)

# Step 3: Semantic matching
matcher = SemanticMatcher()
df_lib_matched = matcher.match_libraries_with_job_posting(df_lib, kw_job)

# Step 4: Rank candidates
ranker = CandidateRanker()
keyword_list = ranker.get_keyword_list(df_lib_matched, n=100)
filtered_users = ranker.filter_candidates(users, keyword_list, m_val=3)
top_candidates = ranker.get_top_n_candidates(
    ranker.rank_candidates(filtered_users), 
    n=100
)

# Step 5: Evaluate
evaluator = Evaluator()
results = evaluator.evaluate_nm_combinations(users, df_lib_matched)
evaluator.print_results(results)
evaluator.save_results(results)
```

## Expected Output

The pipeline will generate:

1. **Console Output**: 
   - Progress messages for each section
   - Performance metrics (Precision, Recall, F1 Score) for each N and M combination
   - Pivot tables showing results

2. **CSV File**: `results/validation_results.csv`
   - Contains all evaluation results with columns:
     - `N`: Number of libraries
     - `M`: Minimum matching libraries
     - `TP`, `FP`, `FN`, `TN`: Confusion matrix components
     - `Precision`, `Recall`, `F1 Score`: Performance metrics
     - `Selected Users`: Number of selected candidates

## Reproducing Specific Results

### To reproduce validation results (N and M combinations):

```python
from libmatch.devlibmatcher.evaluation import Evaluator
from libmatch.devlibscraper.data_collection import GitHubDataCollector
from libmatch.libselector.keyword_extraction import KeywordExtractor
from libmatch.libselector.semantic_matching import SemanticMatcher

# Load data
collector = GitHubDataCollector()
users = collector.load_users('updated_users.pkl')
df_lib = collector.load_libraries()  # Uses local data automatically

extractor = KeywordExtractor()
kw_job = extractor.load_job_posting_keywords('job_posting_update.csv', index=1)

matcher = SemanticMatcher()
df_lib_matched = matcher.match_libraries_with_job_posting(df_lib, kw_job)

# Evaluate with default N and M values
evaluator = Evaluator()
results = evaluator.evaluate_nm_combinations(users, df_lib_matched)
evaluator.print_results(results)
evaluator.save_results(results)
```

### To reproduce candidate ranking for specific N and M:

```python
from libmatch.candidate_ranking import CandidateRanker

ranker = CandidateRanker()
keyword_list = ranker.get_keyword_list(df_lib_matched, n=100)  # N=100
filtered_users = ranker.filter_candidates(users, keyword_list, m_val=3)  # M=3
top_candidates = ranker.get_top_n_candidates(
    ranker.rank_candidates(filtered_users), 
    n=100
)
```

## Data Management

### Downloading Library Data

To download library data from MongoDB (one-time setup):

The package includes pre-computed `library_similarity_ranking.csv` file which is sufficient for validation.

For running the full pipeline from scratch (Phase 1-3), you would need MongoDB access, but this is not required for validation.

## Troubleshooting

### Issue: Library Data File Not Found
**Solution**: 
- Verify `libmatch/data/library_similarity_ranking.csv` exists
- This file is included in the package and should be present

### Issue: MongoDB Connection Error (during download)
**Solution**: 
- Check MongoDB URI in `.env` file or `config.py`
- Verify network connectivity
- Ensure MongoDB Atlas IP whitelist includes your IP

### Issue: Model Not Found
**Solution**:
- Verify model files exist in `output/all-mpnet-base-v2-finetuned-stackwiki-accelerate/`
- Check that all required files are present:
  - `config.json`
  - `model.safetensors` or `pytorch_model.bin`
  - `tokenizer.json`
  - `vocab.txt`

### Issue: File Not Found Error
**Solution**:
- Verify `updated_users.pkl` exists in project root
- Verify `job_posting_update.csv` exists in project root
- Run `check_data_requirements()` to verify all files

### Issue: Memory Error
**Solution**:
- Reduce batch size in keyword extraction
- Process data in chunks
- Use GPU if available for model inference

## Data Requirements Summary

| Component | Data Source | Required | Status |
|-----------|-------------|----------|--------|
| User Data | `updated_users.pkl` | ✅ Yes | ✅ Must be present |
| Job Postings | `job_posting_update.csv` | ✅ Yes | ✅ Must be present |
| Library Data | `libmatch/data/libraries.pkl` | ✅ Yes | ⚠️ Download once |
| KeyBERT Model | `output/.../` | ✅ Yes | ✅ Must be present |
| SentenceBERT Model | `output/.../` | ✅ Yes | ✅ Must be present |

## Notes

- **No MongoDB connection required** for validation. Pre-computed data files are included.
- The anonymized data files (`developer_pool_anonymized.csv`, `validation_labels_anonymized.csv`) are included for immediate use.
- Library similarity ranking (`library_similarity_ranking.csv`) is pre-computed and ready to use.
- All required data files are included in the repository.

## Complete Reproduction Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify library similarity ranking CSV exists: `libmatch/data/library_similarity_ranking.csv`
- [ ] Verify data files: `python libmatch/check_data_requirements.py`
- [ ] Run pipeline: `python libmatch/run_pipeline.py` or `from libmatch.run_pipeline import run_full_pipeline; run_full_pipeline()`
- [ ] Check results: `results/validation_results.csv`
