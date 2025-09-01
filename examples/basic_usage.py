"""
Basic usage examples for the refactored election data crawler.
Shows how to use the new modular components.
"""
import asyncio
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.mp_crawler import MPCrawler
from crawler.mla_crawler import MLACrawler
from utils.csv_processor import CSVProcessor
from utils.file_manager import FileManager
from utils.image_processor import ImageProcessor
from models.candidate import Candidate, CandidateCollection


async def example_mp_crawling():
    """Example: Crawl MP (Lok Sabha) election data."""
    print("=== MP Crawling Example ===")
    
    # Initialize MP crawler for 2024 elections
    mp_crawler = MPCrawler(year=2024, batch_size=20)  # Smaller batch for example
    
    # 1. Crawl constituency links
    print("Step 1: Crawling constituency links...")
    constituency_links = await mp_crawler.crawl_constituency_links()
    print(f"Found {len(constituency_links)} constituency links")
    
    if constituency_links:
        # Take only first 3 for demonstration
        demo_links = constituency_links[:3]
        print(f"Using first 3 links for demo: {demo_links}")
        
        # 2. Crawl candidates from constituencies
        print("\nStep 2: Crawling candidates...")
        stats = await mp_crawler.crawl_candidates_from_constituencies(demo_links, winners_only=True)
        print(f"Crawling stats: {stats}")


async def example_mla_crawling():
    """Example: Crawl MLA (State Assembly) election data."""
    print("\n=== MLA Crawling Example ===")
    
    # Initialize MLA crawler for Karnataka 2023
    mla_crawler = MLACrawler(state="Karnataka", year=2023, batch_size=20)
    
    # 1. Get state assembly URL
    state_url = mla_crawler.get_state_assembly_url()
    print(f"State assembly URL: {state_url}")
    
    # 2. Crawl state assembly page
    print("Step 1: Crawling state assembly page...")
    content = await mla_crawler.crawl_state_assembly_page(state_url)
    
    if content:
        print(f"Retrieved content length: {len(content)} characters")
        
        # 3. Try to crawl winners
        print("\nStep 2: Crawling winners...")
        winners_url = mla_crawler.get_winners_url_for_year()
        print(f"Winners URL: {winners_url}")
        
        stats = await mla_crawler.crawl_winners_from_state(winners_url)
        print(f"Winners crawling stats: {stats}")


