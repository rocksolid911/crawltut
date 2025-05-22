import asyncio

from candidate_crawler import candidatecrawler
from constituency_link_crawler import customcrawler
from extract_candidate_table_csv import extract_candidate_tables_to_csv


async def run_crawler_for_years(years):
    for year in years:
        print(f"\n=== Processing year {year} ===\n")
        await candidatecrawler(year=year)


if __name__ == "__main__":
    # asyncio.run(customcrawler())

    # years_to_process = [2024,2019, 2014, 2009, 2004,]
    # asyncio.run(run_crawler_for_years(years_to_process))
    extract_candidate_tables_to_csv()


