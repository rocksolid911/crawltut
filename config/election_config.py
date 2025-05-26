# config/election_config.py
"""
Configuration for different election types
"""
import re
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ElectionConfig:
    """Configuration for different election types"""
    name: str
    base_url_pattern: str
    year_extraction_pattern: str
    folder_structure: str  # 'constituency_data' or 'state_assembly'
    state_name: str  # Actual state name for folder structure
    constituency_type: str  # 'lok_sabha' or 'assembly'

    def extract_year_from_url(self, url: str) -> str:
        """Extract year from URL based on the pattern"""
        match = re.search(self.year_extraction_pattern, url, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2) if match.lastindex > 1 else match.group(1)
        return "unknown_year"

    def get_base_folder_path(self, year: str) -> str:
        """Get base folder path for storing data"""
        if self.constituency_type == "lok_sabha":
            return f"constituency_data/{year}"
        else:
            return f"state_assembly/{self.state_name}"


# Predefined configurations
ELECTION_CONFIGS: Dict[str, ElectionConfig] = {
    'lok_sabha': ElectionConfig(
        name="Lok Sabha",
        base_url_pattern=r"myneta\.info/LokSabha\d{4}",
        year_extraction_pattern=r'LokSabha(\d{4})|ls(\d{4})',
        folder_structure="constituency_data",
        state_name="",  # Not applicable for Lok Sabha
        constituency_type="lok_sabha"
    ),
    'andhra_pradesh': ElectionConfig(
        name="Andhra Pradesh Assembly",
        base_url_pattern=r"myneta\.info/AndhraPradesh\d{4}",
        year_extraction_pattern=r'AndhraPradesh(\d{4})|ap(\d{4})',
        folder_structure="state_assembly",
        state_name="ANDHRA PRADESH",
        constituency_type="assembly"
    ),
    'karnataka': ElectionConfig(
        name="Karnataka Assembly",
        base_url_pattern=r"myneta\.info/Karnataka\d{4}",
        year_extraction_pattern=r'Karnataka(\d{4})|ka(\d{4})',
        folder_structure="state_assembly",
        state_name="KARNATAKA",
        constituency_type="assembly"
    ),
    'telangana': ElectionConfig(
        name="Telangana Assembly",
        base_url_pattern=r"myneta\.info/Telangana\d{4}",
        year_extraction_pattern=r'Telangana(\d{4})|ts(\d{4})',
        folder_structure="state_assembly",
        state_name="TELANGANA",
        constituency_type="assembly"
    ),
    # Add more states as needed
}


def detect_election_type(url: str) -> Optional[ElectionConfig]:
    """Auto-detect election type from URL"""
    for config in ELECTION_CONFIGS.values():
        if re.search(config.base_url_pattern, url, re.IGNORECASE):
            return config
    return None


def get_config_by_name(name: str) -> Optional[ElectionConfig]:
    """Get configuration by name"""
    return ELECTION_CONFIGS.get(name.lower())