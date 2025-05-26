import asyncio
import csv
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler

from ai_csv_generation import generate
from md_file_reader import get_constituency_csv_file
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type


async def crawl_link_from_csv(csv_path, winners_only=False, batch_size=50):
    """
    Read a CSV file and extract candidate links.

    Args:
        csv_path: Path to the CSV file
        :param csv_path:
        :param batch_size:
        :param winners_only:
    """

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium",
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        session_id="session_id_candidate",
    )

    candidate_dict_link_with_name = {}
    output_dir = os.path.dirname(csv_path)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if winners_only and row[11].strip().lower() != 'yes':
                continue
            # Assuming the first column contains the candidate name and the second column contains the link
            candidate_name = row[4]
            candidate_link = row[12]
            # Validate that the link is a proper HTTP/HTTPS URL
            if candidate_link and isinstance(candidate_link, str) and (
                    candidate_link.startswith('http://') or candidate_link.startswith('https://')):
                candidate_dict_link_with_name[candidate_name] = candidate_link
            # candidate_dict_link_with_name[candidate_name] = candidate_link

    print(f"Found {len(candidate_dict_link_with_name)} candidate links in {csv_path}")

    # Process candidates in batches
    candidates = list(candidate_dict_link_with_name.items())
    batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Process batches of candidates in parallel
        for batch_num, batch in enumerate(batches, 1):
            print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")

            # Create tasks for the batch
            tasks = []
            for candidate_name, candidate_link in batch:
                # Create a safe folder name
                safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
                candidate_dir = os.path.join(output_dir, safe_name)
                os.makedirs(candidate_dir, exist_ok=True)
                json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")

                # Check if the JSON file already exists and is not empty
                if os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
                    print(f"Skipping {candidate_name}: JSON file already exists")
                    continue  # Skip to the next candidate

                # Create task for processing this candidate
                task = process_candidate(crawler, candidate_name, candidate_link,
                                         json_output_file, run_config, )
                tasks.append(task)

            # Wait for all tasks in this batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process the results - log any exceptions
            for candidate_name, result in zip([c[0] for c in batch], results):
                if isinstance(result, Exception):
                    print(f"Error processing {candidate_name}: {result}")


async def process_candidate(crawler, candidate_name, candidate_link, json_output_file, run_config, ):
    """Process a single candidate and extract their data."""
    try:
        print(f"Processing candidate: {candidate_name} ({candidate_link})")

        # Fetch the candidate page
        result = await crawler.arun(candidate_link, config=run_config)
        print(f"Extracted data for {candidate_name}")

        # Extract markdown content as string
        markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)

        # Generate JSON in a separate process to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=10) as executor:
            await loop.run_in_executor(
                executor,
                generate_wrapper,
                markdown_content,
                json_output_file
            )

        print(f"JSON saved to: {json_output_file}")
        return True


    except Exception as e:
        print(f"Error processing {candidate_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception)  # You can specify specific exceptions here
)
def generate_with_retry(markdown_content, output_file):
    """Function that calls generate with retry logic using tenacity."""
    generate(markdown_content, output_file)


def generate_wrapper(markdown_content: str, output_file: str):
    """
    Wrapper function that handles the generate call safely with tenacity retry logic.
    This function runs in a separate thread/process.
    """
    try:
        # Call the generate function with retry logic
        generate_with_retry(markdown_content, output_file)
        print(f"Successfully generated JSON for {output_file}")
    except Exception as e:
        print(f"Error in generate_wrapper after all retries: {e}")
        # Save error information to a file for debugging
        error_file = output_file.replace('.json', '_error.txt')
        with open(error_file, 'w') as f:
            f.write(f"Error after all retries: {str(e)}\n")
            f.write(f"Content length: {len(markdown_content)}\n")


def candidate_link_crawler(year, winners_only):
    """
    Process all constituencies for a given year.

    Args:
        year: The election year to process
        :param winners_only:
    """
    states_and_districts = discover_states_and_districts(year)

    if not states_and_districts:
        print(f"No data found for year {year}")
        return

    print(f"\n=== Found {len(states_and_districts)} states for year {year} ===\n")

    total_districts = sum(len(districts) for districts in states_and_districts.values())
    processed = 0

    for state, districts in states_and_districts.items():
        print(f"\nProcessing state: {state} ({len(districts)} districts)")

        for district in districts:
            processed += 1
            csv_path = get_constituency_csv_file(year=year, state=state, district=district)

            if csv_path:
                print(f"[{processed}/{total_districts}] Processing {district} in {state}")
                print("CSV file found:", csv_path)
                asyncio.run(crawl_link_from_csv(csv_path, winners_only=winners_only), )

                # Uncomment the next line to stop after processing 1 district for demonstration
                # if processed > 0:
                #     print("Stopping after processing 1 districts for demonstration.")
                #     return
            else:
                print(f"[{processed}/{total_districts}] No CSV file found for {district} in {state}")


def discover_states_and_districts(year):
    """
    Discover all available states and districts for a given year.

    Args:
        year: The election year (integer or string)

    Returns:
        Dictionary mapping states to lists of districts
    """
    base_folder = "constituency_data"
    year_str = str(year)

    # Get the year folder path
    year_folder = os.path.join(base_folder, year_str)
    if not os.path.exists(year_folder):
        print(f"No data found for year {year}")
        return {}

    # Get all state folders
    state_folders = [f for f in os.listdir(year_folder)
                     if os.path.isdir(os.path.join(year_folder, f))]

    result = {}
    for state in state_folders:
        state_path = os.path.join(year_folder, state)

        # Get all district folders within this state
        district_folders = [f for f in os.listdir(state_path)
                            if os.path.isdir(os.path.join(state_path, f))]

        result[state] = district_folders

    return result
