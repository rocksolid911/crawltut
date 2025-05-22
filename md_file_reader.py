import os
import re
import glob

def get_constituency_md_file(year=None):
    """
    Find and return the path to the constituency Markdown file for a specific year.

    Args:
        year: The election year to look for (e.g. '2024'). If None, will try to find any year.

    Returns:
        Path to the Markdown file if found, None otherwise
    """
    base_folder = "constituency_data"
    # Convert year to string if it's an integer
    if year is not None:
        year = str(year)

    # If year is specified, look in that specific folder
    if year:
        year_folder = os.path.join(base_folder, year)
        if os.path.exists(year_folder):
            md_pattern = os.path.join(year_folder, "constituencies_links_*.md")
            md_files = glob.glob(md_pattern)
            if md_files:
                return md_files[0]  # Return the first match

    # If year not specified or not found, search all year folders
    year_folders = [f for f in os.listdir(base_folder)
                    if os.path.isdir(os.path.join(base_folder, f))
                    and re.match(r'\d{4}|unknown_year', f)]

    for year_folder in sorted(year_folders, reverse=True):  # Start with the newest year
        md_pattern = os.path.join(base_folder, year_folder, "constituencies_links_*.md")
        md_files = glob.glob(md_pattern)
        if md_files:
            return md_files[0]  # Return the first match

    return None