"""
CSV processing utilities.
Centralizes CSV reading, writing, and processing logic to eliminate duplication.
"""
import csv
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from .file_manager import FileManager


class CSVProcessor:
    """Utility class for CSV operations."""
    
    @staticmethod
    def find_csv_files(base_path: str, pattern: str = "*.csv") -> List[str]:
        """
        Find all CSV files in a directory structure.
        
        Args:
            base_path: Base directory to search
            pattern: File pattern to match
            
        Returns:
            List of CSV file paths
        """
        return FileManager.find_files_by_pattern(base_path, pattern, recursive=True)
    
    @staticmethod
    def read_candidate_data(csv_path: str, winners_only: bool = False,
                           encoding: str = 'utf-8') -> List[Dict[str, Any]]:
        """
        Read candidate data from CSV file with standardized format.
        
        Args:
            csv_path: Path to CSV file
            winners_only: Whether to filter only winners
            encoding: File encoding
            
        Returns:
            List of candidate records as dictionaries
        """
        candidates = []
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return candidates
        
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                headers = None
                
                for row_num, row in enumerate(reader):
                    if not row:  # Skip empty rows
                        continue
                    
                    # First non-empty row might be headers
                    if headers is None:
                        # Check if this looks like a header row
                        if CSVProcessor._is_header_row(row):
                            headers = row
                            continue
                        else:
                            # Generate default headers
                            headers = [f"col_{i}" for i in range(len(row))]
                    
                    # Create candidate record
                    candidate = {}
                    for i, value in enumerate(row):
                        header = headers[i] if i < len(headers) else f"col_{i}"
                        candidate[header] = value.strip() if value else ""
                    
                    # Filter winners if requested
                    if winners_only:
                        winner_column = CSVProcessor._find_winner_column(candidate)
                        if winner_column and candidate.get(winner_column, '').lower() != 'yes':
                            continue
                    
                    candidate['_source_file'] = csv_path
                    candidate['_row_number'] = row_num
                    candidates.append(candidate)
                    
        except Exception as e:
            print(f"Error reading CSV file {csv_path}: {str(e)}")
        
        return candidates
    
    @staticmethod
    def extract_candidate_urls(csv_path: str, winners_only: bool = False) -> Dict[str, str]:
        """
        Extract candidate names and URLs from CSV file.
        
        Args:
            csv_path: Path to CSV file
            winners_only: Whether to filter only winners
            
        Returns:
            Dictionary mapping candidate names to URLs
        """
        candidates = CSVProcessor.read_candidate_data(csv_path, winners_only)
        candidate_urls = {}
        
        for candidate in candidates:
            # Try to find name and URL columns
            name = CSVProcessor._extract_candidate_name(candidate)
            url = CSVProcessor._extract_candidate_url(candidate)
            
            if name and url:
                candidate_urls[name] = url
        
        return candidate_urls
    
    @staticmethod
    def write_csv_data(file_path: str, data: List[Dict[str, Any]], 
                       fieldnames: Optional[List[str]] = None) -> bool:
        """
        Write data to CSV file.
        
        Args:
            file_path: Output CSV file path
            data: List of dictionaries to write
            fieldnames: Optional fieldnames list
            
        Returns:
            True if successful, False otherwise
        """
        if not data:
            return False
        
        try:
            # Ensure directory exists
            FileManager.ensure_directory(os.path.dirname(file_path))
            
            # Determine fieldnames if not provided
            if not fieldnames:
                fieldnames = list(data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            return True
            
        except Exception as e:
            print(f"Error writing CSV file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def merge_csv_files(csv_files: List[str], output_path: str) -> bool:
        """
        Merge multiple CSV files into one.
        
        Args:
            csv_files: List of CSV file paths to merge
            output_path: Output CSV file path
            
        Returns:
            True if successful, False otherwise
        """
        all_data = []
        all_fieldnames = set()
        
        # Read all CSV files
        for csv_file in csv_files:
            data = CSVProcessor.read_candidate_data(csv_file)
            all_data.extend(data)
            
            # Collect all unique fieldnames
            for record in data:
                all_fieldnames.update(record.keys())
        
        # Write merged data
        fieldnames = sorted(list(all_fieldnames))
        return CSVProcessor.write_csv_data(output_path, all_data, fieldnames)
    
    @staticmethod
    def get_csv_statistics(csv_path: str) -> Dict[str, Any]:
        """
        Get statistics about a CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dictionary with statistics
        """
        candidates = CSVProcessor.read_candidate_data(csv_path)
        winners = CSVProcessor.read_candidate_data(csv_path, winners_only=True)
        
        return {
            'file_path': csv_path,
            'total_candidates': len(candidates),
            'total_winners': len(winners),
            'has_urls': sum(1 for c in candidates if CSVProcessor._extract_candidate_url(c)),
            'columns': list(candidates[0].keys()) if candidates else [],
            'file_size': os.path.getsize(csv_path) if os.path.exists(csv_path) else 0
        }
    
    # Helper methods
    @staticmethod
    def _is_header_row(row: List[str]) -> bool:
        """Check if a row looks like headers."""
        if not row:
            return False
        
        # Check for common header patterns
        common_headers = ['name', 'constituency', 'party', 'winner', 'url', 'link']
        row_lower = [cell.lower() for cell in row if cell]
        
        # If any common headers found, likely a header row
        return any(header in ' '.join(row_lower) for header in common_headers)
    
    @staticmethod
    def _find_winner_column(candidate: Dict[str, Any]) -> Optional[str]:
        """Find the column that indicates if candidate is a winner."""
        for key in candidate.keys():
            if 'winner' in key.lower() or 'won' in key.lower():
                return key
        return None
    
    @staticmethod
    def _extract_candidate_name(candidate: Dict[str, Any]) -> Optional[str]:
        """Extract candidate name from record."""
        # Try common name column patterns
        name_patterns = ['name', 'candidate', 'candidate_name', 'full_name']
        
        for pattern in name_patterns:
            for key in candidate.keys():
                if pattern in key.lower():
                    name = candidate[key]
                    if name and name.strip():
                        return name.strip()
        
        # Fallback to first non-empty string column
        for value in candidate.values():
            if isinstance(value, str) and value.strip() and not value.startswith('http'):
                return value.strip()
        
        return None
    
    @staticmethod
    def _extract_candidate_url(candidate: Dict[str, Any]) -> Optional[str]:
        """Extract candidate URL from record."""
        # Try common URL column patterns
        url_patterns = ['url', 'link', 'profile', 'candidate_link']
        
        for pattern in url_patterns:
            for key in candidate.keys():
                if pattern in key.lower():
                    url = candidate[key]
                    if url and (url.startswith('http://') or url.startswith('https://')):
                        return url.strip()
        
        # Fallback to any HTTP/HTTPS value
        for value in candidate.values():
            if isinstance(value, str) and (value.startswith('http://') or value.startswith('https://')):
                return value.strip()
        
        return None