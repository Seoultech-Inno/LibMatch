# Library Data Directory

This directory contains pre-computed data files for validation and reproduction.

## Files

- `library_similarity_ranking.csv` - Pre-computed library similarity ranking (cosine similarity scores)
  - Required for validation pipeline
  - Contains: rank, name, cos_sim, keywords, stars, forks, weight columns
- `developer_pool_anonymized.csv` - Anonymized developer pool data
  - Contains: users, pkgs_used, n_pkgs, type, contribs, followers columns
- `validation_labels_anonymized.csv` - Anonymized validation labels
  - Contains: users, is_NLP columns

## Usage

These files are sufficient to run the validation pipeline:

```bash
python libmatch/devlibmatcher/pipeline.py --use-library-ranking-csv --use-anonymized
```

The validation pipeline will automatically use these files without requiring MongoDB connection.

## File Sizes

These CSV files are included in the repository and are relatively small (few MB). They are version controlled and available for immediate use.

