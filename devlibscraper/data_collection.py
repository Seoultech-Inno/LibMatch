"""
Section 3.1: Data Collection and Preprocessing Module
Collects developer data and library information from GitHub.
"""

import re
import json
import time
import pickle
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd

import pandas as pd
from github import Github, RateLimitExceededException, UnknownObjectException
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from tqdm import tqdm

from libmatch.config import (
    GITHUB_TOKENS,
    SUPPORTED_LANGUAGES,
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,
    USE_LOCAL_DATA,
    LIBRARIES_PKL_PATH
)
from libmatch.utils import extract_library_name_from_import


class GitHubDataCollector:
    """
    Class for collecting developer data from GitHub
    
    Implements data collection functionality corresponding to Section 3.1 of the paper.
    """
    
    def __init__(self, github_tokens: List[str] = None):
        """
        Parameters:
        -----------
        github_tokens : List[str], optional
            List of GitHub API tokens (default: loaded from config)
            Note: GitHub token is only needed for data collection methods.
            For loading saved data (load_users, load_libraries), token is optional.
        """
        if github_tokens is None:
            github_tokens = GITHUB_TOKENS
        
        # GitHub token is optional - only needed for data collection, not for loading saved data
        self.github_tokens = github_tokens if github_tokens else []
        if github_tokens:
            self.github = Github(github_tokens[0])
        else:
            self.github = None
        self.files_path = []
    
    def search_python_files(self, repo, dirname: str = '/') -> List[str]:
        """
        Recursively search for Python files (.py, .ipynb) in repository
        
        Parameters:
        -----------
        repo : Repository
            GitHub Repository object
        dirname : str
            Directory path to search
        
        Returns:
        --------
        List[str] : List of Python file paths
        """
        try:
            self.files_path = []
            filenames = [i.path for i in repo.get_contents(dirname)]
            
            for filename in filenames:
                full_filename = filename
                if '.' not in full_filename:
                    self.search_python_files(repo, full_filename)
                else:
                    ext = full_filename.split('.')[-1]
                    if ext == 'py' or ext == 'ipynb':
                        self.files_path.append(full_filename)
        except (TypeError, UnknownObjectException):
            pass
        
        return self.files_path
    
    def extract_libraries_from_code(self, code: str, file_ext: str) -> List[str]:
        """
        Extract import statements from code and return list of library names
        
        Parameters:
        -----------
        code : str
            Source code content
        file_ext : str
            File extension ('py' or 'ipynb')
        
        Returns:
        --------
        List[str] : List of library names
        """
        # Regex pattern: match import statements or from ... import statements
        pattern = r'import [0-9a-zA-Z_.]+|from [0-9a-zA-Z_.]+ import'
        import_statements = re.findall(pattern, code)
        
        # Extract library name from each import statement
        libraries = []
        for statement in import_statements:
            try:
                library_name = extract_library_name_from_import(statement)
                libraries.append(library_name)
            except (IndexError, AttributeError):
                continue
        
        return libraries
    
    def get_packages_from_repos(self, repos: List, languages: List[str] = None) -> List[List[List[str]]]:
        """
        Extract packages used from list of repositories
        
        Parameters:
        -----------
        repos : List
            List of GitHub Repository objects
        languages : List[str], optional
            List of supported programming languages (default: loaded from config)
        
        Returns:
        --------
        List[List[List[str]]] : List of libraries used in each file of each repository
        """
        if languages is None:
            languages = SUPPORTED_LANGUAGES
        
        black_list = []
        repos_pkgs = []
        
        for repo in tqdm(repos, desc="Extracting packages from repositories"):
            repo_pkgs = []
            
            # Filtering: exclude .github.io sites or unsupported languages
            if ".github.io" in repo.name or repo.language not in languages:
                continue
            
            # Exclude forked repositories (as per paper Section 3.3.2)
            if repo.fork:
                continue
            
            # Prioritize setup.py and requirements.txt (as per paper Section 3.3.2)
            repo_pkgs_priority = []
            priority_files = ['setup.py', 'requirements.txt']
            
            for priority_file in priority_files:
                try:
                    if priority_file in [f.path.split('/')[-1] for f in repo.get_contents('/')]:
                        content = repo.get_contents(priority_file).decoded_content.decode('utf-8')
                        if priority_file == 'requirements.txt':
                            # Parse requirements.txt format
                            pkgs = [line.split('==')[0].split('>=')[0].split('<=')[0].strip() 
                                   for line in content.split('\n') 
                                   if line.strip() and not line.strip().startswith('#')]
                        else:
                            # Extract from setup.py using regex
                            pkgs = self.extract_libraries_from_code(content, 'py')
                        repo_pkgs_priority.extend(pkgs)
                except (UnknownObjectException, Exception):
                    continue
            
            # If priority files found, use them; otherwise search Python files
            if repo_pkgs_priority:
                repo_pkgs = [repo_pkgs_priority]
            else:
                # Search for Python files (fallback)
                while True:
                    try:
                        py_files = self.search_python_files(repo, '/')
                    except RateLimitExceededException:
                        black_list.append(repo.full_name)
                        if len(black_list) >= 4:
                            black_list.pop(0)
                            if not (black_list[0] == black_list[1] == black_list[2]):
                                print(f"Rate limit exceeded for {repo.full_name}")
                                print("Sleeping for 1 hour...")
                                time.sleep(3600)
                        continue
                    break
                
                # Extract libraries from each file
                for file in py_files:
                    ext = file.split('.')[-1]
                    while True:
                        try:
                            if ext == 'py':
                                code = repo.get_contents(file).decoded_content.decode('utf-8')
                            elif ext == 'ipynb':
                                code = str(json.loads(
                                    repo.get_contents(file).decoded_content.decode('utf-8')
                                ))
                            
                            file_pkgs = self.extract_libraries_from_code(code, ext)
                            repo_pkgs.append(file_pkgs)
                            break
                        except RateLimitExceededException:
                            black_list.append(repo.full_name)
                            if len(black_list) >= 4:
                                black_list.pop(0)
                                if not (black_list[0] == black_list[1] == black_list[2]):
                                    print(f"Rate limit exceeded for {repo.full_name}")
                                    print("Sleeping for 1 hour...")
                                    time.sleep(3600)
                            continue
                        except Exception as e:
                            print(f"Error processing {repo.full_name}/{file}: {e}")
                            break
            
            repos_pkgs.append(repo_pkgs)
        
        return repos_pkgs
    
    def load_users(self, pkl_path: Path) -> pd.DataFrame:
        """
        Load saved user data
        
        Parameters:
        -----------
        pkl_path : Path
            Path to pickle file
        
        Returns:
        --------
        pd.DataFrame : User data
        """
        print(f"Loading users from {pkl_path}...")
        with open(pkl_path, 'rb') as f:
            users = pickle.load(f)
        print(f"Loaded {len(users)} users")
        return users
    
    def load_libraries(self, use_local: bool = None) -> pd.DataFrame:
        """
        Load library information from local file or MongoDB
        
        Parameters:
        -----------
        use_local : bool, optional
            Whether to use local data file (default: from config)
        
        Returns:
        --------
        pd.DataFrame : Library information DataFrame
        """
        if use_local is None:
            use_local = USE_LOCAL_DATA
        
        # Try to load from local file first if enabled
        if use_local and LIBRARIES_PKL_PATH.exists():
            try:
                return self.load_libraries_from_local(LIBRARIES_PKL_PATH)
            except Exception as e:
                print(f"Warning: Failed to load from local file: {e}")
                print("Falling back to MongoDB...")
        
        # Load from MongoDB
        return self.load_libraries_from_mongodb()
    
    def load_libraries_from_mongodb(self) -> pd.DataFrame:
        """
        Load library information from MongoDB
        
        Returns:
        --------
        pd.DataFrame : Library information DataFrame
        """
        print(f"Connecting to MongoDB: {MONGO_DB_NAME}.{MONGO_COLLECTION_NAME}...")
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        db = client[MONGO_DB_NAME]
        col = db[MONGO_COLLECTION_NAME]
        
        # Load library data (only those with stars and forks not equal to 0)
        cursor = col.find({"$and": [{"stars": {"$ne": 0}}, {"forks": {"$ne": 0}}]})
        df_lib = pd.json_normalize(cursor)
        
        client.close()
        print(f"Loaded {len(df_lib)} libraries from MongoDB")
        
        return df_lib
    
    def load_libraries_from_local(self, file_path: Path = None) -> pd.DataFrame:
        """
        Load library information from local file
        
        Parameters:
        -----------
        file_path : Path, optional
            Path to library data file (default: libmatch/data/libraries.pkl)
        
        Returns:
        --------
        pd.DataFrame : Library information DataFrame
        """
        if file_path is None:
            from libmatch.config import DATA_DIR
            file_path = DATA_DIR / 'libraries.pkl'
        
        if not file_path.exists():
            # Check for library_similarity_ranking.csv as alternative
            from libmatch.config import DATA_DIR
            ranking_csv = DATA_DIR / 'library_similarity_ranking.csv'
            if ranking_csv.exists():
                raise FileNotFoundError(
                    f"Library data file not found: {file_path}\n"
                    f"For validation, use library_similarity_ranking.csv instead.\n"
                    f"Run: python libmatch/devlibmatcher/pipeline.py --use-library-ranking-csv"
                )
            else:
                raise FileNotFoundError(
                    f"Library data file not found: {file_path}\n"
                    f"Please ensure library_similarity_ranking.csv exists in libmatch/data/"
                )
        
        print(f"Loading libraries from local file: {file_path}...")
        
        if file_path.suffix == '.pkl':
            with open(file_path, 'rb') as f:
                df_lib = pickle.load(f)
        elif file_path.suffix == '.json':
            df_lib = pd.read_json(file_path, orient='records')
        elif file_path.suffix == '.csv':
            df_lib = pd.read_csv(file_path)
            # Convert keywords back to list if it's a string
            if 'keywords' in df_lib.columns:
                df_lib['keywords'] = df_lib['keywords'].apply(
                    lambda x: x.split(', ') if isinstance(x, str) else x
                )
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        print(f"Loaded {len(df_lib)} libraries from local file")
        
        return df_lib
    
    def lib2kw(self, library_list: List[str], df_lib: pd.DataFrame = None) -> List[str]:
        """
        Convert library list to keyword list
        
        Parameters:
        -----------
        library_list : List[str]
            List of library names
        df_lib : pd.DataFrame, optional
            Library DataFrame (if None, loads from local file or MongoDB)
        
        Returns:
        --------
        List[str] : List of keywords
        """
        if df_lib is None:
            df_lib = self.load_libraries()
        
        lst_kw = []
        for lib in library_list:
            matches = df_lib[df_lib['search_word'] == lib]
            if not matches.empty:
                keywords = matches.iloc[0]['keywords']
                if isinstance(keywords, list):
                    lst_kw.append(keywords)
        
        lst_kw = sum(lst_kw, [])  # Flatten list
        return lst_kw
    
    def lib_check(self, library_count_list: List[tuple], df_lib: pd.DataFrame = None) -> List[str]:
        """
        Filter valid libraries from library list
        
        Parameters:
        -----------
        library_count_list : List[tuple]
            List of (library_name, usage_count) tuples
        df_lib : pd.DataFrame, optional
            Library DataFrame (if None, loads from local file or MongoDB)
        
        Returns:
        --------
        List[str] : List of valid library names
        """
        if df_lib is None:
            df_lib = self.load_libraries()
        
        lst_lib = []
        for lib, cnt in library_count_list:
            matches = df_lib[df_lib['search_word'] == lib]
            if not matches.empty:
                lst_lib.append(lib)
        
        return lst_lib

