# from old_working_code_mp.candidate_link_crawler import candidatecrawler
# from old_working_code_mp.candidate_profile_craweler import candidate_link_crawler
#
#
# async def run_crawler_for_years(years):
#     for year in years:
#         print(f"\n=== Processing year {year} ===\n")
#         await candidatecrawler(year=year)
#
#
# if __name__ == "__main__":
#     # asyncio.run(customcrawler())
#     # years_to_process = [2024, 2019, 2014, 2009, 2004]
#     # asyncio.run(run_crawler_for_years(years_to_process))
#     # extract_candidate_tables_to_csv()
#     #  candidate_link_crawler(year=2024)
#     years_to_process = [2019, 2014, 2009, 2004]
#
#     # Process each year sequentially
#     for year in years_to_process:
#         print(f"\n=== Processing year {year} ===\n")
#         candidate_link_crawler(year=year,winners_only=True)


# main.py
"""
Main entry point for the election data extraction system with support for existing folder structures
"""
import asyncio
from typing import Optional

from config.election_config import detect_election_type, get_config_by_name, ELECTION_CONFIGS
from utils.file_manager import ElectionFileManager
from crawlers.constituency_crawler import ConstituencyCrawler
from crawlers.candidate_crawler import CandidateCrawler


class ElectionDataExtractor:
    """Main class for election data extraction supporting both folder structures"""

    def __init__(self):
        self.file_manager = ElectionFileManager()

    async def extract_constituencies(self, url: str, election_type: Optional[str] = None):
        """Extract constituency links from a given URL"""
        # Detect or get election configuration
        if election_type:
            config = get_config_by_name(election_type)
            if not config:
                print(f"Unknown election type: {election_type}")
                print(f"Available types: {list(ELECTION_CONFIGS.keys())}")
                return
        else:
            config = detect_election_type(url)
            if not config:
                print("Could not detect election type from URL")
                print("Please specify election_type parameter")
                return

        print(f"Using configuration for: {config.name}")
        print(f"Data will be stored in: {config.get_base_folder_path('2024')}")

        # Create and run constituency crawler
        crawler = ConstituencyCrawler(config, self.file_manager)
        return await crawler.crawl_constituencies(url)

    async def extract_candidates(self, year: str, election_type: str, state_filter: Optional[str] = None):
        """Extract candidate data for a specific year and election type"""
        config = get_config_by_name(election_type)
        if not config:
            print(f"Unknown election type: {election_type}")
            print(f"Available types: {list(ELECTION_CONFIGS.keys())}")
            return

        print(f"Extracting {config.name} candidates for {year}")
        if config.constituency_type == "lok_sabha":
            print(f"Using folder structure: constituency_data/{year}/")
        else:
            print(f"Using folder structure: state_assembly/{config.state_name}/")

        # Create and run candidate crawler
        crawler = CandidateCrawler(config, self.file_manager)
        await crawler.crawl_candidates(year, state_filter)


# Convenience functions for direct usage
async def extract_constituencies(url: str, election_type: Optional[str] = None):
    """Convenience function to extract constituencies"""
    extractor = ElectionDataExtractor()
    return await extractor.extract_constituencies(url, election_type)


async def extract_candidates(year: str, election_type: str, state_filter: Optional[str] = None):
    """Convenience function to extract candidates"""
    extractor = ElectionDataExtractor()
    return await extractor.extract_candidates(year, election_type, state_filter)


# Usage examples for direct execution
async def demo_andhra_pradesh():
    """Demo: Extract Andhra Pradesh Assembly data"""
    print("=== ANDHRA PRADESH ASSEMBLY DEMO ===")

    extractor = ElectionDataExtractor()

    # Extract constituency links
    print("Step 1: Extracting constituency links...")
    await extractor.extract_constituencies(
        "https://www.myneta.info/AndhraPradesh2024/",
        election_type="andhra_pradesh"
    )

    # Extract candidate data
    print("Step 2: Extracting candidate data...")
    await extractor.extract_candidates("2024", "andhra_pradesh")

    print("Demo completed! Check state_assembly/ANDHRA PRADESH/ folder")


async def demo_lok_sabha():
    """Demo: Extract Lok Sabha data (maintains existing structure)"""
    print("=== LOK SABHA DEMO ===")

    extractor = ElectionDataExtractor()

    # Extract constituency links
    print("Step 1: Extracting constituency links...")
    await extractor.extract_constituencies(
        "https://www.myneta.info/LokSabha2024/",
        election_type="lok_sabha"
    )

    # Extract candidate data for specific state
    print("Step 2: Extracting candidate data for Karnataka...")
    await extractor.extract_candidates("2024", "lok_sabha", state_filter="KARNATAKA")

    print("Demo completed! Check constituency_data/2024/ folder")


def show_usage():
    """Show usage examples"""
    print("🚀 ELECTION DATA EXTRACTION SYSTEM")
    print("=" * 50)
    print()

    print("📋 BASIC USAGE:")
    print("from main import ElectionDataExtractor")
    print()
    print("extractor = ElectionDataExtractor()")
    print("await extractor.extract_constituencies(url, election_type)")
    print("await extractor.extract_candidates(year, election_type)")
    print()

    print("🏛️ SUPPORTED ELECTION TYPES:")
    for key, config in ELECTION_CONFIGS.items():
        print(f"   - {key}: {config.name}")
    print()

    print("💻 CLI USAGE:")
    print("python cli.py constituencies --url 'URL' --election-type TYPE")
    print("python cli.py candidates --year YEAR --election-type TYPE")
    print("python cli.py csv --election-type TYPE")
    print("python cli.py profiles --csv-path 'PATH' --election-type TYPE")
    print()

    print("📁 FOLDER STRUCTURES:")
    print("Lok Sabha: constituency_data/{year}/{state}/{district}/")
    print("Assembly:  state_assembly/{state_name}/{district}/")
    print()

    print("🏷️ FILE NAMING:")
    print("MP files:  {candidate_name}.json")
    print("MLA files: {candidate_name}_mla.json")


# Main execution for testing and demos
async def main():
    """Main function for direct execution"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "demo-ap":
            await demo_andhra_pradesh()
        elif command == "demo-ls":
            await demo_lok_sabha()
        elif command == "help":
            show_usage()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: demo-ap, demo-ls, help")
    else:
        print("🎯 ELECTION DATA EXTRACTION SYSTEM")
        print("=" * 40)
        print()
        print("Choose an option:")
        print("1. Demo Andhra Pradesh Assembly extraction")
        print("2. Demo Lok Sabha extraction")
        print("3. Show usage information")
        print("4. Exit")
        print()

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            await demo_andhra_pradesh()
        elif choice == "2":
            await demo_lok_sabha()
        elif choice == "3":
            show_usage()
        elif choice == "4":
            print("Goodbye!")
        else:
            print("Invalid choice. Showing usage information:")
            show_usage()


if __name__ == "__main__":
    asyncio.run(main())