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



def get_constituency_csv_file(year=None, state=None, district=None):
    """
    Find and return the path to constituency CSV files.

    Args:
        year: The election year (e.g. '2024')
        state: The state name (e.g. 'ASSAM')
        district: The district name (e.g. 'DARRANG_UDALGURI')

    Returns:
        Path to CSV file if found, None otherwise
    """
    base_folder = "constituency_data"

    # Convert year to string if it's an integer
    if year is not None:
        year = str(year)

    # If all parameters are provided, get the specific district CSV
    if year and state and district:
        district_csv = os.path.join(base_folder, year, state, district, f"{district}.csv")
        if os.path.exists(district_csv):
            return district_csv

    # If only year and state provided, find all CSVs in that state
    elif year and state:
        csv_pattern = os.path.join(base_folder, year, state, "**", "*.csv")
        csv_files = glob.glob(csv_pattern, recursive=True)
        if csv_files:
            return csv_files  # Return all matches

    # If only year provided, search at year level as before
    elif year:
        year_folder = os.path.join(base_folder, year)
        if os.path.exists(year_folder):
            csv_pattern = os.path.join(year_folder, "**", "*.csv")
            csv_files = glob.glob(csv_pattern, recursive=True)
            if csv_files:
                return csv_files

    # If no parameters, search all years
    else:
        all_csvs = glob.glob(os.path.join(base_folder, "**", "*.csv"), recursive=True)
        if all_csvs:
            return all_csvs

    return None


def get_state_assembly_csv_file(year=None, state=None):
    """
    Find and return the path to state assembly CSV files.

    Args:
        year: The election year (e.g. '2024')
        state: The state name (e.g. 'ASSAM')
    Returns:
        Path to CSV file if found, None otherwise
    """
    base_folder = "state_assembly"

    # Convert year to string if it's an integer
    if year is not None:
        year = str(year)

    # If both year and state are provided, get the specific CSV
    if year and state:
        csv_path = os.path.join(base_folder,state,year, f"{state}_{year}.csv")
        if os.path.exists(csv_path):
            return csv_path

    # If only year is provided, search at year level
    elif year:
        year_folder = os.path.join(base_folder, year)
        if os.path.exists(year_folder):
            csv_pattern = os.path.join(year_folder, "**", "*.csv")
            csv_files = glob.glob(csv_pattern, recursive=True)
            if csv_files:
                return csv_files  # Return all matches

    # If no parameters, search all years
    else:
        all_csvs = glob.glob(os.path.join(base_folder, "**", "*.csv"), recursive=True)
        if all_csvs:
            return all_csvs

    return None