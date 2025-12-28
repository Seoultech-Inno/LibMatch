"""
Section 3.5: Evaluation and Validation Module
Evaluates the performance of the developer candidate recommendation system.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from libmatch.config import DEFAULT_N_VALUES, DEFAULT_M_VALUES, VALIDATION_RESULTS_PATH
from libmatch.devlibmatcher.candidate_ranking import CandidateRanker
from libmatch.visualization import plot_candidates_scatter, plot_metrics_comparison


class Evaluator:
    """
    Class for evaluating the performance of developer candidate recommendation system
    
    Implements evaluation and validation functionality corresponding to Section 3.5 of the paper.
    """
    
    def __init__(self):
        """Initialize Evaluator"""
        self.ranker = CandidateRanker()
    
    def calculate_metrics(self, users: pd.DataFrame, keyword_list: List[List[str]], 
                         m_val: int) -> Dict:
        """
        Calculate performance metrics for given keyword_list and M value
        
        Parameters:
        -----------
        users : pd.DataFrame
            User data (requires is_NLP, pkgs_used columns)
        keyword_list : List[List[str]]
            Grouped library keyword list
        m_val : int
            Minimum number of matching libraries (M value)
        
        Returns:
        --------
        dict : Dictionary of performance metrics
        """
        # Filter libraries
        users = self.ranker.filter_candidates(users, keyword_list, m_val)
        
        # Calculate Confusion Matrix components
        TP = len(users[(users['is_NLP'] == True) & (users['P'] == True)])
        FP = len(users[(users['is_NLP'] == False) & (users['P'] == True)])
        FN = len(users[(users['is_NLP'] == True) & (users['P'] == False)])
        TN = len(users[(users['is_NLP'] == False) & (users['P'] == False)])
        
        # Calculate performance metrics
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'TP': TP,
            'FP': FP,
            'FN': FN,
            'TN': TN,
            'Precision': precision,
            'Recall': recall,
            'F1 Score': f1_score,
            '선택된 사용자 수': TP + FP  # validation.py와 동일한 컬럼 users
        }
    
    def evaluate_nm_combinations(self, users: pd.DataFrame, df_lib: pd.DataFrame,
                                n_values: List[int] = None, 
                                m_values: List[int] = None) -> pd.DataFrame:
        """
        Measure performance for all combinations of N and M values
        
        Parameters:
        -----------
        users : pd.DataFrame
            User data
        df_lib : pd.DataFrame
            Library information DataFrame
        n_values : List[int], optional
            List of N values (default: loaded from config)
        m_values : List[int], optional
            List of M values (default: loaded from config)
        
        Returns:
        --------
        pd.DataFrame : DataFrame containing results
        """
        if n_values is None:
            n_values = DEFAULT_N_VALUES
        if m_values is None:
            m_values = DEFAULT_M_VALUES
        
        results = []
        
        print("=" * 80)
        print("Starting performance measurement for N and M value combinations")
        print("=" * 80)
        print(f"N values: {n_values}")
        print(f"M values: {m_values}")
        print(f"Total combinations: {len(n_values) * len(m_values)}\n")
        
        # For each N value
        for n_val in n_values:
            print(f"\n{'=' * 80}")
            print(f"Processing N = {n_val}...")
            print(f"{'=' * 80}")
            
            # Generate keyword list according to N value
            keyword_list_n = self.ranker.get_keyword_list(df_lib, n=n_val)
            
            # Evaluate for each M value
            for m_val in m_values:
                metrics = self.calculate_metrics(users, keyword_list_n, m_val)
                
                # Save result
                result = {
                    'N': n_val,
                    'M': m_val,
                    **metrics
                }
                results.append(result)
                
                print(f"  N={n_val:3d}, M={m_val}: "
                      f"Precision={metrics['Precision']:.4f}, "
                      f"Recall={metrics['Recall']:.4f}, "
                      f"F1={metrics['F1 Score']:.4f}")
        
        return pd.DataFrame(results)
    
    def print_results(self, df_results: pd.DataFrame):
        """
        Print results
        
        Parameters:
        -----------
        df_results : pd.DataFrame
            Evaluation results DataFrame
        """
        # Print full results table
        print("\n" + "=" * 100)
        print("Performance measurement results for N and M value combinations (Precision, Recall, F1 Score)")
        print("=" * 100)
        print(df_results.to_string(index=False))
        print("=" * 100)
        
        # Organize as pivot table (N as rows, M as columns)
        print("\n" + "=" * 80)
        print("Precision Pivot Table")
        print("=" * 80)
        pivot_precision = df_results.pivot_table(
            values='Precision', index='N', columns='M', aggfunc='first'
        )
        print(pivot_precision.to_string())
        
        print("\n" + "=" * 80)
        print("Recall Pivot Table")
        print("=" * 80)
        pivot_recall = df_results.pivot_table(
            values='Recall', index='N', columns='M', aggfunc='first'
        )
        print(pivot_recall.to_string())
        
        print("\n" + "=" * 80)
        print("F1 Score Pivot Table")
        print("=" * 80)
        pivot_f1 = df_results.pivot_table(
            values='F1 Score', index='N', columns='M', aggfunc='first'
        )
        print(pivot_f1.to_string())
        print("=" * 80)
    
    def save_results(self, df_results: pd.DataFrame, output_path: str = None):
        """
        Save results to CSV file
        
        Parameters:
        -----------
        df_results : pd.DataFrame
            Evaluation results DataFrame
        output_path : str, optional
            Save path (default: loaded from config)
        """
        if output_path is None:
            output_path = str(VALIDATION_RESULTS_PATH)
        
        df_results.to_csv(output_path, index=False)
        print(f"\nResults saved to {output_path}.")
    
    def evaluate_library_filtering(self, users: pd.DataFrame, keyword_list: List[List[str]], 
                                   min_matches: int, save_csv: Optional[str] = None, 
                                   show_plot: bool = True, calculate_metrics: bool = True) -> dict:
        """
        Library filtering and performance evaluation function (evaluate_library_filtering from Lib2Keyword.ipynb)
        
        Parameters:
        -----------
        users : pd.DataFrame
            User data (requires is_NLP, pkgs_used, contribs, followers columns)
        keyword_list : List[List[str]]
            Library keyword list to use for filtering
        min_matches : int
            Minimum number of matching libraries (M value)
        save_csv : str, optional
            CSV filename to save results (None to not save)
        show_plot : bool, default=True
            Whether to display visualization
        calculate_metrics : bool, default=True
            Whether to calculate performance metrics
        
        Returns:
        --------
        dict : Dictionary of performance metrics
        """
        # Filter libraries
        users = self.ranker.filter_candidates(users, keyword_list, min_matches)
        
        # Extract selected users
        temp_2 = users[users['P'] == True].copy()
        if 'users' in temp_2.columns:
            temp_2['users'] = temp_2['users'].map(
                lambda x: x.login if hasattr(x, 'login') else x
            )
        temp_2 = temp_2.loc[:, ['users', 'pkgs_used', 'contribs', 'followers']].copy()
        temp_2.reset_index(drop=True, inplace=True)
        
        # Save CSV
        if save_csv:
            temp_2.to_csv(save_csv, index=False)
            print(f"Filtered candidates saved to {save_csv}")
        
        # Visualization
        if show_plot:
            plot_candidates_scatter(users)
        
        # Calculate performance metrics
        metrics = {}
        if calculate_metrics:
            metrics = self.calculate_metrics(users, keyword_list, min_matches)
            
            # Basic statistics
            total_users = len(users)
            total_nlp_developers = len(users[users['is_NLP'] == True])
            total_selected_users = len(users[users['P'] == True])
            
            print("=" * 70)
            print(f"Performance Metrics - M = {min_matches}")
            print("=" * 70)
            print(f"\n[Basic Statistics]")
            print(f"  Total users: {total_users}")
            print(f"  NLP developers: {total_nlp_developers}")
            print(f"  Selected users: {total_selected_users}")
            print(f"\n[Confusion Matrix]")
            print(f"  TP (True Positive): {metrics['TP']}")
            print(f"  FP (False Positive): {metrics['FP']}")
            print(f"  FN (False Negative): {metrics['FN']}")
            print(f"  TN (True Negative): {metrics['TN']}")
            print(f"\n[Performance Metrics]")
            print(f"  Precision: {metrics['Precision']:.4f}")
            print(f"  Recall: {metrics['Recall']:.4f}")
            print(f"  F1 Score: {metrics['F1 Score']:.4f}")
            print("=" * 70)
        
        return metrics

