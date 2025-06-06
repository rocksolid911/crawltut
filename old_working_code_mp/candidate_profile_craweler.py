import asyncio
import csv
import glob
import io
import os
import re
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlparse

import aiohttp
import requests
from PIL import Image
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler


from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from old_working_code_mp.ai_csv_generation import generate
from old_working_code_mp.md_file_reader import get_constituency_csv_file


# async def crawl_link_from_csv(csv_path, winners_only=False, batch_size=50):
#     """
#     Read a CSV file and extract candidate links.
#
#     Args:
#         csv_path: Path to the CSV file
#         :param csv_path:
#         :param batch_size:
#         :param winners_only:
#     """
#
#     # Configure browser
#     browser_config = BrowserConfig(
#         headless=True,
#         browser_type="chromium",
#     )
#
#     run_config = CrawlerRunConfig(
#         cache_mode=CacheMode.BYPASS,
#         session_id="session_id_candidate",
#     )
#
#     candidate_dict_link_with_name = {}
#     output_dir = os.path.dirname(csv_path)
#
#     with open(csv_path, 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if winners_only and row[11].strip().lower() != 'yes':
#                 continue
#             # Assuming the first column contains the candidate name and the second column contains the link
#             candidate_name = row[4]
#             candidate_link = row[12]
#             # Validate that the link is a proper HTTP/HTTPS URL
#             if candidate_link and isinstance(candidate_link, str) and (
#                     candidate_link.startswith('http://') or candidate_link.startswith('https://')):
#                 candidate_dict_link_with_name[candidate_name] = candidate_link
#             # candidate_dict_link_with_name[candidate_name] = candidate_link
#
#     print(f"Found {len(candidate_dict_link_with_name)} candidate links in {csv_path}")
#
#     # Process candidates in batches
#     candidates = list(candidate_dict_link_with_name.items())
#     batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]
#
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         # Process batches of candidates in parallel
#         for batch_num, batch in enumerate(batches, 1):
#             print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")
#
#             # Create tasks for the batch
#             tasks = []
#             for candidate_name, candidate_link in batch:
#                 # Create a safe folder name
#                 safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
#                 candidate_dir = os.path.join(output_dir, safe_name)
#                 os.makedirs(candidate_dir, exist_ok=True)
#                 json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")
#
#                 # *** UPDATED: Check both JSON and image files ***
#                 image_file = os.path.join(candidate_dir, f"{safe_name}.jpg")
#
#                 json_exists = os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0
#                 image_exists = os.path.exists(image_file) and os.path.getsize(image_file) > 0
#
#                 if json_exists and image_exists:
#                     print(f"Skipping {candidate_name}: JSON and image files already exist")
#                     continue  # Skip to the next candidate
#                 elif json_exists and not image_exists:
#                     print(f"JSON exists for {candidate_name}, but missing image - will download image only")
#                 elif not json_exists and image_exists:
#                     print(f"Image exists for {candidate_name}, but missing JSON - will process JSON only")
#                 else:
#                     print(f"Processing {candidate_name}: Both JSON and image missing")
#                 # *** END UPDATED SECTION ***
#
#                 # Create task for processing this candidate
#                 task = process_candidate(crawler, candidate_name, candidate_link,
#                                          json_output_file, run_config, )
#                 tasks.append(task)
#
#             # Wait for all tasks in this batch to complete
#             results = await asyncio.gather(*tasks, return_exceptions=True)
#
#             # Process the results - log any exceptions
#             for candidate_name, result in zip([c[0] for c in batch], results):
#                 if isinstance(result, Exception):
#                     print(f"Error processing {candidate_name}: {result}")


