# LibMatch: Automated Talent Acquisition from GitHub

> LibMatch is an AI-powered framework for proactive talent acquisition that
> identifies qualified developers for a given job posting by matching job
> requirements with technology libraries used by GitHub developers.

**Annals of Data Science, 2026**

[Paper](https://doi.org/10.1007/s40745-026-00705-4) ·
[Installation](#installation) ·
[Usage](#usage) ·
[Citation](#citation)

Python package implementing LibMatch for developer talent acquisition by matching job descriptions with developer libraries using KeyBERT and SentenceBERT.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Validation

```bash
python libmatch/devlibmatcher/pipeline.py --use-library-ranking-csv --use-anonymized
```

Or using Python:

```python
from libmatch.devlibmatcher.pipeline import devlibmatcher

results = devlibmatcher(
    use_library_ranking_csv=True,
    use_anonymized=True
)
```

## Data Files

The package includes anonymized data files in `libmatch/data/`:
- `library_similarity_ranking.csv` - Pre-computed library similarity ranking
- `developer_pool_anonymized.csv` - Anonymized developer pool data
- `validation_labels_anonymized.csv` - Anonymized validation labels
- `finetuning_training_data.csv` - Training data for fine-tuning (4,471 library description-keyword pairs)
- `ToolBERT.csv` - StackShare.io tool data (2,237 entries)

## Model

Fine-tuned SentenceBERT model is included in `libmatch/model/`:
- `all-mpnet-base-v2-finetuned-stackwiki-accelerate/` - Fine-tuned model (418MB, tracked via Git LFS)

## Structure

```
libmatch/
├── libselector/          # Phase 1: LibSelector
├── devlibscraper/       # Phase 2: DevLibScraper
├── devlibmatcher/       # Phase 3: DevLibMatcher
├── data/                # Data files
└── model/               # Fine-tuned model
```

## Fine-tuning

To fine-tune your own SentenceBERT model:

```python
from libmatch.libselector.fine_tuning import fine_tune_sentencebert

fine_tune_sentencebert(
    training_data_path='libmatch/data/finetuning_training_data.csv',
    output_path='output/my-model'
)
```

## Paper Reference

> Treasure hunting in the talent ocean: Automating talent acquisition for competent developers from GitHub

This implementation follows the three-phase approach:
- **Phase 1: LibSelector** - Library selection relevant to job postings
- **Phase 2: DevLibScraper** - Developer identification using selected libraries
- **Phase 3: DevLibMatcher** - Candidate selection and classification

@article{kim2026libmatch,
  title   = {Treasure Hunting in the Talent Ocean: Automating Talent Acquisition for Competent Developers from GitHub},
  author  = {Kim, Minchan and Lee, Hakyeon},
  journal = {Annals of Data Science},
  year    = {2026},
  doi     = {10.1007/s40745-026-00705-4}
}
