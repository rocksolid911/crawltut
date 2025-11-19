"""
Common utilities for the election data crawler project.
This module contains shared functionality used across multiple modules.
"""

import os
import requests
import io
from datetime import datetime
from PIL import Image
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode


class CrawlerConfig:
    """
    Centralized configuration for web crawling operations.
    Provides consistent browser and crawler settings across the application.
    """

    @staticmethod
    def get_browser_config(headless=True, browser_type="chromium"):
        """
        Get standard browser configuration for crawling.

        Args:
            headless: Whether to run browser in headless mode
            browser_type: Type of browser to use (default: chromium)

        Returns:
            BrowserConfig: Configured browser settings
        """
        return BrowserConfig(
            headless=headless,
            browser_type=browser_type,
        )

    @staticmethod
    def get_run_config(session_id, cache_mode=CacheMode.BYPASS):
        """
        Get standard run configuration for crawling.

        Args:
            session_id: Unique identifier for the crawling session
            cache_mode: Cache strategy to use

        Returns:
            CrawlerRunConfig: Configured run settings
        """
        return CrawlerRunConfig(
            cache_mode=cache_mode,
            session_id=session_id,
        )


class ImageDownloader:
    """
    Utilities for downloading and saving candidate profile images.
    """

    @staticmethod
    def download_image_from_url(image_url, output_path):
        """
        Download image from URL and save as JPEG.

        Args:
            image_url: URL of the image to download
            output_path: Path where image should be saved

        Returns:
            bool: True if successful, False otherwise
        """
        if not image_url or not image_url.startswith(('http://', 'https://')):
            return False

        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert('RGB')

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            image.save(output_path, format='JPEG')
            print(f"✅ Image saved: {os.path.basename(output_path)}")
            return True

        except Exception as e:
            print(f"❌ Failed to download image: {str(e)}")
            return False


class ForceRegenerationTracker:
    """
    Utilities for tracking force-regenerated JSON files.
    Prevents redundant regeneration of already processed files.
    """

    @staticmethod
    def mark_as_force_regenerated(json_file_path):
        """
        Create a flag file to mark this file as force-regenerated.

        Args:
            json_file_path: Path to the JSON file
        """
        flag_file = json_file_path.replace('.json', '.force_regenerated')
        with open(flag_file, 'w') as f:
            f.write(datetime.now().isoformat())
        print(f"🏷️ Marked as force-regenerated: {os.path.basename(flag_file)}")

    @staticmethod
    def is_force_regenerated(json_file_path):
        """
        Check if this file was already force-regenerated.

        Args:
            json_file_path: Path to the JSON file

        Returns:
            bool: True if already force-regenerated, False otherwise
        """
        flag_file = json_file_path.replace('.json', '.force_regenerated')
        return os.path.exists(flag_file)

    @staticmethod
    def get_force_regenerated_timestamp(json_file_path):
        """
        Get the timestamp when this file was force-regenerated.

        Args:
            json_file_path: Path to the JSON file

        Returns:
            str: ISO format timestamp, or "Unknown" if not available
        """
        flag_file = json_file_path.replace('.json', '.force_regenerated')
        if os.path.exists(flag_file):
            try:
                with open(flag_file, 'r') as f:
                    return f.read().strip()
            except:
                return "Unknown"
        return None


class PathUtils:
    """
    Utilities for working with file paths and names.
    """

    @staticmethod
    def create_safe_filename(name):
        """
        Convert a name into a safe filename by removing special characters.

        Args:
            name: Original name (e.g., candidate name)

        Returns:
            str: Safe filename with only alphanumeric characters and underscores
        """
        return "".join([c if c.isalnum() else "_" for c in name]).rstrip("_")

    @staticmethod
    def ensure_directory_exists(file_path):
        """
        Ensure that the directory for a given file path exists.

        Args:
            file_path: Path to a file
        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)


class Constants:
    """
    Application-wide constants.
    """

    # File encodings to try when reading CSV files
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252']

    # Base paths
    BASE_PATH_STATE_ASSEMBLY = "state_assembly"
    BASE_PATH_CANDIDATE_DATA = "candidate_data"
    BASE_PATH_CONSTITUENCY_DATA = "constituency_data"

    # CSV column indices (for MP elections)
    MP_CSV_WINNER_COLUMN = 11
    MP_CSV_NAME_COLUMN = 4
    MP_CSV_URL_COLUMN = 12
    MP_CSV_CONSTITUENCY_COLUMN = 2

    # Batch sizes for async operations
    DEFAULT_BATCH_SIZE = 50
    MAX_WORKERS = 10

    # Retry settings
    MAX_RETRIES = 5
    RETRY_DELAY = 0.5
