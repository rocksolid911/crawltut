import asyncio
import csv
import glob
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from urllib.parse import urlparse

from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler


from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from old_working_code_mp.ai_csv_generation import generate
from old_working_code_mp.md_file_reader import get_constituency_csv_file
import requests
import io
from PIL import Image


async def get_candidate_image_from_link( winners_only=False, batch_size=50):
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

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # candidate_dict_link_with_name = {}
        # output_dir = os.path.dirname(csv_path)
        #
        # with open(csv_path, 'r', encoding='utf-8') as f:
        #     reader = csv.reader(f)
        #     for row in reader:
        #         if winners_only and row[11].strip().lower() != 'yes':
        #             continue
        #         # Assuming the first column contains the candidate name and the second column contains the link
        #         candidate_name = row[4]
        #         candidate_link = row[12]
        #         # Validate that the link is a proper HTTP/HTTPS URL
        #         if candidate_link and isinstance(candidate_link, str) and (
        #                 candidate_link.startswith('http://') or candidate_link.startswith('https://')):
        #             candidate_dict_link_with_name[candidate_name] = candidate_link
        #
        # print(f"Found {len(candidate_dict_link_with_name)} candidate links in {csv_path}")
        #
        # # Process candidates in batches
        # candidates = list(candidate_dict_link_with_name.items())
        # batches = [candidates[i:i + batch_size] for i in range(0, len(candidates), batch_size)]
        #
        # for batch in batches:
        #     tasks = []
        #     for name, link in batch:
        #         tasks.append(crawler.arun(link, config=run_config))
        #     results = await asyncio.gather(*tasks)
        #
        #     for result, (name, link) in zip(results, batch):
        #         output_file = os.path.join(output_dir, f"{name}.md")
        #         with open(output_file, 'w', encoding='utf-8') as f:
        #             f.write(result.markdown)
        #         print(f"Saved data for {name} to {output_file}")
        result = await crawler.arun(
            url="https://www.myneta.info/LokSabha2019/candidate.php?candidate_id=5717",
            config=run_config
        )
        print(result.markdown)  # Pr






    