# crawlers/base_crawler.py
"""
Base crawler class for different election types
"""
import asyncio
import os
from abc import ABC, abstractmethod
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from typing import List, Tuple, Optional

from config.election_config import ElectionConfig
from utils.file_manager import ElectionFileManager
from parsers.content_parser import ContentParser


class BaseCrawler(ABC):
    """Base class for election data crawlers"""

    def __init__(self, config: ElectionConfig, file_manager: ElectionFileManager):
        self.config = config
        self.file_manager = file_manager
        self.parser = ContentParser()

    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration"""
        return BrowserConfig(
            headless=True,
            browser_type="chromium",
        )

    def get_run_config(self, session_id: str = "default_session") -> CrawlerRunConfig:
        """Get crawler run configuration"""
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id
        )

    @abstractmethod
    async def crawl_constituencies(self, url: str, state_filter: Optional[str] = None):
        """Crawl constituency data"""
        pass

    @abstractmethod
    async def crawl_candidates(self, year: str, state_filter: Optional[str] = None):
        """Crawl candidate data"""
        pass