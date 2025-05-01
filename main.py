import asyncio
from crawl4ai import AsyncWebCrawler ,BrowserConfig, CrawlerRunConfig,CacheMode

async def main():
    browser_config = BrowserConfig(
        headless=False,
        browser_type="chromium",  # Use Chromium as the browser

    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.ENABLED,  # Ignore cache for fresh content
    )
    async with AsyncWebCrawler(config= browser_config) as crawler:
        result = await crawler.arun("https://www.myneta.info/",config=run_config)
        print(result.markdown)  # Print first 300 chars

if __name__ == "__main__":
    asyncio.run(main())
