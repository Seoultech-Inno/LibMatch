"""
Section 3.2.1: SentenceBERT Fine-tuning Module

Fine-tunes SentenceBERT model using library description-keyword pairs.
This module implements the fine-tuning process described in Section 3.2.1 of the paper.

The fine-tuning uses:
- Base Model: all-mpnet-base-v2
- Training Data: Library description-keyword pairs from Libraries.io (4,469 pairs)
- Loss Function: CosineSimilarityLoss
- Hyperparameters: batch_size=16, epochs=2, learning_rate=2e-5, warmup_steps=100
"""

import os
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

from libmatch.config import (
    DATA_DIR,
    PROJECT_ROOT
)


def load_training_data_from_csv(csv_path: Union[str, Path]) -> List[InputExample]:
    """
    Load training data from CSV file
    
    Parameters:
    -----------
    csv_path : Union[str, Path]
        Path to CSV file with columns: name, description, keywords
        
    Returns:
    --------
    List[InputExample] : List of training examples
    """
    df = pd.read_csv(csv_path)
    
    train_examples = []
    for _, row in df.iterrows():
        description = str(row['description']).strip()
        keywords = str(row['keywords']).strip()
        
        if description and keywords and keywords != '[]':
            # Convert keywords string to comma-separated format if needed
            if keywords.startswith('[') and keywords.endswith(']'):
                # Parse list-like string
                import ast
                try:
                    kw_list = ast.literal_eval(keywords)
                    keywords_str = ', '.join([str(k) for k in kw_list])
                except:
                    keywords_str = keywords
            else:
                keywords_str = keywords
            
            train_examples.append(
                InputExample(
                    texts=[description, keywords_str],
                    label=0.7
                )
            )
    
    return train_examples


def fine_tune_sentencebert(
    base_model_name: str = 'all-mpnet-base-v2',
    training_data: Optional[List[InputExample]] = None,
    training_data_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    batch_size: int = 16,
    epochs: int = 2,
    learning_rate: float = 2e-5,
    warmup_steps: int = 100,
    weight_decay: float = 0.01
) -> SentenceTransformer:
    """
    Fine-tune SentenceBERT model using library description-keyword pairs
    
    This function implements the fine-tuning process described in Section 3.2.1 of the paper.
    
    Parameters:
    -----------
    base_model_name : str
        Base model name (default: 'all-mpnet-base-v2')
    training_data : List[InputExample], optional
        Pre-loaded training data (if None, will load from CSV file)
    training_data_path : Union[str, Path], optional
        Path to CSV file with training data (default: data/finetuning_training_data.csv)
    output_path : Union[str, Path], optional
        Path to save fine-tuned model (default: output/all-mpnet-base-v2-finetuned-stackwiki-accelerate)
    batch_size : int
        Batch size for training (default: 16, as per paper)
    epochs : int
        Number of training epochs (default: 2, as per paper)
    learning_rate : float
        Learning rate (default: 2e-5, as per paper)
    warmup_steps : int
        Number of warmup steps (default: 100, as per paper)
    weight_decay : float
        Weight decay for optimizer (default: 0.01)
        
    Returns:
    --------
    SentenceTransformer : Fine-tuned model
    """
    print("=" * 80)
    print("SentenceBERT Fine-tuning")
    print("=" * 80)
    
    # Load base model
    print(f"\n[Step 1] Loading base model: {base_model_name}")
    model = SentenceTransformer(base_model_name)
    print("✅ Base model loaded successfully")
    
    # Load training data
    print("\n[Step 2] Loading training data...")
    if training_data is None:
        if training_data_path is None:
            # Try default paths
            default_paths = [
                DATA_DIR / 'finetuning_training_data.csv',
                PROJECT_ROOT / 'libmatch' / 'data' / 'finetuning_training_data.csv'
            ]
            training_data_path = None
            for path in default_paths:
                if Path(path).exists():
                    training_data_path = path
                    break
            
            if training_data_path is None:
                raise FileNotFoundError(
                    "Training data file not found. Please provide training_data_path or "
                    "ensure data/finetuning_training_data.csv exists."
                )
        
        print(f"Loading from CSV: {training_data_path}")
        training_data = load_training_data_from_csv(training_data_path)
    
    print(f"✅ Loaded {len(training_data)} training examples")
    
    # Create DataLoader
    print("\n[Step 3] Preparing DataLoader...")
    train_dataloader = DataLoader(
        training_data,
        shuffle=True,
        batch_size=batch_size
    )
    print(f"✅ DataLoader created (batch_size={batch_size})")
    
    # Define loss function
    print("\n[Step 4] Setting up loss function...")
    train_loss = losses.CosineSimilarityLoss(model)
    print("✅ CosineSimilarityLoss configured")
    
    # Fine-tune model
    print("\n[Step 5] Fine-tuning model...")
    print(f"   Epochs: {epochs}")
    print(f"   Learning Rate: {learning_rate}")
    print(f"   Warmup Steps: {warmup_steps}")
    print(f"   Weight Decay: {weight_decay}")
    
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': learning_rate, 'weight_decay': weight_decay},
        show_progress_bar=True
    )
    print("✅ Fine-tuning completed")
    
    # Save model
    if output_path is None:
        output_path = PROJECT_ROOT / 'output' / 'all-mpnet-base-v2-finetuned-stackwiki-accelerate'
    
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[Step 6] Saving fine-tuned model to {output_path}...")
    model.save(str(output_path))
    print("✅ Model saved successfully")
    
    print("\n" + "=" * 80)
    print("Fine-tuning complete!")
    print(f"Model saved to: {output_path}")
    print("=" * 80)
    
    return model


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Fine-tune SentenceBERT model')
    parser.add_argument(
        '--base-model',
        type=str,
        default='all-mpnet-base-v2',
        help='Base model name (default: all-mpnet-base-v2)'
    )
    parser.add_argument(
        '--training-data',
        type=str,
        default=None,
        help='Path to training data CSV file'
    )
    parser.add_argument(
        '--output-path',
        type=str,
        default=None,
        help='Path to save fine-tuned model'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Batch size (default: 16)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=2,
        help='Number of epochs (default: 2)'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=2e-5,
        help='Learning rate (default: 2e-5)'
    )
    parser.add_argument(
        '--warmup-steps',
        type=int,
        default=100,
        help='Warmup steps (default: 100)'
    )
    
    args = parser.parse_args()
    
    fine_tune_sentencebert(
        base_model_name=args.base_model,
        training_data_path=args.training_data,
        output_path=args.output_path,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        warmup_steps=args.warmup_steps
    )

