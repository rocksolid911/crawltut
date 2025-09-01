"""
File management utilities.
Centralizes file operations and path handling to eliminate duplication.
"""
import os
import re
from pathlib import Path
from typing import List, Optional


class FileManager:
    """Utility class for common file operations."""
    
    @staticmethod
    def create_safe_filename(name: str, max_length: int = 200) -> str:
        """
        Create a safe filename from candidate name or other text.
        Eliminates duplication of filename sanitization logic.
        
        Args:
            name: Original name/text
            max_length: Maximum filename length
            
        Returns:
            Safe filename string
        """
        if not name:
            return "unnamed"
        
        # Replace non-alphanumeric characters with underscores
        safe_name = re.sub(r'[^\w\-_]', '_', name)
        
        # Remove consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        
        # Truncate if too long
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length].rstrip('_')
        
        return safe_name or "unnamed"
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            path: Directory path to create
            
        Returns:
            The created directory path
        """
        os.makedirs(path, exist_ok=True)
        return path
    
    @staticmethod
    def create_candidate_directory(base_dir: str, candidate_name: str) -> str:
        """
        Create a directory for a candidate with safe naming.
        
        Args:
            base_dir: Base directory path
            candidate_name: Candidate name
            
        Returns:
            Created directory path
        """
        safe_name = FileManager.create_safe_filename(candidate_name)
        candidate_dir = os.path.join(base_dir, safe_name)
        return FileManager.ensure_directory(candidate_dir)
    
    @staticmethod
    def find_files_by_pattern(base_path: str, pattern: str = "*.csv", 
                             recursive: bool = True) -> List[str]:
        """
        Find files matching a pattern in a directory.
        
        Args:
            base_path: Base directory to search
            pattern: File pattern (e.g., "*.csv", "*_winners.csv")
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        base_path = Path(base_path)
        if not base_path.exists():
            return []
        
        if recursive:
            return [str(p) for p in base_path.rglob(pattern)]
        else:
            return [str(p) for p in base_path.glob(pattern)]
    
    @staticmethod
    def file_exists_and_not_empty(file_path: str) -> bool:
        """
        Check if file exists and is not empty.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file exists and has content
        """
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension in lowercase."""
        return Path(filename).suffix.lower()
    
    @staticmethod
    def join_paths(*paths: str) -> str:
        """Safely join multiple path components."""
        return os.path.join(*paths)
    
    @staticmethod
    def get_parent_directory(file_path: str) -> str:
        """Get parent directory of a file path."""
        return os.path.dirname(file_path)
    
    @staticmethod
    def create_year_directory_structure(base_path: str, year: int, 
                                       election_type: str = "mp") -> str:
        """
        Create directory structure for election year data.
        
        Args:
            base_path: Base directory
            year: Election year
            election_type: Type of election ("mp" or "mla")
            
        Returns:
            Created directory path
        """
        year_dir = os.path.join(base_path, f"{election_type}_{year}")
        return FileManager.ensure_directory(year_dir)