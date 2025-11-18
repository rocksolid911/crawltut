"""
Member of Parliament (MP) crawler.

This module crawls MP candidate data from myneta.info.
"""
import asyncio
import os
from typing import List, Optional

from crawl4ai import AsyncWebCrawler

from config.settings import get_crawler_config
from src.crawlers.base_crawler import CandidateCrawler
from src.extractors.image_extractor import download_image_from_markdown
from src.parsers.json_generator import generate_json_async
from src.utils.csv_utils import read_candidates_from_csv, log_missing_image, get_csv_path_from_json
from src.utils.file_utils import discover_states_and_districts, get_constituency_csv_file


class MPCrawler(CandidateCrawler):
    """Crawler for Member of Parliament candidates."""

    async def process_candidate(self, candidate_name: str, candidate_url: str,
                                json_output_file: str, crawler: AsyncWebCrawler,
                                force_regenerate_json: bool = False,
                                skip_if_force_regenerated: bool = True) -> bool:
        """
        Process a single MP candidate.

        Args:
            candidate_name: Name of the candidate
            candidate_url: URL of the candidate profile
            json_output_file: Path to output JSON file
            crawler: AsyncWebCrawler instance
            force_regenerate_json: If True, regenerate JSON even if exists
            skip_if_force_regenerated: If True, skip if already force-regenerated

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Processing: {candidate_name} ({candidate_url})")

            # File paths and existence checks
            json_exists = os.path.exists(json_output_file) and os.path.getsize(json_output_file) > 0
            image_path = os.path.splitext(json_output_file)[0] + ".jpg"
            image_exists = os.path.exists(image_path) and os.path.getsize(image_path) > 0
            csv_path = get_csv_path_from_json(json_output_file)

            # Determine what needs to be processed
            from src.parsers.json_generator import is_force_regenerated
            already_force_regenerated = is_force_regenerated(json_output_file)

            need_json = not json_exists or (
                force_regenerate_json and not (skip_if_force_regenerated and already_force_regenerated))
            need_image = not image_exists

            # Skip if both exist and no force regeneration needed
            if json_exists and image_exists and not need_json:
                print(f"Both JSON and image already exist for {candidate_name} - skipping")
                return True

            # Fetch page content (needed for either JSON or image)
            result = await crawler.arun(candidate_url, config=self.run_config)
            markdown_content = result.markdown if hasattr(result, 'markdown') else str(result)
            print(f"Extracted data for {candidate_name}")

            # Process image if needed
            if need_image:
                await download_image_from_markdown(markdown_content, image_path, candidate_name)

            # Process JSON if needed
            if need_json:
                await generate_json_async(markdown_content, json_output_file,
                                        force_regenerate_json, skip_if_force_regenerated)
                print(f"JSON saved for {candidate_name}")

            return True

        except Exception as e:
            print(f"Error processing {candidate_name}: {e}")
            try:
                csv_path = get_csv_path_from_json(json_output_file)
                log_missing_image(csv_path, candidate_name, candidate_url,
                                f"Processing error: {str(e)}")
            except:
                pass
            return False

    async def crawl_from_csv(self, csv_path: str, winners_only: bool = False,
                            batch_size: Optional[int] = None,
                            force_regenerate_json: bool = False,
                            skip_if_force_regenerated: bool = True) -> None:
        """
        Crawl candidates from a CSV file.

        Args:
            csv_path: Path to the CSV file
            winners_only: If True, only process winners
            batch_size: Number of candidates to process in parallel
            force_regenerate_json: If True, regenerate JSON even if exists
            skip_if_force_regenerated: If True, skip if already force-regenerated
        """
        batch_size = batch_size or self.config.batch_size
        candidates = read_candidates_from_csv(csv_path, winners_only)

        print(f"Found {len(candidates)} candidate links in {csv_path}")

        if force_regenerate_json:
            if skip_if_force_regenerated:
                print("FORCE REGENERATE JSON MODE: Will regenerate existing JSON files (skipping already force-regenerated)")
            else:
                print("FORCE REGENERATE JSON MODE: Will regenerate ALL existing JSON files")

        # Split into batches
        output_dir = os.path.dirname(csv_path)
        batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} candidates)")

                tasks = []
                for candidate in batch:
                    candidate_name = candidate['name']
                    candidate_url = candidate['url']

                    # Get output directory and files
                    candidate_dir = self.get_candidate_output_dir(output_dir, candidate_name)
                    json_output_file, image_path = self.get_candidate_files(candidate_dir, candidate_name)

                    # Create task
                    task = self.process_candidate(
                        candidate_name, candidate_url, json_output_file, crawler,
                        force_regenerate_json, skip_if_force_regenerated
                    )
                    tasks.append(task)

                # Wait for all tasks in this batch to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Log exceptions
                for candidate, result in zip(batch, results):
                    if isinstance(result, Exception):
                        print(f"Error processing {candidate['name']}: {result}")

    async def run(self, year: int, winners_only: bool = False,
                 force_regenerate_json: bool = False,
                 skip_if_force_regenerated: bool = True) -> None:
        """
        Run the MP crawler for a specific year.

        Args:
            year: Election year to process
            winners_only: If True, only process winners
            force_regenerate_json: If True, regenerate JSON even if exists
            skip_if_force_regenerated: If True, skip if already force-regenerated
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
                    await self.crawl_from_csv(
                        csv_path,
                        winners_only=winners_only,
                        force_regenerate_json=force_regenerate_json,
                        skip_if_force_regenerated=skip_if_force_regenerated
                    )
                else:
                    print(f"[{processed}/{total_districts}] No CSV file found for {district} in {state}")


async def run_mp_crawler_for_years(years: List[int], winners_only: bool = False,
                                   force_regenerate_json: bool = False,
                                   skip_if_force_regenerated: bool = True) -> None:
    """
    Run MP crawler for multiple years.

    Args:
        years: List of years to process
        winners_only: If True, only process winners
        force_regenerate_json: If True, regenerate JSON even if exists
        skip_if_force_regenerated: If True, skip if already force-regenerated
    """
    crawler = MPCrawler()

    for year in years:
        print(f"\n=== Processing year {year} ===\n")
        await crawler.run(
            year=year,
            winners_only=winners_only,
            force_regenerate_json=force_regenerate_json,
            skip_if_force_regenerated=skip_if_force_regenerated
        )
