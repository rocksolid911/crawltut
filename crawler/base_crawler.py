"""
Base crawler class with common functionality.
Eliminates duplication of async processing and batch handling logic.
"""
import asyncio
from typing import List, Tuple, Optional, Any
from crawl4ai import AsyncWebCrawler
from .core import WebCrawlerConfig


class BaseCrawler:
    """Base class for all crawlers with common async processing functionality."""
    
    def __init__(self, browser_config=None, batch_size=50):
        """Initialize base crawler with configuration."""
        self.browser_config = browser_config or WebCrawlerConfig.get_default_browser_config()
        self.batch_size = batch_size
    
    async def crawl_single_url(self, crawler: AsyncWebCrawler, url: str, run_config) -> Any:
        """Crawl a single URL and return the result."""
        try:
            result = await crawler.arun(url, config=run_config)
            return result
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return None
    
    async def crawl_urls_batch(self, urls: List[str], run_config, process_result_callback=None) -> List[Any]:
        """
        Crawl URLs in batches to avoid overwhelming the server.
        
        Args:
            urls: List of URLs to crawl
            run_config: Crawler run configuration
            process_result_callback: Optional callback to process each result
            
        Returns:
            List of crawl results
        """
        results = []
        batches = self._create_batches(urls)
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} URLs)")
                
                # Create tasks for the batch
                tasks = [
                    self.crawl_single_url(crawler, url, run_config)
                    for url in batch
                ]
                
                # Execute batch and collect results
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results if callback provided
                if process_result_callback:
                    for i, result in enumerate(batch_results):
                        if result and not isinstance(result, Exception):
                            process_result_callback(result, batch[i])
                
                results.extend(batch_results)
                
                # Small delay between batches to be respectful to the server
                if batch_num < len(batches):
                    await asyncio.sleep(1)
        
        return results
    
    async def crawl_url_pairs_batch(self, url_pairs: List[Tuple[str, Any]], run_config, 
                                   process_result_callback=None) -> List[Any]:
        """
        Crawl URL pairs (url, associated_data) in batches.
        
        Args:
            url_pairs: List of tuples (url, associated_data)
            run_config: Crawler run configuration
            process_result_callback: Optional callback to process each result
            
        Returns:
            List of crawl results
        """
        results = []
        batches = self._create_batches(url_pairs)
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for batch_num, batch in enumerate(batches, 1):
                print(f"Processing batch {batch_num}/{len(batches)} ({len(batch)} URL pairs)")
                
                # Create tasks for the batch
                tasks = [
                    self.crawl_single_url(crawler, url, run_config)
                    for url, _ in batch
                ]
                
                # Execute batch and collect results
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results if callback provided
                if process_result_callback:
                    for i, result in enumerate(batch_results):
                        if result and not isinstance(result, Exception):
                            url, associated_data = batch[i]
                            process_result_callback(result, url, associated_data)
                
                results.extend(batch_results)
                
                # Small delay between batches
                if batch_num < len(batches):
                    await asyncio.sleep(1)
        
        return results
    
    def _create_batches(self, items: List[Any]) -> List[List[Any]]:
        """Create batches from a list of items."""
        return [items[i:i + self.batch_size] for i in range(0, len(items), self.batch_size)]
    
    def validate_url(self, url: str) -> bool:
        """Validate that a URL is properly formatted."""
        if not url or not isinstance(url, str):
            return False
        return url.startswith('http://') or url.startswith('https://')
    
    def filter_valid_urls(self, urls: List[str]) -> List[str]:
        """Filter out invalid URLs from a list."""
        return [url for url in urls if self.validate_url(url)]