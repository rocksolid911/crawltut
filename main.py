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
    # asyncio.run(customcrawler())
    # years_to_process = [2024, 2019, 2014, 2009, 2004]
    # asyncio.run(run_crawler_for_years(years_to_process))
    # extract_candidate_tables_to_csv()
    #  candidate_link_crawler(year=2024,winners_only=False)
    # Process all years sequentially for mp candidate links (main one for mp)
    #process_all_years()
    # years_to_process = [2019, 2014, 2009, 2004]
    #
    # # Process each year sequentially
    # for year in years_to_process:
    #     print(f"\n=== Processing year {year} ===\n")
    #     candidate_link_crawler(year=year,winners_only=True)
    #asyncio.run(assembly_candidate_link_crawler())

    # state_urls = [
    #     "https://www.myneta.info/state_assembly.php?state=Andhra%20Pradesh",
    #     "https://www.myneta.info/state_assembly.php?state=Arunachal%20Pradesh",
    #     "https://www.myneta.info/state_assembly.php?state=Assam",
    #     "https://www.myneta.info/state_assembly.php?state=Bihar",
    #     "https://www.myneta.info/state_assembly.php?state=Chattisgarh",
    #     "https://www.myneta.info/state_assembly.php?state=Delhi",
    #     "https://www.myneta.info/state_assembly.php?state=Goa",
    #     "https://www.myneta.info/state_assembly.php?state=Gujarat",
    #     "https://www.myneta.info/state_assembly.php?state=Haryana",
    #     "https://www.myneta.info/state_assembly.php?state=Himachal%20Pradesh",
    #     "https://www.myneta.info/state_assembly.php?state=Jammu%20And%20Kashmir",
    #     "https://www.myneta.info/state_assembly.php?state=Jharkhand",
    #     "https://www.myneta.info/state_assembly.php?state=Karnataka",
    #     "https://www.myneta.info/state_assembly.php?state=Kerala",
    #     "https://www.myneta.info/state_assembly.php?state=Madhya%20Pradesh",
    #     "https://www.myneta.info/state_assembly.php?state=Maharashtra",
    #     "https://www.myneta.info/state_assembly.php?state=Manipur",
    #     "https://www.myneta.info/state_assembly.php?state=Meghalaya",
    #     "https://www.myneta.info/state_assembly.php?state=Mizoram",
    #     "https://www.myneta.info/state_assembly.php?state=Nagaland",
    #     "https://www.myneta.info/state_assembly.php?state=Odisha",
    #     "https://www.myneta.info/state_assembly.php?state=Puducherry",
    #     "https://www.myneta.info/state_assembly.php?state=Punjab",
    #     "https://www.myneta.info/state_assembly.php?state=Rajasthan",
    #     "https://www.myneta.info/state_assembly.php?state=Sikkim",
    #     "https://www.myneta.info/state_assembly.php?state=Tamil%20Nadu",
    #     "https://www.myneta.info/state_assembly.php?state=Telangana",
    #     "https://www.myneta.info/state_assembly.php?state=Tripura",
    #     "https://www.myneta.info/state_assembly.php?state=Uttarakhand",
    #     "https://www.myneta.info/state_assembly.php?state=Uttar%20Pradesh",
    #     "https://www.myneta.info/state_assembly.php?state=West%20Bengal",
    # ]
    # asyncio.run(crawl_multiple_states(state_urls))

    # asyncio.run(crawl_mla_data_with_link("https://www.myneta.info/ap09/index.php?action=show_winners&sort=default"))
    # extract_all_winners_links()

    # extract_all_candidate_urls()

    #methods for extracting candidate data for mla elections (main one for mla)



    asyncio.run(process_candidate_data(force_regenerate_json=True, skip_if_force_regenerated=True))

    # below is a test function to extract candidate images from links
    # asyncio.run(get_candidate_image_from_link())
    # asyncio.run(extract_and_download_profile_images())