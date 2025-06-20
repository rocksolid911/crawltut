


import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def main():
    browser_config = BrowserConfig()  # Default browser configuration
    run_config = CrawlerRunConfig()   # Default crawl run configuration

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://www.myneta.info/LokSabha2024/candidate.php?candidate_id=5268",
            config=run_config
        )
        print(result.markdown)  #




if __name__ == "__main__":
    asyncio.run(main())