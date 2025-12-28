# LibMatch: Automating Talent Acquisition for Competent Developers

Python package implementing the LibMatch approach for proactive talent acquisition by matching job descriptions with developer libraries using KeyBERT and SentenceBERT.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Validation

The package includes pre-computed data files for validation. Run the validation pipeline:

```bash
python libmatch/devlibmatcher/pipeline.py --use-library-ranking-csv --use-anonymized
```

Or using Python:

```python
from libmatch.devlibmatcher.pipeline import devlibmatcher

# Run validation with anonymized data
results = devlibmatcher(
    use_library_ranking_csv=True,
    use_anonymized=True
)
```

### 3. Validation Results

Results are saved to:
- `results/validation_results.csv` - Evaluation results for all N and M combinations
- `results/devlibmatcher/evaluation_results.csv` - Detailed evaluation results
- `results/devlibmatcher/filtered_candidates.pkl` - Filtered candidates
- `results/devlibmatcher/classified_candidates.pkl` - Classified candidates (Pioneers, Ambassadors, Potential, Dedicated)

## Data Files

The package includes the following anonymized data files in `libmatch/data/`:
- `library_similarity_ranking.csv` - Pre-computed library similarity ranking
- `developer_pool_anonymized.csv` - Anonymized developer pool data
- `validation_labels_anonymized.csv` - Anonymized validation labels

## Structure

```
libmatch/
├── libselector/          # Phase 1: LibSelector (Section 3.2)
├── devlibscraper/       # Phase 2: DevLibScraper (Section 3.3)
├── devlibmatcher/       # Phase 3: DevLibMatcher (Section 3.4-3.5)
└── data/                # Data files
```

## Paper Reference

This implementation is based on:

> Treasure hunting in the talent ocean: Automating talent acquisition for competent developers from GitHub

The package implements the three-phase approach:
- **Phase 1: LibSelector** - Library selection relevant to job postings
- **Phase 2: DevLibScraper** - Developer identification using selected libraries
- **Phase 3: DevLibMatcher** - Candidate selection and classification
