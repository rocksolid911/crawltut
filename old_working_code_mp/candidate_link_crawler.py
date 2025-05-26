import asyncio
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, DefaultMarkdownGenerator

from constituancy_link_parser import parse_constituency_links
from md_file_reader import get_constituency_md_file


# async def candidatecrawler(year , state=None):
#     # Your existing code for loading constituency data
#     md_file = get_constituency_md_file(year=year)
#     if not md_file:
#         print("Error: No constituency markdown file found. Please run constituency crawler first.")
#         return
#
#     with open(md_file, 'r', encoding='utf-8') as f:
#         md_content = f.read()
#
#     constituency_data = parse_constituency_links(md_content)
#     # Save all constituency data to markdown files
#
#     # first_url = constituency_data[0][1] if constituency_data else None
#     print(constituency_data)
#     #
#     session_id = "session_id_candidate"
#     browser_config = BrowserConfig(
#         headless=True,
#         browser_type="chromium",
#     )
#
#     # Configuration for normal page crawling
#     run_config = CrawlerRunConfig(
#         cache_mode=CacheMode.BYPASS,
#         session_id=session_id
#     )
#
#     async  with AsyncWebCrawler(config=browser_config) as crawler:
#         for name, url, constituency_id in constituency_data:
#             print(f"Crawling: {name} (ID: {constituency_id})")
#             result = await crawler.arun(
#                 url,
#                 config=run_config
#             )
#             # Save the result to a markdown file
#             output_file = os.path.join("constituency_data",year, f"{name}_{constituency_id}.md")
#             with open(output_file, 'w', encoding='utf-8') as f:
#                 f.write(result.markdown)
#             print(f"Saved data for {name} to {output_file}")
#     #await save_candidate_links(constituency_data, browser_config, run_config)


# async def save_candidate_links(constituency_data, browser_config, run_config):

async def candidatecrawler(year, state=None):
    """
    Crawl candidate data from constituencies for a specific year.

    Args:
        year: The election year (mandatory)
        state: Optional state filter to limit crawling to specific state
    """
    # Get constituency data
    md_file = get_constituency_md_file(year=year)
    if not md_file:
        print(f"Error: No constituency markdown file found for year {year}. Please run constituency crawler first.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    constituency_data = parse_constituency_links(md_content)

    # Filter by state if specified
    if state:
        constituency_data = [data for data in constituency_data if state.lower() in data[0].lower()]
        if not constituency_data:
            print(f"No constituencies found for state: {state}")
            return

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
        for i, (name, url, constituency_id) in enumerate(constituency_data):
            print(f"Processing {i + 1}/{len(constituency_data)}: {name}")

            try:

                # Add a delay before each crawl (adjust the seconds as needed)
                await asyncio.sleep(2)  # Wait for 2 seconds before each crawl

                # Fetch the constituency page
                result = await crawler.arun(url, config=run_config)
                # Extract state from the Markdown content
                state_match = extract_location_from_markdown_content(result.markdown)
                if state_match:
                    print(f"Found state name: {state_match}")
                else:
                    print("Could not extract state name from the matched header")
                # Extract district name from constituency
                if "(" in name:
                    district_name = name.split("(")[0].strip()
                else:
                    district_name = name.strip()

                # Clean district name for directory
                clean_district = district_name.replace(' ', '_').replace('-', '_')

                # Create directory structure
                output_dir = os.path.join("../constituency_data", str(year), state_match, clean_district)
                os.makedirs(output_dir, exist_ok=True)

                # Clean constituency name for filename
                clean_name = name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')

                # Define file paths
                md_file_path = os.path.join(output_dir, f"{clean_name}_{constituency_id}.md")
                # txt_file_path = os.path.join(output_dir, f"{clean_name}_{constituency_id}.txt")

                # Save markdown file
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(result.markdown)

                print(f"✓ Saved data for {name} to {output_dir}")


            except Exception as e:
                print(f"✗ Error processing {name}: {str(e)}")


def extract_location_from_markdown_content(markdown_content):
    # Split the content into lines
    lines = markdown_content.splitlines()

    for line in lines:
        # Look for the line that starts with "### List of Candidates - ANDAMAN AND NICOBAR ISLANDS:"
        if line.startswith("### List of Candidates - "):
            # Extract the part after the colon
            after_colon = line.split(':', 1)[1]

            # If there's a square bracket after the location, remove it
            if '[' in after_colon:
                location = after_colon.split('(', 1)[0].strip()
            else:
                location = after_colon.strip()

            return location

    # Return None if the line wasn't found
    return None





