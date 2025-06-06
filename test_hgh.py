import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Your existing crawler imports
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


class AssemblyDataProcessor:
    """
    SIMPLIFIED: Only processes state election data, ignores state links completely.
    Think of this like a Flutter service that handles only election data processing and storage.
    """

    def __init__(self, base_storage_path="state_assembly"):
        self.base_path = base_storage_path
        self.create_base_directory()

    def create_base_directory(self):
        """Creates the base directory structure"""
        Path(self.base_path).mkdir(exist_ok=True)
        print(f"✓ Base directory ready: {self.base_path}")

    def extract_state_name_from_url(self, url):
        """
        Extracts state name from the URL.
        Like parsing route parameters in Flutter navigation.
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            state_name = query_params.get('state', ['Unknown'])[0]
            return state_name.replace('%20', ' ')  # Handle URL encoding
        except Exception as e:
            print(f"⚠️ Could not extract state name from URL: {e}")
            return "Unknown_State"

    def identify_content_type(self, markdown_content):
        """
        Identifies if the content contains state election data.
        Like checking the type of data model you're working with in Flutter.
        SIMPLIFIED: Only looks for election data, ignores state links completely.
        """
        # Only check for year-wise election data
        state_election_pattern = r"#### \w+.*\d{4}"
        has_state_elections = bool(re.search(state_election_pattern, markdown_content))

        if has_state_elections:
            election_sections = len(re.findall(state_election_pattern, markdown_content))
            print(f"🎯 Found {election_sections} election sections - processing as state election data")
            return "state_elections"
        else:
            print("❌ No election data found")
            return "unknown"

    def save_state_assembly_links(self, markdown_content):
        """Saves the main state assembly links"""
        filename = "state_assembly_election_links.md"
        file_path = os.path.join(self.base_path, filename)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)

        print(f"✓ Saved main state assembly links to: {file_path}")
        return file_path

    def parse_state_elections_data(self, markdown_content, state_name):
        """
        Parses state-specific election data by year.
        Like parsing nested JSON objects in Flutter.
        FIXED: Now handles mismatched years between headers and URLs.
        """
        print(f"\n🔍 DEBUGGING: Parsing election data for {state_name}")
        print(f"📄 Content length: {len(markdown_content)} characters")

        # Debug: Show first few lines of content being parsed
        lines = markdown_content.split('\n')[:15]
        print(f"📝 First 15 lines of content to parse:")
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"   {i:2d}: {line.strip()}")

        # Split content by year headers - Fixed regex pattern
        split_pattern = rf"#### {re.escape(state_name)} (\d{{4}})"
        print(f"🔍 Using split pattern: {split_pattern}")

        # Find all year matches first
        year_matches = list(re.finditer(split_pattern, markdown_content))
        print(f"🎯 Found {len(year_matches)} year headers:")
        for match in year_matches:
            year = match.group(1)
            print(f"   • {state_name} {year} at position {match.start()}")

        if not year_matches:
            print("❌ No year headers found! Trying flexible pattern...")
            # Try more flexible pattern
            flexible_pattern = r"#### .*?(\d{4})"
            year_matches = list(re.finditer(flexible_pattern, markdown_content))
            print(f"🔍 Flexible pattern found {len(year_matches)} matches:")
            for match in year_matches:
                print(f"   • Match: '{match.group(0)}' -> Year: {match.group(1)}")

        year_data = {}

        for i, match in enumerate(year_matches):
            year = match.group(1)
            start_pos = match.start()

            # Find end position (start of next section or end of content)
            if i + 1 < len(year_matches):
                end_pos = year_matches[i + 1].start()
            else:
                # Look for end markers like "### State Assemblies" or end of content
                end_markers = [
                    r"###\s+State Assemblies",
                    r"### ",
                    r"\|\s+\*\*DONATE NOW\*\*"
                ]

                end_pos = len(markdown_content)
                for marker in end_markers:
                    marker_match = re.search(marker, markdown_content[start_pos:])
                    if marker_match:
                        end_pos = start_pos + marker_match.start()
                        break

            # Extract content for this year
            section_content = markdown_content[start_pos:end_pos].strip()

            print(f"\n📋 Processing {state_name} {year}:")
            print(f"   • Start position: {start_pos}")
            print(f"   • End position: {end_pos}")
            print(f"   • Content length: {len(section_content)} chars")
            print(f"   • First line: {section_content.split(chr(10))[0] if section_content else 'EMPTY'}")

            if section_content:
                # Try to detect actual year from URLs in content if needed
                actual_year = self._detect_year_from_urls(section_content)
                final_year = actual_year if actual_year else year

                if actual_year and actual_year != year:
                    print(f"🔧 Fixed year mismatch: Header said {year}, URLs indicate {actual_year}")

                year_data[final_year] = section_content
                print(f"✅ Added {state_name} {final_year} to results")
            else:
                print(f"⚠️ Empty content for {state_name} {year}")

        print(f"\n📊 PARSING SUMMARY:")
        print(f"   • Total years processed: {len(year_data)}")
        for year in sorted(year_data.keys()):
            content_length = len(year_data[year])
            print(f"   • {year}: {content_length} characters")

        return year_data

    def _detect_year_from_urls(self, content):
        """
        Detects the actual year from URLs in the content.
        Like extracting metadata from API responses in Flutter.
        """
        # Common URL patterns that contain years
        url_year_patterns = [
            r'/(\d{4})/',  # /2024/
            r'(\d{4})/',  # 2024/
            r'([a-zA-Z]+)(\d{4})/',  # state2024/
            r'/([a-zA-Z]+)(\d{2})/',  # /ap09/ -> 2009
        ]

        years_found = []

        for pattern in url_year_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle tuple matches (from grouped patterns)
                    for group in match:
                        if group.isdigit():
                            if len(group) == 2:  # 2-digit year like "09"
                                year = 2000 + int(group)  # Convert 09 -> 2009
                            elif len(group) == 4:  # 4-digit year
                                year = int(group)
                            else:
                                continue

                            # Only accept reasonable years (2000-2030)
                            if 2000 <= year <= 2030:
                                years_found.append(year)
                else:
                    # Handle single matches
                    if match.isdigit():
                        if len(match) == 2:
                            year = 2000 + int(match)
                        elif len(match) == 4:
                            year = int(match)
                        else:
                            continue

                        if 2000 <= year <= 2030:
                            years_found.append(year)

        # Return the most common year found, or None if no valid years
        if years_found:
            # Get most frequent year
            year_counts = {}
            for year in years_found:
                year_counts[year] = year_counts.get(year, 0) + 1

            most_common_year = max(year_counts, key=year_counts.get)
            return str(most_common_year)

        return None

    def save_state_elections_by_year(self, markdown_content, state_name):
        """
        Saves state election data organized by state first, then year.
        Structure: state_assembly/{state_name}/{year}/{state_name}.md
        Like organizing your Flutter app by features first, then by functionality.
        FIXED: Now extracts only the state-specific section, ignoring the general state list.
        """
        # Extract only the state-specific election section
        state_specific_content = self._extract_state_specific_content(markdown_content, state_name)

        if not state_specific_content:
            print(f"⚠️ No state-specific content found for {state_name}")
            return []

        year_data = self.parse_state_elections_data(state_specific_content, state_name)
        saved_files = []

        for year, content in year_data.items():
            # Create directory structure: state_assembly/{state_name}/{year}/
            state_dir = os.path.join(self.base_path, state_name.replace(" ", "_"))
            year_dir = os.path.join(state_dir, year)

            Path(year_dir).mkdir(parents=True, exist_ok=True)

            # Save file: {state_name}.md
            filename = f"{state_name.replace(' ', '_')}.md"
            file_path = os.path.join(year_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

            saved_files.append(file_path)
            print(f"✓ Saved {state_name} {year} data to: {file_path}")

        return saved_files

    def _extract_state_specific_content(self, markdown_content, state_name):
        """
        Extracts only the state-specific election content, ignoring the general state list.
        Like filtering specific data from a mixed API response in Flutter.
        """
        print(f"\n🔍 DEBUGGING: Extracting {state_name}-specific content")

        # Find the start of state-specific content
        state_header_pattern = rf"### {re.escape(state_name)} Assembly Election"
        state_match = re.search(state_header_pattern, markdown_content, re.IGNORECASE)

        if not state_match:
            print(f"⚠️ Could not find state header for {state_name}")
            print(f"🔍 Looking for pattern: {state_header_pattern}")

            # Try to find any mention of the state
            lines = markdown_content.split('\n')
            for i, line in enumerate(lines[:20]):
                if state_name.lower() in line.lower():
                    print(f"   Found '{state_name}' in line {i + 1}: {line.strip()}")

            # Try without "Assembly Election"
            simple_pattern = rf"### {re.escape(state_name)}"
            simple_match = re.search(simple_pattern, markdown_content, re.IGNORECASE)
            if simple_match:
                print(f"✅ Found simple state header: {simple_pattern}")
                state_match = simple_match
            else:
                return None
        else:
            print(f"✅ Found state header at position {state_match.start()}")

        # Find the end of state-specific content (where general state list starts)
        general_list_patterns = [
            r"###\s+State Assemblies\s+",
            r"\|\s+\*\*DONATE NOW\*\*",
            r"###\s+",  # Any other section header
        ]

        end_pos = len(markdown_content)
        end_reason = "end of content"

        for pattern in general_list_patterns:
            general_match = re.search(pattern, markdown_content[state_match.start():])
            if general_match:
                potential_end = state_match.start() + general_match.start()
                if potential_end < end_pos:
                    end_pos = potential_end
                    end_reason = f"found pattern: {pattern}"
                    break

        # Extract content between state header and end point
        state_content = markdown_content[state_match.start():end_pos].strip()

        print(f"📄 Extraction results:")
        print(f"   • Start position: {state_match.start()}")
        print(f"   • End position: {end_pos} ({end_reason})")
        print(f"   • Extracted length: {len(state_content)} characters")

        # Show first few lines of extracted content
        if state_content:
            lines = state_content.split('\n')[:10]
            print(f"📝 First 10 lines of extracted content:")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   {i:2d}: {line.strip()}")

        return state_content if state_content else None

    def process_crawled_data(self, markdown_content, source_url):
        """
        Main processor function that handles crawled election data only.
        Like a focused data handler in Flutter that only processes what you need.
        SIMPLIFIED: Only processes election data, completely ignores state links.
        """
        print(f"\n📊 Processing crawled data from: {source_url}")
        print("=" * 60)

        # Extract state name from URL
        state_name = self.extract_state_name_from_url(source_url)
        print(f"🏛️ State: {state_name}")

        # Check if we have election data
        content_type = self.identify_content_type(markdown_content)

        saved_files = []

        if content_type == "state_elections":
            # Process state-specific election data
            print(f"💾 Saving {state_name} election data by years...")
            files = self.save_state_elections_by_year(markdown_content, state_name)
            saved_files.extend(files)

        else:
            # No election data found - save as raw for debugging
            print("⚠️ No election data found - saving as raw data for manual review...")
            filename = f"raw_data_{state_name.replace(' ', '_')}.md"
            file_path = os.path.join(self.base_path, filename)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(f"# Raw Data from {source_url}\n")
                file.write(f"# No election data detected\n\n")
                file.write(markdown_content)

            saved_files.append(file_path)
            print(f"💾 Saved raw data to: {file_path}")

        print(f"\n✅ Processing complete! Saved {len(saved_files)} file(s)")
        return saved_files


async def assembly_candidate_link_crawler():
    """
    Your enhanced crawler function with integrated data processing.
    Think of this like a Flutter service method that fetches data and automatically stores it.
    """
    # Initialize the data processor
    data_processor = AssemblyDataProcessor()

    # Ask user for URL
    default_url = "https://www.myneta.info/state_assembly.php?state=Andhra%20Pradesh"
    user_url = input(f"Enter URL to crawl (press Enter for default '{default_url}'): ").strip()
    url = user_url if user_url else default_url

    print(f"🌐 Crawling: {url}")
    print("------------------------------------------------------------------------------------")

    # Your existing crawler configuration
    session_id = "session_id"
    browser_config = BrowserConfig(
        headless=False,
        browser_type="chromium",
    )
    md_generator = DefaultMarkdownGenerator()
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator,
        session_id=session_id,
    )

    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=run_config)

            if result.success:
                print("✅ Crawling successful!")

                # Process and save the crawled data
                saved_files = data_processor.process_crawled_data(
                    result.markdown,
                    url
                )

                # Optional: Print a summary
                print(f"\n📋 Summary:")
                print(f"   • Source URL: {url}")
                print(f"   • Files created: {len(saved_files)}")
                print(f"   • Storage location: {data_processor.base_path}")

                return {
                    'success': True,
                    'url': url,
                    'markdown': result.markdown,
                    'saved_files': saved_files,
                    'storage_path': data_processor.base_path
                }
            else:
                print("❌ Crawling failed!")
                print(f"Error: {result.error_message}")
                return {'success': False, 'error': result.error_message}

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return {'success': False, 'error': str(e)}


# Additional utility functions for batch processing
async def crawl_multiple_states(state_urls):
    """
    Crawl multiple state URLs in sequence.
    Like processing a list of API endpoints in Flutter.
    """
    results = []
    data_processor = AssemblyDataProcessor()

    for i, url in enumerate(state_urls, 1):
        print(f"\n🔄 Processing {i}/{len(state_urls)}: {url}")

        # Use the same crawler logic but without user input
        session_id = f"session_{i}"
        browser_config = BrowserConfig(headless=True, browser_type="chromium")
        md_generator = DefaultMarkdownGenerator()
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            markdown_generator=md_generator,
            session_id=session_id,
        )

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url, config=run_config)

                if result.success:
                    saved_files = data_processor.process_crawled_data(
                        result.markdown, url
                    )
                    results.append({
                        'url': url,
                        'success': True,
                        'saved_files': saved_files
                    })
                else:
                    results.append({
                        'url': url,
                        'success': False,
                        'error': result.error_message
                    })

        except Exception as e:
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })

    return results


# # Example usage
# if __name__ == "__main__":
#     import asyncio
#
#     # Single URL crawling
#     asyncio.run(assembly_candidate_link_crawler())
#
#     # Example of batch processing multiple states
#     # state_urls = [
#     #     "https://www.myneta.info/state_assembly.php?state=Andhra%20Pradesh",
#     #     "https://www.myneta.info/state_assembly.php?state=Karnataka",
#     #     "https://www.myneta.info/state_assembly.php?state=Tamil%20Nadu",
#     # ]
#     # results = asyncio.run(crawl_multiple_states(state_urls))