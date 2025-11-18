"""
Configuration settings for the Indian Election Data Scraper.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CrawlerConfig:
    """Configuration for web crawler behavior."""

    # Browser settings
    headless: bool = True
    browser_type: str = "chromium"
    session_id: str = "election_crawler_session"

    # Crawling behavior
    batch_size: int = 50
    delay_between_requests: int = 2  # seconds
    max_retries: int = 5

    # Data paths
    base_data_dir: str = "data"
    logs_dir: str = "logs"

    # Specific data directories
    constituency_data_dir: str = "constituency_data"
    candidate_data_dir: str = "candidate_data"
    state_assembly_dir: str = "state_assembly"

    # Output settings
    missing_images_csv: str = "missing_profile_images.csv"
    missing_images_mla_csv: str = "missing_profile_images_mla.csv"

    # Feature flags
    force_regenerate_json: bool = False
    skip_if_force_regenerated: bool = True
    winners_only: bool = False

    def __post_init__(self):
        """Create necessary directories after initialization."""
        self._create_directories()

    def _create_directories(self):
        """Create all necessary data directories."""
        directories = [
            self.base_data_dir,
            self.logs_dir,
            self.constituency_data_dir,
            self.candidate_data_dir,
            self.state_assembly_dir,
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def get_constituency_path(self, year: int, state: Optional[str] = None,
                             district: Optional[str] = None) -> str:
        """Get the path for constituency data."""
        path = os.path.join(self.constituency_data_dir, str(year))
        if state:
            path = os.path.join(path, state)
        if district:
            path = os.path.join(path, district)
        return path

    def get_candidate_path(self, year: int) -> str:
        """Get the path for candidate data."""
        return os.path.join(self.candidate_data_dir, str(year))

    def get_state_assembly_path(self, state: str, year: int) -> str:
        """Get the path for state assembly data."""
        return os.path.join(self.state_assembly_dir, state, str(year))


@dataclass
class ScraperConfig:
    """Configuration for data source and URLs."""

    # Base URLs
    base_url: str = "https://www.myneta.info"
    state_assembly_url_template: str = "https://www.myneta.info/state_assembly.php?state={state}"

    # Election years to process
    default_years: list = None

    def __post_init__(self):
        if self.default_years is None:
            self.default_years = [2024, 2019, 2014, 2009, 2004]

    def get_state_assembly_url(self, state: str) -> str:
        """Get the URL for a specific state assembly."""
        return self.state_assembly_url_template.format(state=state)


# Global configuration instances
crawler_config = CrawlerConfig()
scraper_config = ScraperConfig()


def get_crawler_config() -> CrawlerConfig:
    """Get the global crawler configuration."""
    return crawler_config


def get_scraper_config() -> ScraperConfig:
    """Get the global scraper configuration."""
    return scraper_config


# Indian states list
INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chattisgarh",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu And Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttarakhand",
    "Uttar Pradesh",
    "West Bengal",
]
