from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, DefaultMarkdownGenerator

from html_text_markdown_parser import extract_constituencies_from_html


async def customcrawler():
    # Ask user for URL
    default_url = "https://www.myneta.info/LokSabha2024/"
    user_url = input(f"Enter URL to crawl (press Enter for default '{default_url}'): ").strip()
    url = user_url if user_url else default_url

    print(f"Crawling: {url}")
    print("------------------------------------------------------------------------------------")
    print(f"Crawling: {url}")
    print("This will extract constituency links for the specified election.")
    print("Data will be saved in constituency_data/[year] folder structure.")
    print("Please wait while the crawler navigates the page...")
    print("------------------------------------------------------------------------------------")

    session_id = "session_id"
    browser_config = BrowserConfig(
        headless=False,
        browser_type="chromium",
        # Increase timeout to handle all the dropdowns
    )
    md_generator = DefaultMarkdownGenerator(
        # content_filter=PruningContentFilter(threshold=10)
        # content_source='fit_html'

    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        # js_code=js_command,
        markdown_generator=md_generator,
        session_id=session_id,

    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url,
            config=run_config
        )

        extract_constituencies_from_html(
            html_content=result.cleaned_html,
            url=url,

        )

