# Election Data Crawler

A comprehensive Python application for crawling and extracting election candidate data from [MyNeta.info](https://www.myneta.info/) for both MP (Lok Sabha) and MLA (State Assembly) elections in India.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Automated Web Crawling**: Extract candidate data from MyNeta.info for all Indian states
- **Multi-Level Support**: Handles both MP (Lok Sabha) and MLA (State Assembly) elections
- **Historical Data**: Process election data from multiple years (2004, 2009, 2014, 2019, 2024)
- **Image Extraction**: Automatically downloads candidate profile images
- **JSON Generation**: Converts candidate data into structured JSON format using AI
- **Bye-Elections Support**: Separately handles bye-election data
- **Force Regeneration**: Smart regeneration logic to avoid redundant processing
- **Batch Processing**: Efficient parallel processing with configurable batch sizes
- **Error Handling**: Robust error handling with retry logic and detailed logging

## 📁 Project Structure

```
crawltut/
├── src/                          # Source code (new organized structure)
│   ├── crawlers/                # Web crawling modules
│   ├── extractors/              # Data extraction modules
│   ├── parsers/                 # Content parsing modules
│   └── utils/                   # Common utilities
│       └── common_utils.py     # Shared utility functions
│
├── old_working_code_mp/         # Legacy MP election code
│   ├── candidate_profile_crawler.py
│   ├── candidate_link_crawler.py
│   ├── ai_csv_generation.py
│   └── ...
│
├── tests/                       # Test suite
│   ├── test_common_utils.py
│   └── conftest.py
│
├── state_assembly/              # State assembly CSV data
├── candidate_data/              # Generated candidate JSON/images
├── constituency_data/           # Constituency-level data
│
├── assembly_state_wise_winner_link_crawler.py
├── candidate_url_extractor.py
├── candidate_image_crawler.py
├── mla_candidate_image_extractor.py
├── main.py                      # Main entry point
│
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd crawltut
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # For production use
   pip install -r requirements.txt

   # For development
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (if required for AI generation)
   ```

## 📖 Usage

### Basic Usage

#### 1. Extract MLA (State Assembly) Candidate Data

```python
# Run the main script
python main.py
```

This will:
- Find all CSV files with candidate data
- Extract candidate profile URLs
- Crawl candidate pages
- Generate JSON files with detailed information
- Download candidate images

#### 2. Extract MP (Lok Sabha) Candidate Data

```python
from old_working_code_mp.candidate_link_crawler import candidate_link_crawler

# Process all years
candidate_link_crawler(year=2024, winners_only=False)
candidate_link_crawler(year=2019, winners_only=True)
```

#### 3. Extract Candidate URLs from CSV Files

```python
from candidate_url_extractor import extract_all_candidate_urls

# Extract all URLs
results = extract_all_candidate_urls("state_assembly")
print(f"Found {results['total_candidates']} candidates")
print(f"Total URLs: {len(results['urls'])}")
```

#### 4. Download Profile Images

```python
from mla_candidate_image_extractor import extract_and_download_profile_images
import asyncio

# Download missing images
asyncio.run(extract_and_download_profile_images())
```

### Advanced Usage

#### Force Regenerate JSON Files

```python
import asyncio
from candidate_url_extractor import process_candidate_data

# Regenerate all JSON files (skip already regenerated ones)
asyncio.run(process_candidate_data(
    force_regenerate_json=True,
    skip_if_force_regenerated=True
))
```

#### Process Specific State/Year

```python
from old_working_code_mp.candidate_link_crawler import candidate_link_crawler

# Process specific year with custom settings
candidate_link_crawler(
    year=2024,
    winners_only=False,          # Process all candidates
    force_regenerate_json=True,   # Regenerate existing files
    skip_if_force_regenerated=True  # Skip already regenerated
)
```

## ⚙️ Configuration

### Common Configuration Options

The `src/utils/common_utils.py` module contains configurable constants:

```python
class Constants:
    # File encodings
    ENCODINGS = ['utf-8', 'latin-1', 'cp1252']

    # Base paths
    BASE_PATH_STATE_ASSEMBLY = "state_assembly"
    BASE_PATH_CANDIDATE_DATA = "candidate_data"

    # Performance settings
    DEFAULT_BATCH_SIZE = 50
    MAX_WORKERS = 10
    MAX_RETRIES = 5
```

### Browser Configuration

```python
from src.utils.common_utils import CrawlerConfig

# Get browser config
browser_config = CrawlerConfig.get_browser_config(
    headless=True,           # Run in headless mode
    browser_type="chromium"  # Use Chromium browser
)

# Get run config
run_config = CrawlerConfig.get_run_config(
    session_id="my_session",
    cache_mode=CacheMode.BYPASS  # Bypass cache
)
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests (may require network)
pytest -m integration

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Run Tests in Parallel

```bash
pytest -n auto
```

## 👨‍💻 Development

### Code Style

This project follows PEP 8 style guidelines. Format your code with:

```bash
# Format code
black .

# Sort imports
isort .

# Check code style
flake8 .

# Type checking
mypy src/
```

### Pre-commit Checks

Before committing, run:

```bash
# Format and check code
black . && isort . && flake8 . && pytest
```

## 📊 Data Structure

### Output Files

#### CSV Files
- Location: `state_assembly/{State}/{Year}/{State}_{Year}_winners.csv`
- Contains: Candidate names, constituencies, parties, URLs, etc.

#### JSON Files
- Location: `candidate_data/{Year}/{State}/{CandidateName}/{CandidateName}.json`
- Contains: Detailed candidate information (education, assets, criminal cases, etc.)

#### Image Files
- Location: `candidate_data/{Year}/{State}/{CandidateName}/{CandidateName}.jpg`
- Format: JPEG
- Type: Candidate profile photos

### Sample JSON Structure

```json
{
  "name": "John Doe",
  "constituency": "District 1",
  "party": "Party Name",
  "criminal_cases": 0,
  "education": "Graduate",
  "total_assets": "Rs 10,00,000",
  "liabilities": "Rs 50,000",
  "url": "https://www.myneta.info/..."
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root and virtual environment is activated
   pip install -r requirements.txt
   ```

2. **Browser Issues**
   ```bash
   # Install Playwright browsers
   playwright install chromium
   ```

3. **Memory Issues with Large Datasets**
   - Reduce `DEFAULT_BATCH_SIZE` in `common_utils.py`
   - Process one state/year at a time

4. **Network Timeouts**
   - Check internet connection
   - Increase retry count in `Constants.MAX_RETRIES`

## 📝 TODO / Roadmap

- [ ] Complete migration to new `src/` package structure
- [ ] Add comprehensive logging with `logging` module
- [ ] Implement caching for API requests
- [ ] Add CLI interface with argparse
- [ ] Create database storage option (SQLite/PostgreSQL)
- [ ] Add data validation and sanitization
- [ ] Implement rate limiting for respectful crawling
- [ ] Add progress bars for long-running operations
- [ ] Create web dashboard for visualization
- [ ] Add Docker support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Data source: [MyNeta.info](https://www.myneta.info/) - Association for Democratic Reforms (ADR)
- Web crawling: [Crawl4AI](https://github.com/unclecode/crawl4ai)
- All contributors and maintainers

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This tool is for educational and research purposes. Please respect the terms of service of myneta.info and practice responsible web crawling.
