import asyncio
import os
import csv
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from pathlib import Path
from collections import defaultdict

from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler

from old_working_code_mp.candidate_profile_craweler import generate_wrapper

import requests
import io
from PIL import Image


class CandidateURLExtractor:
    """
    Extracts candidate URLs from CSV files in organized state/year folder structure.
    Think of this like a Flutter service that reads local database files and processes data.
    """

    def __init__(self, base_path="state_assembly"):
        self.base_path = base_path
        self.results = {
            'total_files': 0,
            'total_candidates': 0,
            'states': {},
            'urls': [],
            'errors': []
        }

    def find_all_csv_files(self):
        """
        Finds all CSV files in the state/year folder structure.
        Like scanning your app's local storage for data files.
        """
        csv_files = []

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    csv_files.append(file_path)

        print(f"🔍 Found {len(csv_files)} CSV files")
        return csv_files

    def extract_state_year_from_path(self, file_path):
        """
        Extracts state name and year from file path.
        Like parsing route parameters in Flutter navigation.
        """
        try:
            # Split path and find state and year
            parts = Path(file_path).parts

            # Expected structure: state_assembly/State_Name/Year/filename.csv
            if len(parts) >= 3:
                state_name = parts[-3].replace('_', ' ')  # Convert back from folder name
                year = parts[-2]
                filename = parts[-1]

                # Determine if it's main election or bye-election
                election_type = "bye_election" if "bye" in filename.lower() else "main_election"

                return {
                    'state': state_name,
                    'year': year,
                    'type': election_type,
                    'filename': filename
                }
            else:
                return {
                    'state': 'Unknown',
                    'year': 'Unknown',
                    'type': 'unknown',
                    'filename': Path(file_path).name
                }
        except Exception as e:
            print(f"⚠️ Error parsing path {file_path}: {e}")
            return {
                'state': 'Unknown',
                'year': 'Unknown',
                'type': 'unknown',
                'filename': Path(file_path).name
            }

    def read_csv_and_extract_urls(self, file_path):
        """
        Reads CSV file and extracts candidate URLs.
        Like reading data from local database in Flutter.
        """
        try:
            # Try reading with pandas first (handles encoding better)
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')

            # Look for candidate_url column (case-insensitive)
            url_column = None
            for col in df.columns:
                if 'url' in col.lower() and 'candidate' in col.lower():
                    url_column = col
                    break

            if not url_column:
                # Try just 'url' column
                for col in df.columns:
                    if col.lower() == 'url':
                        url_column = col
                        break

            if not url_column:
                print(f"⚠️ No URL column found in {file_path}")
                return []

            # Extract URLs and candidate info
            candidates = []
            for index, row in df.iterrows():
                url = row[url_column]
                if pd.notna(url) and url.strip():  # Check if URL exists and is not empty
                    candidate_info = {
                        'name': row.get('name', 'Unknown') if 'name' in df.columns else f"Candidate_{index + 1}",
                        'constituency': row.get('constituency',
                                                'Unknown') if 'constituency' in df.columns else 'Unknown',
                        'party': row.get('party', 'Unknown') if 'party' in df.columns else 'Unknown',
                        'url': url.strip(),
                        'sno': row.get('sno', index + 1) if 'sno' in df.columns else index + 1
                    }
                    candidates.append(candidate_info)

            print(f"✅ Extracted {len(candidates)} URLs from {Path(file_path).name}")
            return candidates

        except Exception as e:
            error_msg = f"Error reading {file_path}: {str(e)}"
            print(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            return []

    def process_all_files(self):
        """
        Main function to process all CSV files and extract URLs.
        Like a complete data processing pipeline in Flutter.
        """
        print("🚀 CANDIDATE URL EXTRACTION STARTED")
        print("=" * 60)

        # Find all CSV files
        csv_files = self.find_all_csv_files()
        self.results['total_files'] = len(csv_files)

        if not csv_files:
            print("❌ No CSV files found!")
            return self.results

        # Process each file
        all_candidates = []

        for file_path in csv_files:
            print(f"\n📄 Processing: {file_path}")

            # Extract metadata from path
            metadata = self.extract_state_year_from_path(file_path)
            state = metadata['state']
            year = metadata['year']
            election_type = metadata['type']

            # Read CSV and extract URLs
            candidates = self.read_csv_and_extract_urls(file_path)

            # Add metadata to each candidate
            for candidate in candidates:
                candidate.update({
                    'state': state,
                    'year': year,
                    'election_type': election_type,
                    'source_file': file_path
                })
                all_candidates.append(candidate)

            # Update results by state
            if state not in self.results['states']:
                self.results['states'][state] = {}

            if year not in self.results['states'][state]:
                self.results['states'][state][year] = {
                    'main_election': 0,
                    'bye_election': 0,
                    'total': 0
                }

            self.results['states'][state][year][election_type] = len(candidates)
            self.results['states'][state][year]['total'] += len(candidates)

        # Store all URLs and candidates
        self.results['urls'] = [candidate['url'] for candidate in all_candidates]
        self.results['candidates'] = all_candidates
        self.results['total_candidates'] = len(all_candidates)

        # Print summary
        self.print_summary()

        return self.results

    def print_summary(self):
        """
        Prints a comprehensive summary of extracted data.
        Like displaying analytics in your Flutter app.
        """
        print(f"\n🎯 EXTRACTION SUMMARY")
        print("=" * 60)
        print(f"📊 Overall Statistics:")
        print(f"   • Total CSV files processed: {self.results['total_files']}")
        print(f"   • Total candidates with URLs: {self.results['total_candidates']}")
        print(f"   • Total unique URLs: {len(set(self.results['urls']))}")
        print(f"   • States covered: {len(self.results['states'])}")

        if self.results['errors']:
            print(f"   • ⚠️ Errors encountered: {len(self.results['errors'])}")

        print(f"\n📋 State-wise Breakdown:")
        for state, years in self.results['states'].items():
            print(f"\n🏛️ {state}:")
            total_state_candidates = sum(year_data['total'] for year_data in years.values())
            print(f"   Total candidates: {total_state_candidates}")

            for year, data in sorted(years.items()):
                main = data['main_election']
                bye = data['bye_election']
                total = data['total']
                print(f"   • {year}: {total} candidates ({main} main + {bye} bye-election)")

        if self.results['errors']:
            print(f"\n❌ Errors:")
            for error in self.results['errors']:
                print(f"   • {error}")

    def save_urls_to_file(self, output_file="extracted_candidate_urls.txt"):
        """
        Saves all extracted URLs to a text file.
        Like exporting data from your Flutter app.
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Candidate URLs Extracted from {self.results['total_files']} CSV files\n")
                f.write(f"# Total URLs: {len(self.results['urls'])}\n")
                f.write(f"# Generated on: {pd.Timestamp.now()}\n\n")

                for url in self.results['urls']:
                    f.write(f"{url}\n")

            print(f"💾 Saved {len(self.results['urls'])} URLs to: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Error saving URLs: {e}")
            return None

    def save_detailed_report(self, output_file="candidate_extraction_report.csv"):
        """
        Saves detailed candidate information to CSV.
        Like creating a comprehensive data export in Flutter.
        """
        try:
            if not self.results.get('candidates'):
                print("⚠️ No candidate data to save")
                return None

            df = pd.DataFrame(self.results['candidates'])
            df.to_csv(output_file, index=False, encoding='utf-8')

            print(f"📊 Saved detailed report with {len(df)} candidates to: {output_file}")
            return output_file

        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return None

    def get_urls_by_state(self, state_name):
        """
        Returns URLs for a specific state.
        Like filtering data by category in Flutter.
        """
        if not hasattr(self.results, 'candidates') or not self.results.get('candidates'):
            return []

        state_candidates = [
            candidate for candidate in self.results['candidates']
            if candidate['state'].lower() == state_name.lower()
        ]

        return [candidate['url'] for candidate in state_candidates]

    def get_urls_by_year(self, year):
        """
        Returns URLs for a specific year.
        """
        if not self.results.get('candidates'):
            return []

        year_candidates = [
            candidate for candidate in self.results['candidates']
            if candidate['year'] == str(year)
        ]

        return [candidate['url'] for candidate in year_candidates]


# Main execution function
def extract_all_candidate_urls(base_path="state_assembly"):
    """
    Main function to extract all candidate URLs from CSV files.

    Usage:
        results = extract_all_candidate_urls("state_assembly")
        urls = results['urls']
    """
    extractor = CandidateURLExtractor(base_path)
    results = extractor.process_all_files()

    # Save outputs
    extractor.save_urls_to_file("all_candidate_urls.txt")
    extractor.save_detailed_report("candidate_details.csv")

    return results


# Example usage functions
def get_andhra_pradesh_urls():
    """Get only Andhra Pradesh candidate URLs"""
    extractor = CandidateURLExtractor()
    results = extractor.process_all_files()
    return extractor.get_urls_by_state("Andhra Pradesh")


def get_urls_by_year(year):
    """Get candidate URLs for a specific year"""
    extractor = CandidateURLExtractor()
    results = extractor.process_all_files()
    return extractor.get_urls_by_year(year)






# async def process_candidate_data(base_path_for_getting_link="state_assembly", batch_size=1):
#     """
#     Process candidates from CSV files and generate JSON data files.
#     Handles by-election candidates separately.
#
#     Args:
#         base_path_for_getting_link: Base directory containing candidate CSV files
#         batch_size: Number of candidates to process in parallel
#     """
#     print("🔍 Finding candidate CSV files...")
#
#     # Find all CSV files
#     csv_files = []
#     for root, dirs, files in os.walk(base_path_for_getting_link):
#         for file in files:
#             if file.endswith("_winners.csv"):
#                 csv_files.append(os.path.join(root, file))
#
#     print(f"📊 Found {len(csv_files)} winner CSV files")
#
#     if not csv_files:
#         print("❌ No candidate CSV files found!")
#         return
#
#     # Configure browser settings for crawling
#     browser_config = BrowserConfig(
#         headless=True,
#         browser_type="chromium",
#     )
#
#     run_config = CrawlerRunConfig(
#         cache_mode=CacheMode.BYPASS,
#         session_id="candidate_crawl_session",
#     )
#
#     # Process each CSV file
#     total_candidates = 0
#     by_election_candidates = 0
#
#     # Base directory for output
#     output_base = "candidate_data"
#     os.makedirs(output_base, exist_ok=True)
#
#     async with AsyncWebCrawler(config=browser_config) as crawler:
#         for csv_file in csv_files:
#             # Extract state and year from file path
#             # Expected path: state_assembly/State_Name/YYYY/State_Name_YYYY_winners.csv
#             path_parts = csv_file.split(os.sep)
#             if len(path_parts) >= 3:
#                 state = path_parts[-3]
#                 year = path_parts[-2]
#                 print(f"\n📄 Processing {state} {year} winners from {csv_file}")
#
#                 # Read the CSV file
#                 candidates = []
#                 try:
#                     with open(csv_file, 'r', encoding='utf-8') as f:
#                         reader = csv.reader(f)
#                         next(reader, None)  # Skip header
#
#                         for row in reader:
#                             candidate_name = row[1].strip()
#                             candidate_url = row[8].strip()
#                             constituency = row[2].strip() if len(row) > 3 else "Unknown"
#
#                             # Check if the URL is valid
#                             if candidate_url and isinstance(candidate_url, str) and (
#                                     candidate_url.startswith('http://') or
#                                     candidate_url.startswith('https://')):
#
#                                 # Check if this is a by-election
#                                 is_by_election = False
#                                 if constituency:
#                                     by_election_match = re.search(r'\b(by[-\s]election|by[-\s]poll)\b',
#                                                                   constituency, re.IGNORECASE)
#                                     is_by_election = bool(by_election_match)
#
#                                 candidates.append({
#                                     'name': candidate_name,
#                                     'url': candidate_url,
#                                     'constituency': constituency,
#                                     'is_by_election': is_by_election
#                                 })
#                             # Ensure row has enough columns
#
#
#                 except Exception as e:
#                     print(f"❌ Error reading CSV {csv_file}: {e}")
#                     continue
#
#                 print(f"ℹ️ Found {len(candidates)} candidates in {csv_file}")
#                 total_candidates += len(candidates)
#
#                 # Process candidates in batches
#                 batches = [candidates[i:i+batch_size] for i in range(0, len(candidates), batch_size)]
#
#                 for batch_num, batch in enumerate(batches, 1):
#                     print(f"🔄 Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")
#
#                     # Create tasks for the batch
#                     tasks = []
#                     for candidate in batch:
#                         candidate_name = candidate['name']
#                         candidate_url = candidate['url']
#                         is_by_election = candidate['is_by_election']
#
#                         # Create safe name for filesystem
#                         safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
#
#                         # Determine output directory based on by-election status
#                         if is_by_election:
#                             by_election_candidates += 1
#                             candidate_dir = os.path.join(output_base, str(year), state, "by_elections", safe_name)
#                         else:
#                             candidate_dir = os.path.join(output_base, str(year), state, safe_name)
#
#                         os.makedirs(candidate_dir, exist_ok=True)
#                         json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")
#
#                         # Skip if already processed
#                         if os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
#                             print(f"✅ Skipping {candidate_name}: JSON already exists")
#                             continue
#
#                         # Add task for processing this candidate
#                         task = process_candidate(
#                             crawler,
#                             candidate_name,
#                             candidate_url,
#                             json_output_file,
#                             run_config
#                         )
#                         tasks.append(task)
#
#                     # Execute all tasks in this batch
#                     if tasks:
#                         results = await asyncio.gather(*tasks, return_exceptions=True)
#
#                         # Log results
#                         success = sum(1 for r in results if r is True)
#                         failed = sum(1 for r in results if isinstance(r, Exception) or r is False)
#                         print(f"📊 Batch completed: {success} successful, {failed} failed")
#                     else:
#                         print("ℹ️ No tasks to process in this batch (all may be skipped)")
#
#     print(f"\n✅ Processing complete! Processed {total_candidates} candidates total.")
#     print(f"🗂️ By-election candidates: {by_election_candidates}")
#
# async def process_candidate(crawler, candidate_name, candidate_url, json_output_file, run_config):
#     """Process a single candidate and extract their data."""
#     try:
#         print(f"🔍 Processing: {candidate_name} ({candidate_url})")
#
#         # Fetch the candidate page
#         result = await crawler.arun(candidate_url, config=run_config)
#
#         # Extract markdown content
#         markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)
#
#         print(f"✅ Extracted data for {candidate_name}")
#
#         # --- Extract image URL from markdown_content ---
#         image_url = None
#         match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', markdown_content)
#         if match:
#             image_url = match.group(1)
#
#         # --- Download and save image as JPG ---
#         if image_url:
#             try:
#                 response = requests.get(image_url, timeout=10)
#                 response.raise_for_status()
#                 image = Image.open(io.BytesIO(response.content)).convert('RGB')
#                 image_path = os.path.splitext(json_output_file)[0] + ".jpg"
#                 image.save(image_path, format='JPEG')
#                 print(f"🖼️ Image saved for {candidate_name} at {image_path}")
#             except Exception as img_err:
#                 print(f"⚠️ Failed to download/save image for {candidate_name}: {img_err}")
#         else:
#             print(f"⚠️ No image found in markdown for {candidate_name}")
#
#         # Generate JSON in a separate thread
#         loop = asyncio.get_event_loop()
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             await loop.run_in_executor(
#                 executor,
#                 generate_wrapper,
#                 markdown_content,
#                 json_output_file
#             )
#
#         print(f"✅ JSON saved for {candidate_name}")
#         return True
#
#     except Exception as e:
#         print(f"❌ Error processing {candidate_name}: {e}")
#         return False


async def process_candidate_data(base_path_for_getting_link="state_assembly",
                                 batch_size=1,
                                 force_regenerate_json=False,
                                 skip_if_force_regenerated=True):
    """
    Process candidates from CSV files and generate JSON data files.
    Handles by-election candidates separately.

    Args:
        base_path_for_getting_link: Base directory containing candidate CSV files
        batch_size: Number of candidates to process in parallel
        force_regenerate_json: Force regenerate JSON files even if they exist
        skip_if_force_regenerated: Skip candidates that have already been force-regenerated
    """
    print("🔍 Finding candidate CSV files...")

    if force_regenerate_json:
        if skip_if_force_regenerated:
            print(
                "🔄 FORCE REGENERATE JSON MODE: Will regenerate existing JSON files (skipping already force-regenerated)")
        else:
            print("🔄 FORCE REGENERATE JSON MODE: Will regenerate ALL existing JSON files")

    # Find all CSV files
    csv_files = []
    for root, dirs, files in os.walk(base_path_for_getting_link):
        for file in files:
            if file.endswith("_winners.csv"):
                csv_files.append(os.path.join(root, file))

    print(f"📊 Found {len(csv_files)} winner CSV files")

    if not csv_files:
        print("❌ No candidate CSV files found!")
        return

    # Configure browser settings for crawling
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium",
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        session_id="candidate_crawl_session",
    )

    # Process each CSV file
    total_candidates = 0
    by_election_candidates = 0

    # Base directory for output
    output_base = "candidate_data"
    os.makedirs(output_base, exist_ok=True)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for csv_file in csv_files:
            # Extract state and year from file path
            # Expected path: state_assembly/State_Name/YYYY/State_Name_YYYY_winners.csv
            path_parts = csv_file.split(os.sep)
            if len(path_parts) >= 3:
                state = path_parts[-3]
                year = path_parts[-2]
                print(f"\n📄 Processing {state} {year} winners from {csv_file}")

                # Read the CSV file
                candidates = []
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader, None)  # Skip header

                        for row in reader:
                            candidate_name = row[1].strip()
                            candidate_url = row[8].strip()
                            constituency = row[2].strip() if len(row) > 3 else "Unknown"

                            # Check if the URL is valid
                            if candidate_url and isinstance(candidate_url, str) and (
                                    candidate_url.startswith('http://') or
                                    candidate_url.startswith('https://')):

                                # Check if this is a by-election
                                is_by_election = False
                                if constituency:
                                    by_election_match = re.search(r'\b(by[-\s]election|by[-\s]poll)\b',
                                                                  constituency, re.IGNORECASE)
                                    is_by_election = bool(by_election_match)

                                candidates.append({
                                    'name': candidate_name,
                                    'url': candidate_url,
                                    'constituency': constituency,
                                    'is_by_election': is_by_election
                                })

                except Exception as e:
                    print(f"❌ Error reading CSV {csv_file}: {e}")
                    continue

                print(f"ℹ️ Found {len(candidates)} candidates in {csv_file}")
                total_candidates += len(candidates)

                # Process candidates in batches
                batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]

                for batch_num, batch in enumerate(batches, 1):
                    print(f"🔄 Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")

                    # Create tasks for the batch
                    tasks = []
                    for candidate in batch:
                        candidate_name = candidate['name']
                        candidate_url = candidate['url']
                        is_by_election = candidate['is_by_election']

                        # Create safe name for filesystem
                        safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")

                        # Determine output directory based on by-election status
                        if is_by_election:
                            by_election_candidates += 1
                            candidate_dir = os.path.join(output_base, str(year), state, "by_elections", safe_name)
                        else:
                            candidate_dir = os.path.join(output_base, str(year), state, safe_name)

                        os.makedirs(candidate_dir, exist_ok=True)
                        json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")
                        force_flag_file = os.path.join(candidate_dir, f"{safe_name}.force_regenerated")

                        # Check if should skip processing
                        should_skip = False
                        skip_reason = ""

                        if force_regenerate_json:
                            # Force regeneration mode
                            if skip_if_force_regenerated and os.path.exists(force_flag_file):
                                # Check when it was force-regenerated
                                try:
                                    with open(force_flag_file, 'r') as f:
                                        timestamp = f.read().strip()
                                    should_skip = True
                                    skip_reason = f"Already force-regenerated on {timestamp}"
                                except:
                                    # If can't read flag file, regenerate
                                    should_skip = False
                            else:
                                # Force regenerate (either no flag or skip_if_force_regenerated=False)
                                if os.path.exists(json_output_file):
                                    print(f"🔄 Force regenerating JSON for {candidate_name} (overriding existing)")
                                    should_skip = False
                                    skip_reason = "Force regeneration mode"

                        else:
                            # Normal mode - skip if JSON already exists
                            if os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
                                should_skip = True
                                skip_reason = "JSON already exists"

                        if should_skip:
                            print(f"✅ Skipping {candidate_name}: {skip_reason}")
                            continue

                        # Add task for processing this candidate
                        task = process_candidate(
                            crawler,
                            candidate_name,
                            candidate_url,
                            json_output_file,
                            run_config,
                            force_regenerate_json
                        )
                        tasks.append(task)

                    # Execute all tasks in this batch
                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)

                        # Log results
                        success = sum(1 for r in results if r is True)
                        failed = sum(1 for r in results if isinstance(r, Exception) or r is False)
                        print(f"📊 Batch completed: {success} successful, {failed} failed")
                    else:
                        print("ℹ️ No tasks to process in this batch (all may be skipped)")

    print(f"\n✅ Processing complete! Processed {total_candidates} candidates total.")
    print(f"🗂️ By-election candidates: {by_election_candidates}")


