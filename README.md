# Indian Election Data Scraper

A production-ready web scraper for collecting comprehensive election data about Indian political candidates from myneta.info. This tool extracts information about both Member of Parliament (MP) and Member of Legislative Assembly (MLA) candidates across multiple election years.

## Features

- **Comprehensive Data Collection**: Scrapes candidate profiles including name, party, constituency, criminal cases, education, assets, and liabilities
- **Image Download**: Automatically downloads candidate profile images
- **Dual Coverage**: Supports both MP (Lok Sabha) and MLA (State Assembly) elections
- **Multi-Year Support**: Process data from elections spanning 2004-2024
- **Async/Concurrent Processing**: Fast parallel processing with configurable batch sizes
- **Robust Error Handling**: Retry logic with exponential backoff for network failures
- **Production-Ready**: Modular, reusable components with comprehensive logging
- **Flexible Configuration**: Easy-to-use configuration system

## Project Structure

```
crawltut/
├── config/                      # Configuration management
│   └── settings.py              # Crawler and scraper settings
├── src/                         # Source code
│   ├── crawlers/                # Crawler implementations
│   │   ├── base_crawler.py      # Base crawler class
│   │   ├── mp_crawler.py        # MP (Parliament) crawler
│   │   └── mla_crawler.py       # MLA (Assembly) crawler
│   ├── parsers/                 # Data parsers
│   │   ├── constituency_parser.py
│   │   └── json_generator.py
│   ├── extractors/              # Data extractors
│   │   └── image_extractor.py
│   ├── utils/                   # Utility functions
│   │   ├── csv_utils.py
│   │   ├── file_utils.py
│   │   └── logger.py
│   └── models/                  # Data models
│       └── candidate.py
├── scripts/                     # Executable scripts
│   ├── run_mp_crawler.py        # Run MP crawler
│   └── run_mla_crawler.py       # Run MLA crawler
├── old_working_code_mp/         # Legacy MP crawler (production-tested)
├── data/                        # Data output directory
├── logs/                        # Log files
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Chrome or Chromium (for web crawling)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd crawltut
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install playwright browsers** (required for crawl4ai):
   ```bash
   playwright install chromium
   ```

## Usage

### Running the MP (Parliament) Crawler

The MP crawler collects data about Lok Sabha (Parliament) candidates.

#### Basic Usage

```bash
# Crawl 2024 election data (all candidates)
python scripts/run_mp_crawler.py --year 2024

# Crawl multiple years
python scripts/run_mp_crawler.py --years 2024 2019 2014

# Crawl all available years (2004-2024)
python scripts/run_mp_crawler.py --all-years
```

#### Advanced Options

```bash
# Crawl only winners
python scripts/run_mp_crawler.py --year 2024 --winners-only

# Force regenerate JSON files (useful for updates)
python scripts/run_mp_crawler.py --year 2024 --force-regenerate

# Process only winners for previous years (recommended)
python scripts/run_mp_crawler.py --years 2019 2014 2009 2004 --winners-only
```

#### MP Crawler Arguments

- `--year YEAR`: Process a single election year
- `--years YEAR [YEAR ...]`: Process multiple election years
- `--all-years`: Process all available years (2004, 2009, 2014, 2019, 2024)
- `--winners-only`: Only process election winners (reduces data size for historical elections)
- `--force-regenerate`: Force regenerate JSON files even if they already exist
- `--no-skip-force-regenerated`: Don't skip candidates that were already force-regenerated

### Running the MLA (State Assembly) Crawler

The MLA crawler collects data about State Legislative Assembly candidates.

#### Basic Usage

```bash
# Crawl all states
python scripts/run_mla_crawler.py --all-states

# Crawl a single state
python scripts/run_mla_crawler.py --state "Maharashtra"

# Crawl multiple states
python scripts/run_mla_crawler.py --states "Maharashtra" "Karnataka" "Tamil Nadu"
```

#### MLA Crawler Arguments

- `--state STATE`: Process a single state
- `--states STATE [STATE ...]`: Process multiple states
- `--all-states`: Process all available states
- `--output-dir DIR`: Output directory for state assembly data (default: state_assembly)

#### Available States

Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chattisgarh, Delhi, Goa, Gujarat, Haryana, Himachal Pradesh, Jammu And Kashmir, Jharkhand, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Puducherry, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttarakhand, Uttar Pradesh, West Bengal

## Data Output

### Directory Structure

```
constituency_data/               # MP constituency data
├── 2024/
│   ├── STATE_NAME/
│   │   └── DISTRICT_NAME/
│   │       ├── constituency.csv    # Candidate list
│   │       └── CANDIDATE_NAME/     # Individual profiles
│   │           ├── candidate.json
│   │           └── candidate.jpg

