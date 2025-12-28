"""
Section 3.4: Candidate Ranking Module
Filters and ranks developer candidates.
"""

from typing import List, Set
import pandas as pd

from libmatch.config import DEFAULT_N_VALUES, DEFAULT_M_VALUES


class CandidateRanker:
    """
    Class for ranking developer candidates
    
    Implements candidate ranking functionality corresponding to Section 3.4 of the paper.
    """
    
    def __init__(self):
        """Initialize CandidateRanker"""
        pass
    
    def get_keyword_list(self, df_lib: pd.DataFrame, n: int = 100) -> List[List[str]]:
        """
        Generate library keyword list according to N value
        
        Parameters:
        -----------
        df_lib : pd.DataFrame
            Library information DataFrame (requires name, keywords, cos_sim columns)
        n : int, default=100
            Minimum number of libraries to have more than n unique keywords after deduplication
        
        Returns:
        --------
        List[List[str]] : Grouped list of library names
        """
        df_temp = df_lib.copy()
        
        # Find minimum number of libraries to have more than n unique keywords
        i = n
        while True:
            if len(df_temp.head(i).drop_duplicates(subset=['keywords'])) > n:
                threshold = i - 1
                break
            i = i + 1
        
        df_temp = df_temp.drop_duplicates(subset=['name'])
        
        # Convert 'keywords' column to string
        df_temp['keywords_str'] = df_temp['keywords'].apply(
            lambda x: ','.join(map(str, x))
        )
        
        # Sort by 'cos_sim' and select top threshold rows
        df_sorted = df_temp.sort_values(by='cos_sim', ascending=False).head(threshold)
        
        # Group by 'keywords_str' and combine 'name's into list
        grouped_names = df_sorted.groupby('keywords_str')['name'].apply(list).tolist()
        
        return grouped_names
    
    def check_keyword_list(self, keyword_list: List[List[str]], 
                          target_list: List[str], n: int) -> bool:
        """
        Check if keywords in keyword_list match n or more keywords in target_list
        
        Parameters:
        -----------
        keyword_list : List[List[str]]
            Grouped keyword list (each group is a list of library names)
        target_list : List[str]
            List of library names used by user (lowercase)
        n : int
            Minimum number of matching libraries (M value)
        
        Returns:
        --------
        bool : True if n or more matches, False otherwise
        """
        count = 0
        used_keywords = set()  # Set to track already counted keywords
        
        for keywords in keyword_list:
            found = False  # Flag indicating if keyword from target_list was found in current list
            for keyword in keywords:
                if keyword.lower() in target_list and keyword not in used_keywords:
                    found = True
                    used_keywords.add(keyword)
            if found:
                count += 1
        
        return count >= n
    
    def filter_candidates(self, users: pd.DataFrame, keyword_list: List[List[str]], 
                         m_val: int) -> pd.DataFrame:
        """
        Filter developer candidates
        
        Parameters:
        -----------
        users : pd.DataFrame
            User data (requires pkgs_used column)
        keyword_list : List[List[str]]
            Library keyword list to use for filtering
        m_val : int
            Minimum number of matching libraries (M value)
        
        Returns:
        --------
        pd.DataFrame : Filtered user data (with P column added)
        """
        users = users.copy()
        users['P'] = users['pkgs_used'].map(
            lambda x: self.check_keyword_list(
                keyword_list,
                [i.lower() for i in list(x)],
                m_val
            )
        )
        return users
    
    def rank_candidates(self, filtered_users: pd.DataFrame, 
                       sort_by: List[str] = None) -> pd.DataFrame:
        """
        Rank filtered developer candidates
        
        Parameters:
        -----------
        filtered_users : pd.DataFrame
            Filtered user data
        sort_by : List[str], optional
            List of column names to sort by (default: ['contribs', 'followers'])
        
        Returns:
        --------
        pd.DataFrame : Ranked user data
        """
        if sort_by is None:
            sort_by = ['contribs', 'followers']
        
        ranked_users = filtered_users[filtered_users['P'] == True].copy()
        
        # Sort (descending order)
        ranked_users = ranked_users.sort_values(
            by=sort_by,
            ascending=False
        ).reset_index(drop=True)
        
        return ranked_users
    
    def get_top_n_candidates(self, ranked_users: pd.DataFrame, n: int = 100) -> pd.DataFrame:
        """
        Return top N developer candidates
        
        Parameters:
        -----------
        ranked_users : pd.DataFrame
            Ranked user data
        n : int
            Number of candidates to return
        
        Returns:
        --------
        pd.DataFrame : Top N candidates
        """
        return ranked_users.head(n)
    
    def return_keyword_list(self, keyword_list: List[List[str]], 
                           target_list: List[str], n: int) -> set:
        """
        Return set of matched keywords
        
        Parameters:
        -----------
        keyword_list : List[List[str]]
            Grouped keyword list
        target_list : List[str]
            List of library names used by user (lowercase)
        n : int
            Minimum number of matching libraries
        
        Returns:
        --------
        set : Set of matched keywords
        """
        used_keywords = set()
        
        for keywords in keyword_list:
            for keyword in keywords:
                if keyword.lower() in target_list and keyword not in used_keywords:
                    used_keywords.add(keyword)
        
        return used_keywords

