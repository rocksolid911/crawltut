# parsers/html_parser.py
"""
HTML parsing utilities for different election types
"""
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List, Optional
from config.election_config import ElectionConfig


class HTMLParser:
    """Parses HTML content for election data"""

    def __init__(self, config: ElectionConfig):
        self.config = config

    def extract_constituencies_from_html(self, html_content: str, url: str, output_folder: str) -> Dict:
        """Extract constituency information from HTML and save to files"""
        # Extract year for file naming
        year = self.config.extract_year_from_url(url)

        # File paths
        txt_file_path = os.path.join(output_folder, f"constituencies_links_{year}.txt")
        md_file_path = os.path.join(output_folder, f"constituencies_links_{year}.md")
        raw_html_path = os.path.join(output_folder, f"raw_result_{year}.html")

        # Save raw HTML
        with open(raw_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Saved raw HTML to {raw_html_path}")

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        states_data = self._extract_states_data(soup, url)

        if not states_data:
            print("Error: Could not extract constituency data from the HTML.")
            return None

        # Save data to files
        self._save_to_txt(txt_file_path, states_data)
        self._save_to_markdown(md_file_path, states_data)

        total_constituencies = sum(len(constituencies) for constituencies in states_data.values())
        print(f"Successfully extracted constituency links and saved to files in {output_folder}")
        print(f"Found {total_constituencies} constituencies across {len(states_data)} states/regions")

        return states_data

    def _extract_states_data(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract states and constituencies data from soup"""
        states_data = {}

        # Method 1: Look for extracted results div
        results_div = soup.find('div', id='extracted-results')
        if results_div:
            states_data = self._parse_extracted_results(results_div, url)

        # Method 2: Look for h3 elements with state names
        if not states_data:
            states_data = self._parse_h3_structure(soup, url)

        # Method 3: Look for button-based navigation (common in assembly sites)
        if not states_data:
            states_data = self._parse_button_structure(soup, url)

        return states_data

    def _parse_extracted_results(self, results_div, url: str) -> Dict:
        """Parse extracted results div structure"""
        states_data = {}
        state_sections = results_div.find_all(['h3', 'ul'])
        current_state = None

        for section in state_sections:
            if section.name == 'h3':
                state_text = section.text
                state_match = re.match(r'(.+?)\s*\((\d+) constituencies\)', state_text)
                if state_match:
                    current_state = state_match.group(1).strip()
                    states_data[current_state] = []
            elif section.name == 'ul' and current_state:
                for li in section.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag:
                        constituency_name = a_tag.text.strip()
                        constituency_href = self._make_absolute_url(a_tag.get('href', ''), url)
                        states_data[current_state].append({
                            'name': constituency_name,
                            'href': constituency_href
                        })

        return states_data

    def _parse_h3_structure(self, soup: BeautifulSoup, url: str) -> Dict:
        """Parse h3-based structure"""
        states_data = {}
        h3_elements = soup.find_all('h3')

        for h3 in h3_elements:
            # Look for constituency lists after h3
            next_sibling = h3.find_next_sibling(['ul', 'div'])
            if next_sibling:
                state_name = h3.text.strip()
                # Clean state name
                state_name = re.sub(r'\(\d+\s+constituencies?\)', '', state_name).strip()

                constituencies = []
                links = next_sibling.find_all('a')
                for link in links:
                    if link.get('href') and 'constituency' in link.get('href', '').lower():
                        constituencies.append({
                            'name': link.text.strip(),
                            'href': self._make_absolute_url(link.get('href'), url)
                        })

                if constituencies:
                    states_data[state_name] = constituencies

        return states_data

    def _parse_button_structure(self, soup: BeautifulSoup, url: str) -> Dict:
        """Parse button-based navigation structure"""
        states_data = {}

        # Look for dropdown buttons or navigation elements
        buttons = soup.find_all(['button', 'a'],
                                text=re.compile(r'constituency|assembly|lok sabha', re.I))

        for button in buttons:
            # Find associated dropdown or list
            parent = button.find_parent(['div', 'section'])
            if parent:
                links = parent.find_all('a')
                valid_links = []

                for link in links:
                    href = link.get('href', '')
                    if any(keyword in href.lower() for keyword in ['constituency', 'candidate', 'ac_id']):
                        valid_links.append({
                            'name': link.text.strip(),
                            'href': self._make_absolute_url(href, url)
                        })

                if valid_links:
                    # For assembly elections, we might not have state separation
                    if self.config.constituency_type == "assembly":
                        state_name = self.config.name.split()[0]  # e.g., "Andhra" from "Andhra Pradesh Assembly"
                    else:
                        state_name = button.text.strip()

                    states_data[state_name] = valid_links

        return states_data

    @staticmethod
    def _make_absolute_url(href: str, base_url: str) -> str:
        """Convert relative URL to absolute"""
        if href and not href.startswith('http'):
            return urljoin(base_url, href)
        return href

    @staticmethod
    def _save_to_txt(file_path: str, states_data: Dict):
        """Save data to text file"""
        with open(file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write("CONSTITUENCY LINKS BY STATE/REGION\n")
            txt_file.write("=" * 40 + "\n\n")

            total_constituencies = 0
            for state, constituencies in states_data.items():
                txt_file.write(f"{state} ({len(constituencies)} constituencies)\n")
                txt_file.write("-" * (len(state) + 20) + "\n")

                total_constituencies += len(constituencies)
                for constituency in constituencies:
                    txt_file.write(f"  {constituency['name']}: {constituency['href']}\n")
                txt_file.write("\n")

            txt_file.write(f"\nTotal: {total_constituencies} constituencies across {len(states_data)} states/regions\n")

    @staticmethod
    def _save_to_markdown(file_path: str, states_data: Dict):
        """Save data to markdown file"""
        with open(file_path, "w", encoding="utf-8") as md_file:
            md_file.write("# Constituency Links By State/Region\n\n")

            total_constituencies = 0
            for state, constituencies in states_data.items():
                md_file.write(f"## {state} ({len(constituencies)} constituencies)\n\n")

                total_constituencies += len(constituencies)
                for constituency in constituencies:
                    md_file.write(f"- [{constituency['name']}]({constituency['href']})\n")
                md_file.write("\n")

            md_file.write(
                f"**Total: {total_constituencies} constituencies across {len(states_data)} states/regions**\n")