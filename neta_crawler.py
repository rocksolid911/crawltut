import asyncio
import re
import os
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode


class MyNetaHierarchicalCrawlerFixed:
    """
    A class to crawl MyNeta.info hierarchically (State -> Constituency -> Candidate)
    and extract all candidate profile URLs - with fixed initialization
    """

    def __init__(self, base_url="https://www.myneta.info/LokSabha2024", output_file="candidate_links.txt"):
        self.base_url = base_url
        self.output_file = output_file
        self.candidate_pattern = re.compile(r'candidate\.php\?candidate_id=\d+')

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

        # Initialize the output file with headers
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write("# MyNeta.info Candidate Links\n")
            f.write("# Format: State > Constituency > Candidate URL\n\n")

    async def crawl(self):
        """
        Main crawling method that orchestrates the hierarchical crawling process
        """
        # Create crawler - FIX: Initialize with default config, set config later
        async with AsyncWebCrawler(
        config=BrowserConfig(
        headless=True,  # Run headless for faster processing
        browser_type="chromium",  # Use Chromium as the browser
        java_script_enabled=True )
        ) as crawler:
            # Start with the main page
            print(f"Crawling main page: {self.base_url}")

            # Configure the browser properly
            browser_config = {
                'headless': True,  # Run headless for faster processing
                'java_script_enabled': True,  # Enable JavaScript
                'viewport_width': 1366,  # Set viewport size
                'viewport_height': 768
            }

            config = CrawlerRunConfig(
               # wait_for="css:.dropbtnJS", # Wait for dropdown buttons to load
                cache_mode=CacheMode.BYPASS,  # Bypass cache to ensure fresh content
                # Pass browser config here instead
            )

            try:
                # Get the main page
                result = await crawler.arun(self.base_url, config=config)

                if not result.success:
                    print(f"Failed to load main page: {result.error_message}")
                    return

                # Parse the main page to find state buttons
                main_soup = BeautifulSoup(result.html, 'html.parser')
                state_buttons = main_soup.find_all('button', class_='w3-button w3-block dropbtnJS')

                print(f"Found {len(state_buttons)} state buttons")

                # Process each state
                for state_idx, state_button in enumerate(state_buttons, 1):
                    # Extract state name and item ID
                    state_name = state_button.text.strip().split('<span')[0].strip()
                    onclick_attr = state_button.get('onclick', '')

                    # Extract item ID from onclick attribute
                    item_id_match = re.search(r"handle_dropdown\('item', '(\d+)'\)", onclick_attr)
                    if not item_id_match:
                        print(f"Could not extract item ID for state: {state_name}")
                        continue

                    item_id = item_id_match.group(1)

                    print(f"\n[{state_idx}/{len(state_buttons)}] Processing state: {state_name} (item_{item_id})")

                    # Find dropdown content for this state
                    dropdown = main_soup.find('div', id=f'item_{item_id}')
                    if not dropdown:
                        print(f"  Could not find dropdown content for state: {state_name}")
                        continue

                    # Extract constituency links from dropdown
                    constituency_links = dropdown.find_all('a',
                                                           href=lambda href: href and 'action=show_candidates' in href)

                    # Skip the "ALL CONSTITUENCIES" link
                    constituency_links = [link for link in constituency_links if 'ALL CONSTITUENCIES' not in link.text]

                    print(f"  Found {len(constituency_links)} constituencies")

                    # Write state header to file
                    with open(self.output_file, 'a', encoding='utf-8') as f:
                        f.write(f"## {state_name}\n\n")

                    # Process each constituency
                    for const_idx, const_link in enumerate(constituency_links, 1):
                        constituency_name = const_link.text.strip()
                        constituency_href = const_link.get('href', '')
                        constituency_url = self.get_full_url(constituency_href)

                        print(f"  [{const_idx}/{len(constituency_links)}] Processing constituency: {constituency_name}")

                        # Write constituency header to file
                        with open(self.output_file, 'a', encoding='utf-8') as f:
                            f.write(f"### {constituency_name}\n\n")

                        # Crawl constituency page to find candidate links
                        await self.process_constituency(crawler, constituency_url, constituency_name)

                        # Add a newline after each constituency
                        with open(self.output_file, 'a', encoding='utf-8') as f:
                            f.write("\n")

                        # Small delay to avoid overwhelming the server
                        await asyncio.sleep(0.5)

                print("\nCrawling complete!")

            except Exception as e:
                print(f"Error during crawling: {str(e)}")

    async def process_constituency(self, crawler, constituency_url, constituency_name):
        """
        Process a constituency page to extract candidate links

        Args:
            crawler: AsyncWebCrawler instance
            constituency_url: URL of the constituency page
            constituency_name: Name of the constituency
        """
        # Use the same browser config approach as above
        browser_config = {
            'headless': True,
            'java_script_enabled': True,
            'viewport_width': 1366,
            'viewport_height': 768
        }

        config = CrawlerRunConfig(
            wait_for="css:table.table",  # Wait for candidates table to load
            cache_mode=CacheMode.BYPASS,  # Bypass cache
            # Pass browser config here instead
        )

        try:
            # Get the constituency page
            result = await crawler.arun(constituency_url, config=config)

            if not result.success:
                print(f"    Failed to load constituency page: {result.error_message}")
                return

            # Parse the constituency page to find candidate links
            const_soup = BeautifulSoup(result.html, 'html.parser')
            candidate_links = const_soup.find_all('a', href=lambda href: href and self.candidate_pattern.search(href))

            print(f"    Found {len(candidate_links)} candidate links")

            # Write candidate links to file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                for cand_link in candidate_links:
                    candidate_url = self.get_full_url(cand_link.get('href', ''))
                    f.write(f"- {candidate_url}\n")

        except Exception as e:
            print(f"    Error processing constituency {constituency_name}: {str(e)}")

    def get_full_url(self, href):
        """
        Convert relative URLs to absolute URLs

        Args:
            href (str): Relative or absolute URL

        Returns:
            str: Absolute URL
        """
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return f"{self.base_url}{href}"
        else:
            return f"{self.base_url}/{href}"


async def main():
    print("MyNeta.info Hierarchical Crawler (Fixed)")
    print("=====================================\n")

    # Get base URL (default to 2024 Lok Sabha)
    base_url = input(
        "Enter the base URL (default: https://www.myneta.info/LokSabha2024): ") or "https://www.myneta.info/LokSabha2024"

    # Get output file name
    output_file = input(
        "Enter output file name (default: myneta_candidates_hierarchical.txt): ") or "myneta_candidates_hierarchical.txt"

    # Create and run the crawler
    crawler = MyNetaHierarchicalCrawlerFixed(base_url=base_url, output_file=output_file)
    await crawler.crawl()

    print(f"\nAll candidate links have been saved to {output_file}")
    print("Links are organized by state and constituency")


if __name__ == "__main__":
    asyncio.run(main())