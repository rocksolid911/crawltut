from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler

from assembly_state_wise_winner_link_craweler import extract_candidates_from_markdown, save_to_csv, print_csv_content


async def crawl_mla_data_with_link(url,state,year):
    """
    Read a CSV file and extract candidate links.

    Args:
        csv_path: Path to the CSV file
        :param year:
        :param state:
        :param url:
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
        # Define the URL to crawl
        # url = "https://www.myneta.info/state_assembly.php?state=Andhra%20Pradesh"

        print(f"Crawling: {url}")
        print("This will extract MLA links for the specified state.")
        print("Please wait while the crawler navigates the page...")

        result = await crawler.arun(
            url,
            config=run_config
        )
        output_dir = f"state_assembly/{state}/{year}/"  # or dynamically set for each state/year
        main_candidates, bye_candidates = extract_candidates_from_markdown(result.markdown)
        if main_candidates:
            main_file = f"{output_dir}{state}_{year}_winners.csv"
            save_to_csv(main_candidates, main_file)
            print_csv_content(main_file, 10)

        if bye_candidates:
            bye_file = f"{output_dir}{state}_{year}_bye_elections.csv"
            save_to_csv(bye_candidates, bye_file)
            print_csv_content(bye_file, 5)

        # Summary
        total_candidates = len(main_candidates) + len(bye_candidates)
        print(f"\n🎯 EXTRACTION SUMMARY:")
        print(f"   • Main election winners: {len(main_candidates)}")
        print(f"   • Bye-election winners: {len(bye_candidates)}")
        print(f"   • Total candidates extracted: {total_candidates}")
        print(f"   • Files created: {main_file}, {bye_file}")

        # Process the result as needed
        # print("Crawling completed. Process the result as needed.")
        # print(f"Result Markdown:\n{result.markdown}")
        # For example, you can save the result to a file or parse it further.
