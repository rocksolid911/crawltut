# crawlers/candidate_crawler.py
"""
Candidate crawler implementation
"""
import os
import asyncio
from typing import Optional

from crawl4ai import AsyncWebCrawler

from crawlers.base_crawler import BaseCrawler


class CandidateCrawler(BaseCrawler):
    """Crawls detailed candidate information"""

    async def crawl_constituencies(self, url: str, state_filter: Optional[str] = None):
        """Not implemented in candidate crawler"""
        raise NotImplementedError("Use ConstituencyCrawler for constituency data extraction")

    async def crawl_candidates(self, year: str, state_filter: Optional[str] = None):
        """Crawl candidate data from constituencies"""
        # Get constituency data
        md_file = self.file_manager.get_constituency_md_file(self.config, year)
        if not md_file:
            print(f"Error: No constituency markdown file found for {self.config.name} {year}")
            return

        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        constituency_data = self.parser.parse_constituency_links(md_content)

        # Filter by state if specified
        if state_filter:
            constituency_data = [data for data in constituency_data
                                 if state_filter.lower() in data[0].lower()]
            if not constituency_data:
                print(f"No constituencies found for state: {state_filter}")
                return

        browser_config = self.get_browser_config()
        run_config = self.get_run_config("candidate_session")

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for i, (name, url, constituency_id) in enumerate(constituency_data):
                print(f"Processing {i + 1}/{len(constituency_data)}: {name}")

                try:
                    await asyncio.sleep(2)  # Rate limiting

                    result = await crawler.arun(url, config=run_config)

                    # Extract location information
                    location = self.parser.extract_location_from_markdown(
                        result.markdown, self.config
                    )

                    # Create appropriate directory structure
                    output_dir = self._create_output_directory(year, location, name)

                    # Save the data
                    self._save_candidate_data(output_dir, name, constituency_id, result.markdown)

                    print(f"✓ Saved data for {name} to {output_dir}")

                except Exception as e:
                    print(f"✗ Error processing {name}: {str(e)}")

    def _create_output_directory(self, year: str, location: str, constituency_name: str) -> str:
        """Create appropriate directory structure based on election type and existing conventions"""

        if self.config.constituency_type == "lok_sabha":
            # Existing MP structure: constituency_data/{year}/{state}/{district}/
            if "(" in constituency_name:
                district_name = constituency_name.split("(")[0].strip()
            else:
                district_name = constituency_name.strip()

            clean_district = district_name.replace(' ', '_').replace('-', '_')
            output_dir = os.path.join("constituency_data", year, location or "unknown_state", clean_district)
        else:
            # State assembly structure: state_assembly/{state_name}/{district_name}/
            clean_constituency = constituency_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            output_dir = os.path.join("state_assembly", self.config.state_name, clean_constituency)

        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _save_candidate_data(self, output_dir: str, name: str, constituency_id: str, markdown_content: str):
        """Save candidate data to file"""
        clean_name = name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        md_file_path = os.path.join(output_dir, f"{clean_name}_{constituency_id}.md")

        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)