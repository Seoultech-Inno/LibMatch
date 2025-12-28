"""
Section 3.2: Keyword Extraction Module
Extracts key keywords from job postings using KeyBERT.
"""

from typing import List, Tuple, Union
import pandas as pd
from tqdm import tqdm
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer

from libmatch.config import KEYBERT_MODEL_PATH, KEYBERT_TOP_N, KEYBERT_USE_MMR
from libmatch.utils import remove_stopwords_from_keywords


class KeywordExtractor:
    """
    Class for extracting keywords from text using KeyBERT
    
    Implements keyword extraction functionality corresponding to Section 3.2 of the paper.
    """
    
    def __init__(self, model_path: str = None, top_n: int = None, use_mmr: bool = None):
        """
        Parameters:
        -----------
        model_path : str, optional
            KeyBERT model path (default: loaded from config)
        top_n : int, optional
            Number of keywords to extract (default: loaded from config)
        use_mmr : bool, optional
            Whether to use MMR (default: loaded from config)
        """
        if model_path is None:
            model_path = str(KEYBERT_MODEL_PATH)
        if top_n is None:
            top_n = KEYBERT_TOP_N
        if use_mmr is None:
            use_mmr = KEYBERT_USE_MMR
        
        self.model_path = model_path
        self.top_n = top_n
        self.use_mmr = use_mmr
        
        # Initialize KeyBERT model
        print(f"Loading KeyBERT model from {model_path}...")
        self.kw_model = KeyBERT(model=model_path)
        self.vectorizer = KeyphraseCountVectorizer()
        print("KeyBERT model loaded successfully")
    
    def extract_keywords(self, text: str) -> List[Tuple[str, float]]:
        """
        Extract keywords from a single text
        
        Parameters:
        -----------
        text : str
            Text to extract keywords from
        
        Returns:
        --------
        List[Tuple[str, float]] : List of (keyword, score) tuples
        """
        try:
            keyword_doc = self.kw_model.extract_keywords(
                text,
                vectorizer=self.vectorizer,
                use_mmr=self.use_mmr,
                top_n=self.top_n
            )
            return keyword_doc
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
    
    def extract_keywords_batch(self, texts: List[str]) -> List[List[Tuple[str, float]]]:
        """
        Extract keywords from multiple texts in batch
        
        Parameters:
        -----------
        texts : List[str]
            List of texts to extract keywords from
        
        Returns:
        --------
        List[List[Tuple[str, float]]] : List of keyword lists for each text
        """
        results = []
        for text in tqdm(texts, desc="Extracting keywords"):
            keywords = self.extract_keywords(text)
            results.append(keywords)
        return results
    
    def extract_keywords_from_job_posting(self, job_posting_df: pd.DataFrame, 
                                         text_column: str = 'RQP') -> pd.DataFrame:
        """
        Extract keywords from job posting DataFrame
        
        Parameters:
        -----------
        job_posting_df : pd.DataFrame
            Job posting DataFrame
        text_column : str
            Column name containing text
        
        Returns:
        --------
        pd.DataFrame : DataFrame with keywords added
        """
        print(f"Extracting keywords from {len(job_posting_df)} job postings...")
        
        # Extract keywords
        keywords_list = self.extract_keywords_batch(job_posting_df[text_column].tolist())
        
        # Convert keyword list to string (excluding scores)
        job_posting_df['keyword'] = [
            ', '.join([kw for kw, score in keywords]) 
            for keywords in keywords_list
        ]
        
        # Remove stopwords
        job_posting_df['keyword'] = job_posting_df['keyword'].apply(
            lambda x: ', '.join(remove_stopwords_from_keywords(x.split(', ')))
        )
        
        print("Keyword extraction completed")
        return job_posting_df
    
    def load_job_posting_keywords(self, csv_path: str, index: int = 1, 
                                  keyword_column: str = 'keyword_rd') -> str:
        """
        Load saved job posting keywords
        
        Parameters:
        -----------
        csv_path : str
            Path to CSV file
        index : int
            Row index to load
        keyword_column : str
            Keyword column name
        
        Returns:
        --------
        str : Keyword string
        """
        print(f"Loading job posting keywords from {csv_path}...")
        job_post = pd.read_csv(csv_path, index_col=0)
        kw_job = job_post[keyword_column][index]
        print(f"Job posting keywords loaded: {kw_job[:100]}...")
        return kw_job

