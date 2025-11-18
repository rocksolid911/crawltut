"""
Base crawler functionality that can be reused across different crawler types.
"""
import asyncio
import os
from abc import ABC, abstractmethod
from typing import Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

from config.settings import CrawlerConfig, get_crawler_config


class BaseCrawler(ABC):
    """
    Abstract base class for all crawlers.

    This provides common functionality for web crawling operations.
    """

    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        Initialize the base crawler.

        Args:
            config: Optional crawler configuration. If not provided, uses global config.
        """
        self.config = config or get_crawler_config()
        self.browser_config = self._create_browser_config()
        self.run_config = self._create_run_config()

    def _create_browser_config(self) -> BrowserConfig:
        """Create browser configuration."""
        return BrowserConfig(
            headless=self.config.headless,
            browser_type=self.config.browser_type,
        )

    def _create_run_config(self) -> CrawlerRunConfig:
        """Create crawler run configuration."""
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=self.config.session_id,
        )

    async def crawl_url(self, url: str, crawler: AsyncWebCrawler) -> str:
        """
        Crawl a single URL and return markdown content.

        Args:
            url: The URL to crawl
            crawler: The AsyncWebCrawler instance

        Returns:
            Markdown content of the page
        """
        try:
            await asyncio.sleep(self.config.delay_between_requests)
            result = await crawler.arun(url, config=self.run_config)
            return result.markdown if hasattr(result, 'markdown') else str(result)
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            raise

    async def crawl_urls_batch(self, urls: list[str], batch_size: Optional[int] = None) -> dict[str, str]:
        """
        Crawl multiple URLs in batches.

        Args:
            urls: List of URLs to crawl
            batch_size: Number of URLs to process concurrently. Defaults to config batch_size.

        Returns:
            Dictionary mapping URLs to their markdown content
        """
        batch_size = batch_size or self.config.batch_size
        results = {}

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            # Split URLs into batches
            batches = [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]

            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} URLs)")

                # Create tasks for this batch
                tasks = [self.crawl_url(url, crawler) for url in batch]

                # Wait for all tasks to complete
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # Store results
                for url, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        print(f"Error processing {url}: {result}")
                        results[url] = None
                    else:
                        results[url] = result

        return results

    def save_markdown(self, content: str, output_path: str) -> None:
        """
        Save markdown content to a file.

        Args:
            content: Markdown content to save
            output_path: Path where the file should be saved
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {output_path}")

    @abstractmethod
    async def run(self, **kwargs):
        """
        Main entry point for the crawler.

        This method should be implemented by subclasses to define
        the specific crawling workflow.
        """
        pass


class ConstituencyCrawler(BaseCrawler):
    """Crawler for constituency pages."""

    async def crawl_constituency(self, name: str, url: str, constituency_id: str,
                                year: int, output_dir: str) -> bool:
        """
        Crawl a single constituency page.

        Args:
            name: Constituency name
            url: Constituency URL
            constituency_id: Constituency identifier
            year: Election year
            output_dir: Directory to save the output

        Returns:
            True if successful, False otherwise
        """
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print(f"Crawling: {name} (ID: {constituency_id})")

                # Fetch the page
                markdown = await self.crawl_url(url, crawler)

                # Save the markdown file
                clean_name = name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
                output_file = os.path.join(output_dir, f"{clean_name}_{constituency_id}.md")
                self.save_markdown(markdown, output_file)

                return True

        except Exception as e:
            print(f"Error processing {name}: {str(e)}")
            return False

    async def run(self, constituencies: list, year: int, output_base_dir: str):
        """
        Run the constituency crawler for multiple constituencies.

        Args:
            constituencies: List of (name, url, id) tuples
            year: Election year
            output_base_dir: Base directory for output
        """
        output_dir = os.path.join(output_base_dir, str(year))
        os.makedirs(output_dir, exist_ok=True)

        for name, url, constituency_id in constituencies:
            await self.crawl_constituency(name, url, constituency_id, year, output_dir)


class CandidateCrawler(BaseCrawler):
    """Base crawler for candidate data."""

    def get_candidate_output_dir(self, base_dir: str, candidate_name: str) -> str:
        """
        Get the output directory for a candidate.

        Args:
            base_dir: Base directory
            candidate_name: Name of the candidate

        Returns:
            Path to candidate directory
        """
        safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
        candidate_dir = os.path.join(base_dir, safe_name)
        os.makedirs(candidate_dir, exist_ok=True)
        return candidate_dir

    def get_candidate_files(self, candidate_dir: str, candidate_name: str) -> tuple[str, str]:
        """
        Get the paths for candidate JSON and image files.

        Args:
            candidate_dir: Directory for candidate data
            candidate_name: Name of the candidate

        Returns:
            Tuple of (json_path, image_path)
        """
        safe_name = "".join([c if c.isalnum() else "_" for c in candidate_name]).rstrip("_")
        json_path = os.path.join(candidate_dir, f"{safe_name}.json")
        image_path = os.path.join(candidate_dir, f"{safe_name}.jpg")
        return json_path, image_path

    async def run(self, **kwargs):
        """Implemented by subclasses."""
        pass
