import asyncio
from crawl4ai import AsyncWebCrawler ,BrowserConfig, CrawlerRunConfig,CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

async def main():
    browser_config = BrowserConfig(
        headless=False,
        browser_type="chromium",  # Use Chromium as the browser

    )
    md_generator = DefaultMarkdownGenerator(
        content_filter = PruningContentFilter(threshold=10)
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator
    )
    async with AsyncWebCrawler(config= browser_config) as crawler:
        result = await crawler.arun("https://www.myneta.info/LokSabha2019/candidate.php?candidate_id=5560",config=run_config)
        print(result.markdown.fit)

if __name__ == "__main__":
    asyncio.run(main())
