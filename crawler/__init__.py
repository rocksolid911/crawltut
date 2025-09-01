"""
Crawler package for election data collection.

This package provides specialized crawlers for different types of Indian elections:
- MP (Lok Sabha) elections
- MLA (State Assembly) elections

All crawlers inherit from BaseCrawler and use centralized configuration.
"""

from .mp_crawler import MPCrawler
from .mla_crawler import MLACrawler
from .base_crawler import BaseCrawler
from .core import WebCrawlerConfig

__all__ = ['MPCrawler', 'MLACrawler', 'BaseCrawler', 'WebCrawlerConfig']