# async def process_candidate(crawler, candidate_name, candidate_link, json_output_file, run_config, ):
#     """Process a single candidate and extract their data."""
#     try:
#         print(f"Processing candidate: {candidate_name} ({candidate_link})")
#
#         # Fetch the candidate page
#         result = await crawler.arun(candidate_link, config=run_config)
#         print(f"Extracted data for {candidate_name}")
#
#         # Extract markdown content as string
#         markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)
#
#         # Generate JSON in a separate process to avoid blocking the event loop
#         loop = asyncio.get_event_loop()
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             await loop.run_in_executor(
#                 executor,
#                 generate_wrapper,
#                 markdown_content,
#                 json_output_file
#             )
#
#         print(f"JSON saved to: {json_output_file}")
#         return True
#
#
#     except Exception as e:
#         print(f"Error processing {candidate_name}: {e}")
#         import traceback
#         traceback.print_exc()
#         return False

# Updated crawl_link_from_csv function
async def crawl_link_from_csv(csv_path, winners_only=False, batch_size=50, force_regenerate_json=False,
                              skip_if_force_regenerated=True):
    """
    Read a CSV file and extract candidate links.

    Args:
        csv_path: Path to the CSV file
        winners_only: Process only winners
        batch_size: Number of candidates to process in parallel
        force_regenerate_json: If True, regenerate JSON even if it already exists
        skip_if_force_regenerated: If True, skip candidates that were already force-regenerated
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
            candidate_name = row[4]
            candidate_link = row[12]
            if candidate_link and isinstance(candidate_link, str) and (
                    candidate_link.startswith('http://') or candidate_link.startswith('https://')):
                candidate_dict_link_with_name[candidate_name] = candidate_link

    print(f"Found {len(candidate_dict_link_with_name)} candidate links in {csv_path}")

    # Show force regenerate status
    if force_regenerate_json:
        if skip_if_force_regenerated:
            print(
                "🔄 FORCE REGENERATE JSON MODE: Will regenerate existing JSON files (skipping already force-regenerated)")
        else:
            print("🔄 FORCE REGENERATE JSON MODE: Will regenerate ALL existing JSON files")

    # Process candidates in batches
    candidates = list(candidate_dict_link_with_name.items())
    batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for batch_num, batch in enumerate(batches, 1):
            print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")

            tasks = []
            for candidate_name, candidate_link in batch:
                safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
                candidate_dir = os.path.join(output_dir, safe_name)
                os.makedirs(candidate_dir, exist_ok=True)
                json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")

                image_file = os.path.join(candidate_dir, f"{safe_name}.jpg")

                json_exists = os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0
                image_exists = os.path.exists(image_file) and os.path.getsize(image_file) > 0

                # Check if already force-regenerated
                already_force_regenerated = is_force_regenerated(json_output_file)

                # If force_regenerate_json is True, treat JSON as not existing (unless already force-regenerated and we should skip)
                if force_regenerate_json and not (skip_if_force_regenerated and already_force_regenerated):
                    json_exists = False

                if json_exists and image_exists:
                    if already_force_regenerated and force_regenerate_json and skip_if_force_regenerated:
                        timestamp = get_force_regenerated_timestamp(json_output_file)
                        print(f"Skipping {candidate_name}: Already force-regenerated on {timestamp}")
                    else:
                        print(f"Skipping {candidate_name}: JSON and image files already exist")
                    continue
                elif json_exists and not image_exists:
                    print(f"JSON exists for {candidate_name}, but missing image - will download image only")
                elif not json_exists and image_exists:
                    if force_regenerate_json:
                        if already_force_regenerated:
                            print(f"Force regenerating JSON again for {candidate_name} (image exists)")
                        else:
                            print(f"Force regenerating JSON for {candidate_name} (image exists)")
                    else:
                        print(f"Image exists for {candidate_name}, but missing JSON - will process JSON only")
                else:
                    if force_regenerate_json:
                        if already_force_regenerated:
                            print(f"Force regenerating both JSON and image again for {candidate_name}")
                        else:
                            print(f"Force regenerating both JSON and image for {candidate_name}")
                    else:
                        print(f"Processing {candidate_name}: Both JSON and image missing")

                # Create task for processing this candidate
                task = process_candidate(crawler, candidate_name, candidate_link,
                                         json_output_file, run_config, force_regenerate_json, skip_if_force_regenerated)
                tasks.append(task)

            # Wait for all tasks in this batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process the results - log any exceptions
            for candidate_name, result in zip([c[0] for c in batch], results):
                if isinstance(result, Exception):
                    print(f"Error processing {candidate_name}: {result}")


async def process_candidate(crawler, candidate_name, candidate_url, json_output_file, run_config,
                            force_regenerate_json=False, skip_if_force_regenerated=True):
    """Process a single candidate and extract their data."""
    try:
        print(f"🔍 Processing: {candidate_name} ({candidate_url})")

        # File paths and existence checks
        json_exists = os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0
        image_path = os.path.splitext(json_output_file)[0] + ".jpg"
        image_exists = os.path.exists(image_path) and os.path.getsize(image_path) > 0
        csv_path = get_csv_path_from_json(json_output_file)

        # Check if already force-regenerated
        already_force_regenerated = is_force_regenerated(json_output_file)

        # Determine what needs to be processed
        need_json = not json_exists or (
                    force_regenerate_json and not (skip_if_force_regenerated and already_force_regenerated))
        need_image = not image_exists

        # Skip if both exist and no force regeneration needed
        if json_exists and image_exists and not need_json:
            print(f"✅ Both JSON and image already exist for {candidate_name} - skipping")
            return True

        # Fetch page content (needed for either JSON or image)
        result = await crawler.arun(candidate_url, config=run_config)
        markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)
        print(f"✅ Extracted data for {candidate_name}")

        # Process image if needed
        if need_image:
            await download_image_from_markdown(markdown_content, image_path, candidate_name, candidate_url, csv_path)

        # Process JSON if needed
        if need_json:
            await generate_json_wrapper(markdown_content, json_output_file, force_regenerate_json,
                                        skip_if_force_regenerated)
            print(f"✅ JSON saved for {candidate_name}")

        return True

    except Exception as e:
        print(f"❌ Error processing {candidate_name}: {e}")
        try:
            csv_path = get_csv_path_from_json(json_output_file)
            log_missing_image(csv_path, candidate_name, candidate_url, f"Processing error: {str(e)}")
        except:
            pass
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


def candidate_link_crawler(year, winners_only,force_regenerate_json,skip_if_force_regenerated):
    """
    Process all constituencies for a given year.

    Args:
        year: The election year to process
        :param skip_if_force_regenerated:
        :param force_regenerate_json:
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
                asyncio.run(crawl_link_from_csv(csv_path, winners_only=winners_only,force_regenerate_json=force_regenerate_json,skip_if_force_regenerated=skip_if_force_regenerated), )

                # Uncomment the next line to stop after processing 1 district for demonstration
                # if processed > 0:
                #     print("Stopping after processing 1 districts for demonstration.")
                #     return
            else:
                print(f"[{processed}/{total_districts}] No CSV file found for {district} in {state}")


def discover_states_and_districts(year,base_folder="constituency_data"):
    """
    Discover all available states and districts for a given year.

    Args:
        year: The election year (integer or string)

    Returns:
        Dictionary mapping states to lists of districts
        :param year:
        :param base_folder:
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


# Add this new function - IMAGE DOWNLOAD FUNCTIONALITY
async def download_profile_image(image_url, output_path):
    """Download profile image from URL and save to the specified path."""
    if not image_url.startswith(('http://', 'https://')):
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Write image content to file
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())

                    print(f"✅ Image saved: {os.path.basename(output_path)}")
                    return True
                else:
                    print(f"❌ Failed to download image: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error downloading image: {str(e)}")
        return False


# Add this new function - IMAGE EXTRACTION FROM HTML
def extract_profile_image_from_html(html_content):
    """Extract profile image URL from HTML content using multiple patterns."""

    # Pattern 1: Look for profile images with alt="profile image"
    profile_img_pattern1 = re.compile(
        r'<img[^>]*src="([^"]*(?:myneta\.info/)?images_candidate/[^"]*\.(?:jpg|png|jpeg))"[^>]*alt="profile image"',
        re.IGNORECASE
    )

    # Pattern 2: Any image in images_candidate directory (absolute URL)
    profile_img_pattern2 = re.compile(
        r'<img[^>]*src="(https?://[^"]*myneta\.info/images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
        re.IGNORECASE
    )

    # Pattern 3: Relative paths to images_candidate
    profile_img_pattern3 = re.compile(
        r'<img[^>]*src="(/images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
        re.IGNORECASE
    )

    # Pattern 4: Any images_candidate reference
    profile_img_pattern4 = re.compile(
        r'<img[^>]*src="([^"]*images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
        re.IGNORECASE
    )

    patterns = [
        (profile_img_pattern1, "Profile image with alt text"),
        (profile_img_pattern2, "Absolute URL to images_candidate"),
        (profile_img_pattern3, "Relative path to images_candidate"),
        (profile_img_pattern4, "Any images_candidate reference"),
    ]

    # Try all patterns in order of preference
    for pattern, description in patterns:
        match = pattern.search(html_content)
        if match:
            image_url = match.group(1)
            # Make sure it's an absolute URL
            if not image_url.startswith(('http://', 'https://')):
                if image_url.startswith('/'):
                    image_url = 'https://myneta.info' + image_url
                else:
                    image_url = 'https://myneta.info/' + image_url
            return image_url

    # Fallback: Look for any images_candidate references
    all_images = re.findall(r'<img[^>]*src="([^"]+\.(?:jpg|png|jpeg))"', html_content, re.IGNORECASE)
    candidate_images = [img for img in all_images if 'images_candidate' in img.lower()]
    if candidate_images:
        image_url = candidate_images[0]
        if not image_url.startswith(('http://', 'https://')):
            if image_url.startswith('/'):
                image_url = 'https://myneta.info' + image_url
            else:
                image_url = 'https://myneta.info/' + image_url
        return image_url

    return None


# Helper function for CSV logging
def log_missing_image(csv_path, candidate_name, candidate_url, reason, state=None, year=None, constituency=None):
    """Log missing image information to CSV file."""
    missing_images_csv = "missing_profile_images_mla.csv"
    csv_headers = ['timestamp', 'state', 'year', 'constituency', 'candidate_name', 'url', 'reason', 'source_csv']

    csv_exists = os.path.exists(missing_images_csv)

    try:
        with open(missing_images_csv, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            if not csv_exists:
                csv_writer.writerow(csv_headers)
                print(f"📝 Created missing images tracking file: {missing_images_csv}")

            # Extract info from path if not provided
            if not all([state, year, constituency]):
                path_parts = csv_path.replace('\\', '/').split('/')
                if len(path_parts) >= 4:
                    try:
                        year = year or path_parts[-4]
                        state = state or path_parts[-3]
                        constituency = constituency or path_parts[-2]
                    except IndexError:
                        pass

            csv_writer.writerow([
                datetime.now().isoformat(),
                state or "Unknown",
                year or "Unknown",
                constituency or "Unknown",
                candidate_name,
                candidate_url,
                reason,
                os.path.basename(csv_path)
            ])

    except Exception as e:
        print(f"❌ Error writing to missing images CSV: {e}")


def get_csv_path_from_json(json_output_file):
    """Extract CSV path from JSON file path."""
    try:
        candidate_dir = os.path.dirname(json_output_file)
        parent_dir = os.path.dirname(candidate_dir)
        csv_files = [f for f in os.listdir(parent_dir) if f.endswith('.csv')]
        if csv_files:
            return os.path.join(parent_dir, csv_files[0])
    except:
        pass
    return "unknown.csv"


async def download_image_from_markdown(markdown_content, image_path, candidate_name, candidate_url, csv_path):
    """Extract image URL from markdown and download it."""
    image_url = None
    match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', markdown_content)
    if match:
        image_url = match.group(1)

    if image_url:
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
            image.save(image_path, format='JPEG')
            print(f"🖼️ Image saved for {candidate_name}")
            return True
        except Exception as img_err:
            print(f"⚠️ Failed to download/save image for {candidate_name}: {img_err}")
            log_missing_image(csv_path, candidate_name, candidate_url, f"Download failed: {str(img_err)}")
            return False
    else:
        print(f"⚠️ No image found in markdown for {candidate_name}")
        log_missing_image(csv_path, candidate_name, candidate_url, "No image found in markdown content")
        return False


# async def generate_json_wrapper(markdown_content, json_output_file):
#     """Generate JSON in a separate thread."""
#     loop = asyncio.get_event_loop()
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         await loop.run_in_executor(
#             executor,
#             generate_wrapper,
#             markdown_content,
#             json_output_file
#         )


async def generate_json_wrapper(markdown_content, json_output_file, force_regenerate=False,
                                skip_if_force_regenerated=True):
    """Generate JSON in a separate thread with force regenerate tracking."""

    # Check if we should skip generation
    if not force_regenerate and os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
        print(f"⚠️ JSON file already exists, skipping generation for {os.path.basename(json_output_file)}")
        return

    # If force regenerating, check if already force-regenerated
    if force_regenerate and skip_if_force_regenerated and is_force_regenerated(json_output_file):
        timestamp = get_force_regenerated_timestamp(json_output_file)
        print(f"🔄 Already force-regenerated on {timestamp}, skipping {os.path.basename(json_output_file)}")
        return

    if force_regenerate and os.path.exists(json_output_file):
        if is_force_regenerated(json_output_file):
            print(
                f"🔄 Force regenerating JSON for {os.path.basename(json_output_file)} (overriding previous force generation)")
        else:
            print(f"🔄 Force regenerating JSON for {os.path.basename(json_output_file)}")

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=10) as executor:
        await loop.run_in_executor(
            executor,
            generate_wrapper,
            markdown_content,
            json_output_file
        )

    # Mark as force-regenerated if this was a force regeneration
    if force_regenerate:
        mark_as_force_regenerated(json_output_file)



# Helper functions for force regenerate tracking
def mark_as_force_regenerated(json_output_file):
    """Create a flag file to mark this candidate as force-regenerated."""
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    with open(flag_file, 'w') as f:
        f.write(datetime.now().isoformat())
    print(f"🏷️ Marked as force-regenerated: {os.path.basename(flag_file)}")

def is_force_regenerated(json_output_file):
    """Check if this candidate was already force-regenerated."""
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    return os.path.exists(flag_file)

def get_force_regenerated_timestamp(json_output_file):
    """Get the timestamp when this candidate was force-regenerated."""
    flag_file = json_output_file.replace('.json', '.force_regenerated')
    if os.path.exists(flag_file):
        try:
            with open(flag_file, 'r') as f:
                return f.read().strip()
        except:
            return "Unknown"
    return None

