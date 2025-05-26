from old_working_code_mp.candidate_link_crawler import candidatecrawler
from old_working_code_mp.candidate_profile_craweler import candidate_link_crawler


async def run_crawler_for_years(years):
    for year in years:
        print(f"\n=== Processing year {year} ===\n")
        await candidatecrawler(year=year)


if __name__ == "__main__":
    # asyncio.run(customcrawler())
    # years_to_process = [2024, 2019, 2014, 2009, 2004]
    # asyncio.run(run_crawler_for_years(years_to_process))
    # extract_candidate_tables_to_csv()
    #  candidate_link_crawler(year=2024)
    years_to_process = [2019, 2014, 2009, 2004]

    # Process each year sequentially
    for year in years_to_process:
        print(f"\n=== Processing year {year} ===\n")
        candidate_link_crawler(year=year,winners_only=True)
