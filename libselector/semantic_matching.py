"""
Section 3.3: Semantic Matching Module
Calculates semantic similarity between job postings and libraries using SentenceBERT.
"""

import pandas as pd
from sentence_transformers import SentenceTransformer, util

from libmatch.config import (
    SENTENCE_BERT_MODEL_PATH,
    LIBRARY_MIN_WEIGHT,
    LIBRARY_MIN_STARS,
    LIBRARY_MIN_FORKS
)
from libmatch.utils import remove_stopwords_from_keywords


class SemanticMatcher:
    """
    Class for calculating semantic similarity using SentenceBERT
    
    Implements semantic matching functionality corresponding to Section 3.3 of the paper.
    """
    
    def __init__(self, model_path: str = None):
        """
        Parameters:
        -----------
        model_path : str, optional
            SentenceBERT model path (default: loaded from config)
        """
        if model_path is None:
            model_path = str(SENTENCE_BERT_MODEL_PATH)
        
        self.model_path = model_path
        print(f"Loading SentenceBERT model from {model_path}...")
        self.model = SentenceTransformer(model_path)
        print("SentenceBERT model loaded successfully")
    
    def encode_text(self, text: str):
        """
        Convert text to embedding vector
        
        Parameters:
        -----------
        text : str
            Text to embed
        
        Returns:
        --------
        numpy.ndarray : Embedding vector
        """
        return self.model.encode(text)
    
    def calculate_cosine_similarity(self, embedding1, embedding2) -> float:
        """
        Calculate cosine similarity between two embedding vectors
        
        Parameters:
        -----------
        embedding1 : numpy.ndarray
            First embedding vector
        embedding2 : numpy.ndarray
            Second embedding vector
        
        Returns:
        --------
        float : Cosine similarity (0~1)
        """
        return float(util.cos_sim(embedding1, embedding2))
    
    def match_libraries_with_job_posting(self, df_lib: pd.DataFrame, 
                                        job_keywords: str) -> pd.DataFrame:
        """
        Calculate similarity between libraries and job posting keywords
        
        Parameters:
        -----------
        df_lib : pd.DataFrame
            Library information DataFrame (requires name, keywords, stars, forks columns)
        job_keywords : str
            Keyword string extracted from job posting
        
        Returns:
        --------
        pd.DataFrame : Library DataFrame with cosine similarity added
        """
        print("Calculating semantic similarity between libraries and job posting...")
        
        # Generate job posting embedding
        embeddings_job = self.encode_text(job_keywords)
        
        # Remove stopwords
        df_lib = df_lib.copy()
        df_lib['keywords'] = df_lib['keywords'].apply(remove_stopwords_from_keywords)
        
        # Calculate weight and filter
        df_lib['weight'] = df_lib['forks'] + df_lib['stars']
        df_lib = df_lib[
            (df_lib['weight'] > LIBRARY_MIN_WEIGHT) &
            (df_lib['stars'] >= LIBRARY_MIN_STARS) &
            (df_lib['forks'] >= LIBRARY_MIN_FORKS)
        ]
        
        # Select necessary columns (stars, forks, weight 포함)
        # 논문 Section 3.2.3에 따라 stars+forks >= 100 필터링된 라이브러리 정보 포함
        columns_to_select = ['name', 'keywords']
        for col in ['stars', 'forks', 'weight']:
            if col in df_lib.columns:
                columns_to_select.append(col)
        df_lib = df_lib[columns_to_select].copy()
        
        # Calculate cosine similarity
        print("Calculating cosine similarity for each library...")
        df_lib['cos_sim'] = df_lib['keywords'].map(
            lambda x: round(
                float(util.cos_sim(
                    self.encode_text(' '.join(x)),
                    embeddings_job
                )), 4
            )
        )
        
        # Clean names and remove duplicates
        df_lib['name'] = df_lib['name'].map(lambda x: x.split(".")[0])
        df_lib = df_lib.drop_duplicates(subset=['name']).sort_values(
            by='cos_sim', ascending=False
        ).reset_index(drop=True)
        
        print(f"Matched {len(df_lib)} unique libraries")
        return df_lib
    
    def lib2descript(self, library_list: list, embeddings_job, df_lib: pd.DataFrame = None) -> list:
        """
        Calculate similarity between library list and job posting embedding (legacy function)
        
        Parameters:
        -----------
        library_list : list
            List of library names
        embeddings_job : numpy.ndarray
            Job posting embedding vector
        df_lib : pd.DataFrame, optional
            Library DataFrame (if None, loads from MongoDB or local file)
        
        Returns:
        --------
        list : List of (library_name, similarity) tuples (sorted by similarity descending)
        """
        if df_lib is None:
            # Try to load from local file first
            from libmatch.devlibscraper.data_collection import GitHubDataCollector
            collector = GitHubDataCollector()
            df_lib = collector.load_libraries()
        
        dict_lib = {}
        for lib in library_list:
            # Search in DataFrame
            matches = df_lib[df_lib['search_word'] == lib]
            if not matches.empty:
                temp = matches.iloc[0]
                if 'description' in temp and pd.notna(temp['description']):
                    embeddings_lib = self.encode_text(temp['description'])
                    cosine_score = self.calculate_cosine_similarity(embeddings_job, embeddings_lib)
                    dict_lib[lib] = round(cosine_score, 4)
        
        # Sort by similarity
        dict_lib = sorted(dict_lib.items(), key=lambda item: item[1], reverse=True)
        return dict_lib

