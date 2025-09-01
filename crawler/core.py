"""
Core crawler configuration and utilities.
Centralizes browser config and common crawler setup to eliminate duplication.
"""
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode


class WebCrawlerConfig:
    """Centralized configuration for web crawlers to eliminate duplication across files."""
    
    @staticmethod
    def get_default_browser_config(headless=True, browser_type="chromium"):
        """Get default browser configuration used across all crawlers."""
        return BrowserConfig(
            headless=headless,
            browser_type=browser_type,
        )
    
    @staticmethod
    def get_default_run_config(session_id="default_session", cache_mode=CacheMode.BYPASS):
        """Get default crawler run configuration."""
        return CrawlerRunConfig(
            cache_mode=cache_mode,
            session_id=session_id,
        )
    
    @staticmethod
    def get_candidate_config(session_id="session_id_candidate"):
        """Get configuration specifically for candidate crawling."""
        return WebCrawlerConfig.get_default_run_config(session_id=session_id)
    
    @staticmethod
    def get_constituency_config(session_id="session_id_constituency"):
        """Get configuration specifically for constituency crawling."""
        return WebCrawlerConfig.get_default_run_config(session_id=session_id)