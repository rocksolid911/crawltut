# crawlers/constituency_crawler.py
"""
Constituency crawler implementation
"""
from crawl4ai import AsyncWebCrawler

from crawlers.base_crawler import BaseCrawler
from parsers.html_parser import HTMLParser
from typing import Optional


class ConstituencyCrawler(BaseCrawler):
    """Crawls constituency links and basic information"""

    async def crawl_constituencies(self, url: str, state_filter: Optional[str] = None):
        """Crawl constituency links from the main page"""
        print(f"Crawling constituencies from: {url}")
        print("---" * 30)

        browser_config = self.get_browser_config()
        run_config = self.get_run_config("constituency_session")

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=run_config)

            # Create output folder
            output_folder = self.file_manager.create_output_folder(self.config, url)

            # Parse and save constituency data
            parser = HTMLParser(self.config)
            states_data = parser.extract_constituencies_from_html(
                html_content=result.cleaned_html,
                url=url,
                output_folder=output_folder
            )

            return states_data

    async def crawl_candidates(self, year: str, state_filter: Optional[str] = None):
        """Not implemented in constituency crawler"""
        raise NotImplementedError("Use CandidateCrawler for candidate data extraction")