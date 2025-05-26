# utils/file_manager.py
"""
Enhanced file management utilities with support for existing folder structure
"""
import os
import re
import glob
from typing import List, Optional, Union, Dict
from config.election_config import ElectionConfig


class ElectionFileManager:
    """Manages file operations for election data with flexible folder structures"""

    def __init__(self):
        # No base folder needed as we use different structures
        pass

    @staticmethod
    def create_output_folder(config: ElectionConfig, url: str) -> str:
        """Create output folder based on election config and URL"""
        year = config.extract_year_from_url(url)

        if config.constituency_type == "lok_sabha":
            # constituency_data/{year}/
            output_folder = f"constituency_data/{year}"
        else:
            # state_assembly/{state_name}/
            output_folder = f"state_assembly/{year}/{config.state_name}"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created directory: {output_folder}")
        else:
            print(f"Using existing directory: {output_folder}")

        return output_folder

    @staticmethod
    def get_constituency_md_file(config: ElectionConfig, year: Optional[str] = None) -> Optional[str]:
        """Find constituency markdown file based on election type"""
        if config.constituency_type == "lok_sabha":
            base_path = f"constituency_data/{year}" if year else "constituency_data/*"
        else:
            base_path = f"state_assembly/{year}/{config.state_name}"

        # Look for markdown files
        md_pattern = os.path.join(base_path, "constituencies_links_*.md")
        md_files = glob.glob(md_pattern)

        if md_files:
            return md_files[0]

        # If not found in specific location, search recursively
        if config.constituency_type == "lok_sabha":
            search_pattern = "constituency_data/*/constituencies_links_*.md"
        else:
            search_pattern = f"state_assembly/*/{config.state_name}/**/constituencies_links_*.md"

        md_files = glob.glob(search_pattern, recursive=True)
        return md_files[0] if md_files else None

    @staticmethod
    def get_constituency_csv_files(config: ElectionConfig, year: Optional[str] = None,
                                   state: Optional[str] = None, district: Optional[str] = None) -> Union[
        str, List[str], None]:
        """Find constituency CSV files based on folder structure"""

        if config.constituency_type == "lok_sabha":
            # Existing MP structure: constituency_data/{year}/{state}/{district}/
            base_path = f"constituency_data/{year}" if year else "constituency_data/*"

            if year and state and district:
                csv_path = os.path.join(base_path, state, district, f"{district}.csv")
                return csv_path if os.path.exists(csv_path) else None
            elif year and state:
                csv_pattern = os.path.join(base_path, state, "**", "*.csv")
                return glob.glob(csv_pattern, recursive=True)
            elif year:
                csv_pattern = os.path.join(base_path, "**", "*.csv")
                return glob.glob(csv_pattern, recursive=True)
            else:
                csv_pattern = "constituency_data/**/**.csv"
                return glob.glob(csv_pattern, recursive=True)

        else:
            # State assembly structure: state_assembly/{state_name}/{district}/
            base_path = f"state_assembly/{year}/{config.state_name}"

            if district:
                csv_path = os.path.join(base_path, district, f"{district}.csv")
                return csv_path if os.path.exists(csv_path) else None
            else:
                csv_pattern = os.path.join(base_path, "**", "*.csv")
                return glob.glob(csv_pattern, recursive=True)

    @staticmethod
    def discover_states_and_districts(config: ElectionConfig, year: Optional[str] = None) -> Dict[str, List[str]]:
        """Discover available states and districts based on folder structure"""
        result = {}

        if config.constituency_type == "lok_sabha":
            # constituency_data/{year}/{state}/{district}/
            if year:
                year_folder = f"constituency_data/{year}"
                if os.path.exists(year_folder):
                    state_folders = [f for f in os.listdir(year_folder)
                                     if os.path.isdir(os.path.join(year_folder, f))]

                    for state in state_folders:
                        state_path = os.path.join(year_folder, state)
                        district_folders = [f for f in os.listdir(state_path)
                                            if os.path.isdir(os.path.join(state_path, f))]
                        result[state] = district_folders
        else:
            # state_assembly/{year}{state_name}/{district}/
            state_folder = f"state_assembly/{year}/{config.state_name}"
            if os.path.exists(state_folder):
                district_folders = [f for f in os.listdir(state_folder)
                                    if os.path.isdir(os.path.join(state_folder, f))]
                result[config.state_name] = district_folders

        return result