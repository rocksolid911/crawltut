# parsers/content_parser.py
"""
Enhanced content parsing utilities
"""
import re
import markdown
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional
from config.election_config import ElectionConfig


class ContentParser:
    """Handles parsing of various content types"""

    @staticmethod
    def parse_constituency_links(md_content: str) -> List[Tuple[str, str, str]]:
        """Extract constituency names and links from markdown content"""
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        matches = []

        for link in links:
            url = link.get('href')
            name = link.text

            # More flexible ID extraction for different election types
            id_patterns = [
                r'constituency_id=(\d+)',
                r'candidate_id=(\d+)',
                r'ac_id=(\d+)',  # Assembly constituency ID
                r'id=(\d+)'
            ]

            constituency_id = None
            for pattern in id_patterns:
                id_match = re.search(pattern, url)
                if id_match:
                    constituency_id = id_match.group(1)
                    break

            if constituency_id:
                matches.append((name.strip(), url, constituency_id))

        print(f"Found {len(matches)} constituencies")
        return matches

    @staticmethod
    def extract_location_from_markdown(markdown_content: str, config: ElectionConfig) -> Optional[str]:
        """Extract location/state from markdown content based on election type"""
        lines = markdown_content.splitlines()

        # Different patterns for different election types
        if config.constituency_type == "lok_sabha":
            pattern = r"### List of Candidates - (.+?):"
        else:
            # Assembly elections might have different patterns
            pattern = r"### (?:Assembly )?Constituency - (.+?):|### (.+?) Assembly Constituency"

        for line in lines:
            match = re.search(pattern, line)
            if match:
                location = match.group(1) or match.group(2) if match.lastindex > 1 else match.group(1)
                if '[' in location:
                    location = location.split('(', 1)[0].strip()
                return location.strip()

        return None