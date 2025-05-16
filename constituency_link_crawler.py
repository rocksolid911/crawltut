from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode, DefaultMarkdownGenerator

from html_text_markdown_parser import extract_constituencies_from_html


async def customcrawler():
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
            "https://www.myneta.info/LokSabha2024/",
            config=run_config
        )

        extract_constituencies_from_html(
            html_content=result.cleaned_html,
            url="https://www.myneta.info/LokSabha2024/",

        )
        # # Save raw HTML to the new directory
        # raw_html_path = os.path.join(output_folder, "raw_result.html")
        # # Save raw HTML to debug
        # with open(raw_html_path, "w", encoding="utf-8") as f:
        #     f.write(result.cleaned_html)
        #
        #
