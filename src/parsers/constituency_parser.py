"""
Parser for constituency data from markdown content.
"""
import re
from typing import List, Tuple, Optional


def parse_constituency_links(markdown_content: str) -> List[Tuple[str, str, str]]:
    """
    Parse constituency links from markdown content.

    Args:
        markdown_content: Markdown content containing constituency links

    Returns:
        List of tuples (name, url, constituency_id)
    """
    constituencies = []

    # Pattern to match constituency links in markdown
    # Example: [Constituency Name](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    matches = re.findall(pattern, markdown_content)

    for name, url in matches:
        # Extract constituency ID from URL if present
        constituency_id = extract_constituency_id_from_url(url)
        if constituency_id:
            constituencies.append((name.strip(), url.strip(), constituency_id))

    return constituencies


def extract_constituency_id_from_url(url: str) -> Optional[str]:
    """
    Extract constituency ID from a URL.

    Args:
        url: The URL to extract ID from

    Returns:
        Constituency ID or None
    """
    # Try to extract numeric ID from URL
    # Example: https://example.com/constituency123.php -> 123
    match = re.search(r'(\d+)', url)
    if match:
        return match.group(1)

    # If no numeric ID, use a hash of the URL
    return None


def extract_location_from_markdown(markdown_content: str) -> Optional[str]:
    """
    Extract location/state name from markdown content.

    Args:
        markdown_content: Markdown content

    Returns:
        Location name or None
    """
    lines = markdown_content.splitlines()

    for line in lines:
        # Look for lines like "### List of Candidates - STATE NAME:"
        if line.startswith("### List of Candidates - "):
            # Extract the part after the dash
            after_dash = line.split('- ', 1)[1]

            # If there's a colon, get the part before it
            if ':' in after_dash:
                location = after_dash.split(':', 1)[0].strip()
                return location

            # If there's a square bracket, get the part before it
            if '[' in after_dash:
                location = after_dash.split('[', 1)[0].strip()
                return location

            return after_dash.strip()

    return None


def extract_district_from_name(constituency_name: str) -> str:
    """
    Extract district name from constituency name.

    Args:
        constituency_name: Full constituency name (may include district in parentheses)

    Returns:
        District name
    """
    if "(" in constituency_name:
        return constituency_name.split("(")[0].strip()
    return constituency_name.strip()


def clean_name_for_path(name: str) -> str:
    """
    Clean a name to be used in file paths.

    Args:
        name: Original name

    Returns:
        Cleaned name suitable for use in file paths
    """
    return name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('/', '_')
