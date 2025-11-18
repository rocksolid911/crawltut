"""
Shared test fixtures and configuration for pytest.
"""

import pytest
import tempfile
import os


@pytest.fixture
def temp_dir():
    """
    Provides a temporary directory for tests.
    Automatically cleaned up after test completion.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_csv_data():
    """
    Provides sample CSV data for testing.
    """
    return [
        ['sno', 'name', 'constituency', 'party', 'criminal_cases', 'education', 'total_assets', 'liabilities',
         'candidate_url'],
        ['1', 'John Doe', 'District 1', 'Party A', '0', 'Graduate', '1000000', '50000',
         'https://example.com/candidate1'],
        ['2', 'Jane Smith', 'District 2', 'Party B', '1', 'Post Graduate', '2000000', '100000',
         'https://example.com/candidate2'],
    ]


@pytest.fixture
def sample_markdown_content():
    """
    Provides sample markdown content for testing.
    """
    return """
### List of Winners in Test State 2024

Sno | Candidate | Constituency | Party | Criminal Case | Education | Total Assets | Liabilities
---|---|---|---|---|---|---|---
1 | [](https://example.com/candidate1)[John Doe](https://example.com/candidate1) | District 1 | Party A | 0 | Graduate | Rs 10,00,000 ~ 10 Lacs+ | Rs 50,000 ~ 50 Thousand+
2 | [](https://example.com/candidate2)[Jane Smith](https://example.com/candidate2) | District 2 | Party B | **1** | Post Graduate | Rs 20,00,000 ~ 20 Lacs+ | Rs 1,00,000 ~ 1 Lac+
"""


@pytest.fixture
def mock_browser_config():
    """
    Provides a mock browser configuration for testing.
    """
    from src.utils.common_utils import CrawlerConfig
    return CrawlerConfig.get_browser_config()


@pytest.fixture
def mock_run_config():
    """
    Provides a mock run configuration for testing.
    """
    from src.utils.common_utils import CrawlerConfig
    return CrawlerConfig.get_run_config("test_session")
