"""
File utility functions.
"""
import os
import glob
from typing import Optional, List


def find_files_by_pattern(pattern: str, base_path: str = ".") -> List[str]:
    """
    Find files matching a glob pattern.

    Args:
        pattern: Glob pattern to match
        base_path: Base directory to search from

    Returns:
        List of matching file paths
    """
    search_pattern = os.path.join(base_path, pattern)
    return glob.glob(search_pattern, recursive=True)


def get_constituency_md_file(year: int, base_folder: str = "constituency_data") -> Optional[str]:
    """
    Get the constituency markdown file for a specific year.

    Args:
        year: Election year
        base_folder: Base folder containing constituency data

    Returns:
        Path to the markdown file, or None if not found
    """
    md_file = os.path.join(base_folder, str(year), f"constituencies_{year}.md")
    if os.path.exists(md_file):
        return md_file
    return None


def get_constituency_csv_file(year: int, state: str, district: str,
                              base_folder: str = "constituency_data") -> Optional[str]:
    """
    Get the CSV file for a specific constituency.

    Args:
        year: Election year
        state: State name
        district: District name
        base_folder: Base folder containing constituency data

    Returns:
        Path to the CSV file, or None if not found
    """
    district_dir = os.path.join(base_folder, str(year), state, district)

    if not os.path.exists(district_dir):
        return None

    # Look for CSV files in the district directory
    csv_files = [f for f in os.listdir(district_dir) if f.endswith('.csv')]

    if csv_files:
        return os.path.join(district_dir, csv_files[0])

    return None


def discover_states_and_districts(year: int, base_folder: str = "constituency_data") -> dict:
    """
    Discover all available states and districts for a given year.

    Args:
        year: The election year
        base_folder: Base folder containing constituency data

    Returns:
        Dictionary mapping states to lists of districts
    """
    year_str = str(year)
    year_folder = os.path.join(base_folder, year_str)

    if not os.path.exists(year_folder):
        print(f"No data found for year {year}")
        return {}

    # Get all state folders
    state_folders = [f for f in os.listdir(year_folder)
                     if os.path.isdir(os.path.join(year_folder, f))]

    result = {}
    for state in state_folders:
        state_path = os.path.join(year_folder, state)

        # Get all district folders within this state
        district_folders = [f for f in os.listdir(state_path)
                          if os.path.isdir(os.path.join(state_path, f))]

        result[state] = district_folders

    return result


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.

    Args:
        directory: Path to the directory
    """
    os.makedirs(directory, exist_ok=True)


def get_safe_filename(name: str) -> str:
    """
    Convert a string to a safe filename.

    Args:
        name: Original name

    Returns:
        Safe filename
    """
    return "".join([c if c.isalnum() else "_" for c in name]).rstrip("_")


def file_exists_and_not_empty(file_path: str) -> bool:
    """
    Check if a file exists and is not empty.

    Args:
        file_path: Path to the file

    Returns:
        True if file exists and is not empty
    """
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0
