import asyncio

from candidate_image_crawler import get_candidate_image_from_link
from candidate_url_extractor import extract_all_candidate_urls, process_candidate_data
from mla_candidate_image_extractor import extract_and_download_profile_images
from mla_link_lister import extract_all_winners_links
from old_working_code_mp.candidate_link_crawler import candidatecrawler
from old_working_code_mp.candidate_profile_craweler import candidate_link_crawler
from old_working_code_mp.md_file_reader import get_state_assembly_csv_file
from test_hgh import assembly_candidate_link_crawler, crawl_multiple_states


async def run_crawler_for_years(years):
    for year in years:
        print(f"\n=== Processing year {year} ===\n")
        await candidatecrawler(year=year)


def process_all_years():
    """Process all election years with appropriate winners_only settings"""
    # Process 2024 with winners_only=False (get all candidates)
    print("\n=== Processing year 2024 (all candidates) ===\n")
    candidate_link_crawler(year=2024, winners_only=False,force_regenerate_json=True,skip_if_force_regenerated=True)

    # Process previous years with winners_only=True (only winners)
    previous_years = [2019, 2014, 2009, 2004]
    for year in previous_years:
        print(f"\n=== Processing year {year} (winners only) ===\n")
        candidate_link_crawler(year=year, winners_only=True,force_regenerate_json=True, skip_if_force_regenerated=True)


if __name__ == "__main__":
    # Main method for extracting candidate data for MLA elections
    asyncio.run(process_candidate_data(force_regenerate_json=True, skip_if_force_regenerated=True))
