"""
Member of Legislative Assembly (MLA) crawler.

This module crawls MLA candidate data from state assembly pages on myneta.info.
"""
import asyncio
import os
from typing import List, Optional

from src.crawlers.base_crawler import BaseCrawler
from src.utils.csv_utils import read_candidates_from_csv
from config.settings import INDIAN_STATES, get_scraper_config


class MLACrawler(BaseCrawler):
    """Crawler for Member of Legislative Assembly candidates."""

    async def crawl_state_assembly(self, state: str, output_dir: str = "state_assembly") -> bool:
        """
        Crawl state assembly page for a specific state.

        Args:
            state: Name of the state
            output_dir: Directory to save the output

        Returns:
            True if successful, False otherwise
        """
        try:
            scraper_config = get_scraper_config()
            url = scraper_config.get_state_assembly_url(state)

            print(f"Crawling state assembly for: {state}")
            print(f"URL: {url}")

            from crawl4ai import AsyncWebCrawler

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                markdown = await self.crawl_url(url, crawler)

                # Create state directory
                state_dir = os.path.join(output_dir, state.replace(' ', '_'))
                os.makedirs(state_dir, exist_ok=True)

                # Save markdown file
                output_file = os.path.join(state_dir, f"assembly_{state.replace(' ', '_')}.md")
                self.save_markdown(markdown, output_file)

                return True

        except Exception as e:
            print(f"Error processing state {state}: {str(e)}")
            return False

    async def crawl_multiple_states(self, state_urls: List[str], output_dir: str = "state_assembly") -> None:
        """
        Crawl multiple state assembly pages.

        Args:
            state_urls: List of state assembly URLs
            output_dir: Directory to save the output
        """
        # Extract state names from URLs and crawl them
        for url in state_urls:
            try:
                # Extract state name from URL
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                query_params = urllib.parse.parse_qs(parsed.query)
                state = query_params.get('state', ['Unknown'])[0]

                await self.crawl_state_assembly(state, output_dir)

            except Exception as e:
                print(f"Error processing URL {url}: {e}")

    async def crawl_all_states(self, output_dir: str = "state_assembly") -> None:
        """
        Crawl all Indian states.

        Args:
            output_dir: Directory to save the output
        """
        print(f"Starting crawl for {len(INDIAN_STATES)} states...")

        for state in INDIAN_STATES:
            await self.crawl_state_assembly(state, output_dir)

    async def run(self, states: Optional[List[str]] = None, output_dir: str = "state_assembly") -> None:
        """
        Run the MLA crawler.

        Args:
            states: Optional list of states to crawl. If None, crawls all states.
            output_dir: Directory to save the output
        """
        if states:
            for state in states:
                await self.crawl_state_assembly(state, output_dir)
        else:
            await self.crawl_all_states(output_dir)


async def run_mla_crawler(states: Optional[List[str]] = None) -> None:
    """
    Run MLA crawler for specified states or all states.

    Args:
        states: Optional list of states to crawl. If None, crawls all states.
    """
    crawler = MLACrawler()
    await crawler.run(states=states)
