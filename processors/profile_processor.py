# processors/profile_processor.py
"""
Enhanced candidate profile processing
"""
import asyncio
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict

from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from config.election_config import ElectionConfig
from old_working_code_mp.ai_csv_generation import generate
from utils.file_manager import ElectionFileManager


# from ai_csv_generation import generate  # Your existing AI generation module

class ProfileProcessor:
    """Processes detailed candidate profiles"""

    def __init__(self, config: ElectionConfig, file_manager: ElectionFileManager):
        self.config = config
        self.file_manager = file_manager

    async def process_candidates_from_csv(self, csv_path: str, winners_only: bool = False,
                                          batch_size: int = 10) -> None:
        """Process candidate profiles from CSV file with appropriate folder structure"""

        # Determine output directory based on election type
        csv_dir = os.path.dirname(csv_path)

        if self.config.constituency_type == "lok_sabha":
            # constituency_data/{year}/{state}/{district}/{candidate_name}/
            output_base = csv_dir
        else:
            # state_assembly/{state_name}/{district}/{candidate_name}/
            output_base = csv_dir

        return await self._process_candidates_async(csv_path, output_base, winners_only, batch_size)

    async def _process_candidates_async(self, csv_path: str, output_base: str,
                                        winners_only: bool, batch_size: int) -> None:
        """Async processing of candidates with appropriate naming conventions"""
        browser_config = BrowserConfig(headless=True, browser_type="chromium")
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, session_id="profile_session")

        # Extract candidate links from CSV
        candidate_links = self._extract_candidate_links(csv_path, winners_only)
        print(f"Found {len(candidate_links)} candidate links in {csv_path}")

        if not candidate_links:
            return

        # Process in batches
        candidates = list(candidate_links.items())
        batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")

                tasks = []
                for candidate_name, candidate_link in batch:
                    # Create candidate directory
                    safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
                    candidate_dir = os.path.join(output_base, safe_name)
                    os.makedirs(candidate_dir, exist_ok=True)

                    # Choose JSON filename based on election type
                    if self.config.constituency_type == "lok_sabha":
                        # Keep existing naming: {candidate_name}.json (MP)
                        json_output_file = os.path.join(candidate_dir, f"{safe_name}.json")
                    else:
                        # Use MLA naming for assembly: {candidate_name}_mla.json
                        json_output_file = os.path.join(candidate_dir, f"{safe_name}_mla.json")

                    # Skip if already processed
                    if os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0:
                        print(f"Skipping {candidate_name}: Already processed")
                        continue

                    task = self._process_single_candidate(
                        crawler, candidate_name, candidate_link, json_output_file, run_config
                    )
                    tasks.append(task)

                # Process batch
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Log any errors
                    for (candidate_name, _), result in zip(batch, results):
                        if isinstance(result, Exception):
                            print(f"Error processing {candidate_name}: {result}")

    def _extract_candidate_links(self, csv_path: str, winners_only: bool) -> Dict[str, str]:
        """Extract candidate links from CSV file"""
        candidate_links = {}

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header

                for row in reader:
                    if len(row) < 13:  # Ensure we have enough columns
                        continue

                    if winners_only and row[11].strip().lower() != 'yes':
                        continue

                    candidate_name = row[4]  # CandidateName column
                    candidate_link = row[12]  # CandidateURL column

                    # Validate URL
                    if candidate_link and (candidate_link.startswith('http://') or
                                           candidate_link.startswith('https://')):
                        candidate_links[candidate_name] = candidate_link

        except Exception as e:
            print(f"Error reading CSV file {csv_path}: {e}")

        return candidate_links

    async def _process_single_candidate(self, crawler, candidate_name: str, candidate_link: str,
                                        json_output_file: str, run_config) -> bool:
        """Process a single candidate profile"""
        try:
            print(f"Processing: {candidate_name}")

            # Fetch candidate page
            result = await crawler.arun(candidate_link, config=run_config)
            markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)

            # Generate JSON using AI (in separate thread to avoid blocking)
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=5) as executor:
                await loop.run_in_executor(
                    executor,
                    self._generate_profile_wrapper,
                    markdown_content,
                    json_output_file
                )

            print(f"✓ Profile saved: {json_output_file}")
            return True

        except Exception as e:
            print(f"✗ Error processing {candidate_name}: {e}")
            return False

    @retry(
        wait=wait_random_exponential(multiplier=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception)
    )
    def _generate_profile_wrapper(self, markdown_content: str, output_file: str) -> None:
        """Wrapper for AI profile generation with retry logic"""
        try:
            # Uncomment this line when you have your AI generation module ready
             generate(markdown_content, output_file)
        except Exception as e:
            print(f"Error generating profile for {output_file}: {e}")
            # For now, save the markdown content as JSON placeholder
            # import json
            # placeholder_data = {
            #     "candidate_name": "extracted_from_markdown",
            #     "raw_content": markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content,
            #     "status": "placeholder - integrate your AI generation module"
            # }