state_assembly/                  # MLA state assembly data
├── STATE_NAME/
│   ├── 2024/
│   │   ├── candidates.csv
│   │   └── CANDIDATE_NAME/
│   │       ├── candidate.json
│   │       └── candidate.jpg

logs/                            # Application logs
missing_profile_images.csv       # Missing MP images log
missing_profile_images_mla.csv   # Missing MLA images log
```

### Data Fields

Each candidate JSON file contains:

- **name**: Candidate name
- **constituency**: Electoral constituency
- **party**: Political party affiliation
- **criminal_cases**: Number of criminal cases
- **education**: Educational qualification
- **total_assets**: Total declared assets
- **liabilities**: Total declared liabilities
- **url**: Source URL on myneta.info
- **election_type**: Type of election (main_election, bye_election)
- **is_winner**: Whether the candidate won
- **state**: State name (for MLAs)
- **year**: Election year

## Configuration

### Modifying Crawler Settings

Edit `config/settings.py` to customize:

```python
@dataclass
class CrawlerConfig:
    headless: bool = True              # Browser headless mode
    batch_size: int = 50               # Parallel processing batch size
    delay_between_requests: int = 2    # Delay in seconds
    max_retries: int = 5               # Maximum retry attempts
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# API keys (if using AI features)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## Features in Detail

### Concurrent Processing

The scraper processes multiple candidates in parallel using asyncio, with configurable batch sizes to balance speed and resource usage.

### Retry Logic

Network failures are handled with exponential backoff retry logic, ensuring reliable data collection even with intermittent connectivity.

### Image Extraction

Profile images are automatically extracted from multiple HTML patterns and downloaded in JPEG format.

### Force Regeneration

Use `--force-regenerate` to update existing data. The system tracks force-regenerated files to avoid redundant processing.

### Missing Data Tracking

Missing profile images are logged to CSV files (`missing_profile_images.csv` and `missing_profile_images_mla.csv`) for later review.

## Development

### Project Architecture

The project follows a modular architecture with:

- **Base Crawler**: Abstract base class providing common crawling functionality
- **Specialized Crawlers**: MP and MLA crawlers extending the base
- **Parsers**: Extract structured data from markdown/HTML
- **Extractors**: Handle specific data extraction tasks (e.g., images)
- **Utils**: Reusable utility functions for files, CSV, logging

### Adding a New Crawler

1. Create a new crawler class extending `BaseCrawler`
2. Implement the `run()` method
3. Add a script in `scripts/` for easy execution

### Running Tests

```bash
pytest tests/
```

## Troubleshooting

### Common Issues

**Issue**: `playwright` browser not found
**Solution**: Run `playwright install chromium`

**Issue**: Rate limiting or blocks from myneta.info
**Solution**: Increase `delay_between_requests` in `config/settings.py`

**Issue**: Out of memory errors
**Solution**: Reduce `batch_size` in configuration

**Issue**: Missing images
**Solution**: Check `missing_profile_images.csv` for details; some candidates may not have profile images

## Best Practices

1. **Start Small**: Test with a single year or state before processing all data
2. **Winners Only for Historical Data**: Use `--winners-only` for years before 2024 to reduce data volume
3. **Regular Backups**: Back up your data regularly, especially before force-regeneration
4. **Monitor Logs**: Check the `logs/` directory for processing status and errors
5. **Respect Rate Limits**: Don't reduce delays too much to avoid being blocked

## Data Ethics

This tool is designed for:
- Academic research
- Political transparency initiatives
- Data journalism
- Public interest analysis

**Please use responsibly**:
- Respect the source website's terms of service
- Don't overload servers with excessive requests
- Attribute data sources appropriately
- Follow applicable data protection regulations

## License

[Specify your license here]

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description of changes

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review log files for error details

## Acknowledgments

- Data source: [myneta.info](https://myneta.info)
- Built with [crawl4ai](https://github.com/unclecode/crawl4ai)

## Changelog

### Version 2.0 (Latest)
- Reorganized into production-ready modular structure
- Added reusable base crawler components
- Implemented configuration management
- Created easy-to-use command-line scripts
- Enhanced error handling and logging
- Updated documentation

### Version 1.0
- Initial working implementation for MP and MLA data collection
