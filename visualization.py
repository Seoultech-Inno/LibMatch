"""
Visualization utility module
Provides visualization functions for developer candidate analysis.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Optional


def plot_candidates_scatter(filtered_users: pd.DataFrame, 
                           save_path: Optional[str] = None):
    """
    Scatter plot of contributors vs followers for filtered developer candidates
    
    Parameters:
    -----------
    filtered_users : pd.DataFrame
        Filtered user data (requires contribs, followers columns)
    save_path : str, optional
        File path to save (None to only display)
    """
    temp_2 = filtered_users[filtered_users['P'] == True].copy()
    
    if 'users' in temp_2.columns:
        # Extract login from users object
        temp_2['users'] = temp_2['users'].map(lambda x: x.login if hasattr(x, 'login') else x)
    
    temp_2 = temp_2.loc[:, ['users', 'pkgs_used', 'contribs', 'followers']].copy()
    temp_2.reset_index(drop=True, inplace=True)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(temp_2['contribs'], temp_2['followers'], alpha=0.6)
    plt.ylabel('followers')
    plt.xlabel('contribs')
    
    # Display median lines
    plt.axvline(np.median(temp_2['contribs']), 0, 1, 
                color='red', linestyle='--', linewidth=2, label='Median contribs')
    plt.axhline(np.median(temp_2['followers']), 0, 1, 
                color='red', linestyle='--', linewidth=2, label='Median followers')
    
    plt.title(f'Contributors vs Followers (Total: {len(temp_2)} candidates)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_library_distribution(users: pd.DataFrame, 
                            column: str = 'n_pkgs',
                            bins: int = 75,
                            xlim: Optional[tuple] = None):
    """
    Histogram of library usage distribution per user
    
    Parameters:
    -----------
    users : pd.DataFrame
        User data
    column : str
        Column name to plot histogram for
    bins : int
        Number of histogram bins
    xlim : tuple, optional
        x-axis range (min, max)
    """
    plt.figure(figsize=(10, 6))
    plt.hist(users[column], bins=bins)
    
    if xlim:
        plt.xlim(xlim)
    
    plt.ylabel('number of users')
    plt.xlabel(f'number of {column}')
    plt.title(f'Distribution of {column}')
    plt.grid(True, alpha=0.3)
    plt.show()
    plt.close()


def plot_metrics_comparison(df_results: pd.DataFrame, 
                           metric: str = 'F1 Score',
                           save_path: Optional[str] = None):
    """
    Performance metrics comparison graph by N and M values
    
    Parameters:
    -----------
    df_results : pd.DataFrame
        Evaluation results DataFrame (requires N, M, Precision, Recall, F1 Score columns)
    metric : str
        Metric name to visualize ('Precision', 'Recall', 'F1 Score')
    save_path : str, optional
        File path to save
    """
    pivot_table = df_results.pivot_table(
        values=metric, index='N', columns='M', aggfunc='first'
    )
    
    plt.figure(figsize=(12, 6))
    
    for m_val in pivot_table.columns:
        plt.plot(pivot_table.index, pivot_table[m_val], 
                marker='o', label=f'M={m_val}')
    
    plt.xlabel('N (Number of libraries)')
    plt.ylabel(metric)
    plt.title(f'{metric} by N and M values')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()
    
    plt.close()