def example_csv_processing():
    """Example: Process CSV files using utilities."""
    print("\n=== CSV Processing Example ===")
    
    # 1. Find CSV files in a directory
    csv_files = CSVProcessor.find_csv_files("candidate_data", "*.csv")
    print(f"Found {len(csv_files)} CSV files")
    
    if csv_files:
        # Take first file for demonstration
        csv_file = csv_files[0]
        print(f"Processing file: {csv_file}")
        
        # 2. Read candidate data
        candidates_data = CSVProcessor.read_candidate_data(csv_file)
        print(f"Read {len(candidates_data)} candidate records")
        
        # 3. Get statistics
        stats = CSVProcessor.get_csv_statistics(csv_file)
        print(f"File statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 4. Extract candidate URLs
        candidate_urls = CSVProcessor.extract_candidate_urls(csv_file, winners_only=True)
        print(f"Found {len(candidate_urls)} candidate URLs")


def example_file_management():
    """Example: File management utilities."""
    print("\n=== File Management Example ===")
    
    # 1. Create safe filename
    candidate_name = "John Doe (Independent) - Special Characters!@#"
    safe_name = FileManager.create_safe_filename(candidate_name)
    print(f"Original name: {candidate_name}")
    print(f"Safe filename: {safe_name}")
    
    # 2. Create candidate directory
    base_dir = "example_data"
    candidate_dir = FileManager.create_candidate_directory(base_dir, candidate_name)
    print(f"Created directory: {candidate_dir}")
    
    # 3. Find files by pattern
    py_files = FileManager.find_files_by_pattern(".", "*.py")
    print(f"Found {len(py_files)} Python files in current directory")
    
    # 4. Check if files exist
    example_file = "main.py"
    exists = FileManager.file_exists_and_not_empty(example_file)
    print(f"File '{example_file}' exists and not empty: {exists}")


def example_candidate_models():
    """Example: Using candidate data models."""
    print("\n=== Candidate Models Example ===")
    
    # 1. Create candidate from dictionary data
    candidate_data = {
        'name': 'John Doe',
        'constituency': 'Example Constituency',
        'party': 'Example Party',
        'year': 2024,
        'election_type': 'mp',
        'is_winner': 'yes',
        'votes_received': '50000',
        'profile_url': 'https://example.com/john-doe'
    }
    
    candidate = Candidate.from_dict(candidate_data)
    print(f"Created candidate: {candidate.get_display_name()}")
    print(f"Is winner: {candidate.is_winner}")
    print(f"Votes: {candidate.votes_received}")
    
    # 2. Create candidate collection
    collection = CandidateCollection()
    collection.add_candidate(candidate)
    
    # Add another candidate
    candidate2_data = {
        'name': 'Jane Smith',
        'constituency': 'Another Constituency',
        'party': 'Another Party',
        'year': 2024,
        'election_type': 'mp',
        'is_winner': 'no',
        'votes_received': '30000'
    }
    
    candidate2 = Candidate.from_dict(candidate2_data)
    collection.add_candidate(candidate2)
    
    # 3. Get collection statistics
    stats = collection.get_statistics()
    print(f"Collection statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 4. Filter winners
    winners = collection.get_winners()
    print(f"Winners in collection: {len(winners)}")
    
    # 5. Convert to CSV data
    csv_data = collection.to_csv_data()
    print(f"CSV data rows: {len(csv_data)}")


async def example_image_processing():
    """Example: Image processing utilities."""
    print("\n=== Image Processing Example ===")
    
    # Example markdown content with images
    markdown_content = """
    # Candidate Profile
    
    ![Profile Image](https://example.com/profile.jpg)
    
    Some other content...
    
    <img src="https://example.com/another-image.png" alt="Another image" />
    """
    
    # 1. Extract image URLs
    image_urls = ImageProcessor.extract_image_urls_from_markdown(
        markdown_content, 
        base_url="https://example.com"
    )
    print(f"Found image URLs: {image_urls}")
    
    # 2. Get profile image
    profile_image = ImageProcessor.extract_profile_image_from_markdown(
        markdown_content,
        base_url="https://example.com"
    )
    print(f"Profile image URL: {profile_image}")
    
    # 3. Validate image URL
    valid_url = "https://example.com/image.jpg"
    invalid_url = "not-a-valid-url"
    
    print(f"'{valid_url}' is valid: {ImageProcessor.is_valid_image_url(valid_url)}")
    print(f"'{invalid_url}' is valid: {ImageProcessor.is_valid_image_url(invalid_url)}")
    
    # 4. Create candidate image path
    candidate_dir = "candidate_data/john_doe"
    image_path = ImageProcessor.create_candidate_image_path(candidate_dir, "John Doe")
    print(f"Candidate image path: {image_path}")


async def main():
    """Run all examples."""
    print("Election Data Crawler - Usage Examples")
    print("=" * 50)
    
    try:
        # File operations examples (sync)
        example_csv_processing()
        example_file_management()
        example_candidate_models()
        await example_image_processing()
        
        # Crawler examples (async) - commented out to avoid actual web requests
        print("\n" + "=" * 50)
        print("Note: Web crawling examples are commented out to avoid making actual requests.")
        print("Uncomment the lines below to test actual crawling functionality:")
        print("# await example_mp_crawling()")
        print("# await example_mla_crawling()")
        
        # Uncomment these lines to test actual crawling:
        # await example_mp_crawling()
        # await example_mla_crawling()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())