async def process_candidate(crawler, candidate_name, candidate_url, json_output_file, run_config,
                            force_regenerate_json=False):
    """Process a single candidate and extract their data."""
    try:
        print(f"🔍 Processing: {candidate_name} ({candidate_url})")

        # Fetch the candidate page
        result = await crawler.arun(candidate_url, config=run_config)

        # Extract markdown content
        markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)

        print(f"✅ Extracted data for {candidate_name}")
        # Show force regeneration message
        if force_regenerate_json and os.path.exists(json_output_file):
            force_flag_file = os.path.splitext(json_output_file)[0] + ".force_regenerated"
            if os.path.exists(force_flag_file):
                print(
                    f"🔄 Force regenerating JSON for {os.path.basename(json_output_file)} (overriding previous force generation)")
            else:
                print(f"🔄 Force regenerating JSON for {os.path.basename(json_output_file)}")

        # Generate JSON in a separate thread
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=10) as executor:
            await loop.run_in_executor(
                executor,
                generate_wrapper,
                markdown_content,
                json_output_file
            )

        # Create force regeneration flag if in force mode
        if force_regenerate_json:
            from datetime import datetime
            force_flag_file = os.path.splitext(json_output_file)[0] + ".force_regenerated"
            timestamp = datetime.now().isoformat()
            with open(force_flag_file, 'w') as f:
                f.write(timestamp)
            print(f"🏷️ Marked as force-regenerated: {os.path.basename(force_flag_file)}")

        print(f"✅ JSON saved for {candidate_name}")
        return True

    except Exception as e:
        print(f"❌ Error processing {candidate_name}: {e}")
        return False
