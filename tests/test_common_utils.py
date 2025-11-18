"""
Unit tests for common utilities module.
"""

import pytest
import os
import tempfile
from datetime import datetime
from src.utils.common_utils import (
    CrawlerConfig,
    ImageDownloader,
    ForceRegenerationTracker,
    PathUtils,
    Constants
)


class TestCrawlerConfig:
    """Test cases for CrawlerConfig class."""

    def test_get_browser_config(self):
        """Test browser configuration creation."""
        config = CrawlerConfig.get_browser_config()
        assert config is not None
        assert config.headless is True
        assert config.browser_type == "chromium"

    def test_get_run_config(self):
        """Test run configuration creation."""
        config = CrawlerConfig.get_run_config("test_session")
        assert config is not None
        assert config.session_id == "test_session"


class TestPathUtils:
    """Test cases for PathUtils class."""

    def test_create_safe_filename(self):
        """Test safe filename creation."""
        # Test with special characters
        assert PathUtils.create_safe_filename("John Doe") == "John_Doe"
        assert PathUtils.create_safe_filename("A.B.C") == "A_B_C"
        assert PathUtils.create_safe_filename("Test@123") == "Test_123"

        # Test with already safe name
        assert PathUtils.create_safe_filename("SafeName123") == "SafeName123"

    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "subdir", "test.txt")
            PathUtils.ensure_directory_exists(test_path)
            assert os.path.exists(os.path.dirname(test_path))


class TestForceRegenerationTracker:
    """Test cases for ForceRegenerationTracker class."""

    def test_mark_and_check_force_regeneration(self):
        """Test marking and checking force regeneration status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = os.path.join(tmpdir, "test.json")

            # Initially should not be marked
            assert not ForceRegenerationTracker.is_force_regenerated(json_file)

            # Mark as force regenerated
            ForceRegenerationTracker.mark_as_force_regenerated(json_file)

            # Should now be marked
            assert ForceRegenerationTracker.is_force_regenerated(json_file)

            # Should have a timestamp
            timestamp = ForceRegenerationTracker.get_force_regenerated_timestamp(json_file)
            assert timestamp is not None
            assert timestamp != "Unknown"

    def test_get_timestamp_nonexistent(self):
        """Test getting timestamp for non-existent file."""
        timestamp = ForceRegenerationTracker.get_force_regenerated_timestamp("/nonexistent/file.json")
        assert timestamp is None


class TestConstants:
    """Test cases for Constants class."""

    def test_encodings_list(self):
        """Test encodings list is not empty."""
        assert len(Constants.ENCODINGS) > 0
        assert 'utf-8' in Constants.ENCODINGS

    def test_base_paths(self):
        """Test base path constants are defined."""
        assert Constants.BASE_PATH_STATE_ASSEMBLY is not None
        assert Constants.BASE_PATH_CANDIDATE_DATA is not None
        assert Constants.BASE_PATH_CONSTITUENCY_DATA is not None

    def test_batch_sizes(self):
        """Test batch size constants are positive."""
        assert Constants.DEFAULT_BATCH_SIZE > 0
        assert Constants.MAX_WORKERS > 0


# Integration tests (require network and external dependencies)
@pytest.mark.integration
class TestImageDownloader:
    """Integration test cases for ImageDownloader class."""

    def test_download_invalid_url(self):
        """Test downloading from invalid URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.jpg")
            result = ImageDownloader.download_image_from_url("not_a_url", output_path)
            assert result is False

    def test_download_with_empty_url(self):
        """Test downloading with empty URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.jpg")
            result = ImageDownloader.download_image_from_url("", output_path)
            assert result is False
