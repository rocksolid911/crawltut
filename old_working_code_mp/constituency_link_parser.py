import re
import markdown
from bs4 import BeautifulSoup


def parse_constituency_links(md_content):
    """
    Extract constituency names and their corresponding links from markdown content

    Args:
        md_content: Content of the markdown file as string

    Returns:
        List of tuples [(constituency_name, link, constituency_id)]
    """
    # Option 1: Using regex (faster but less robust)
    # link_pattern = r'\- \[(.*?)\]\((https://.*?constituency_id=(\d+))\)'
    # matches = re.findall(link_pattern, md_content)

    # Option 2: Using markdown parser (more robust)
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    matches = []
    for link in links:
        url = link.get('href')
        name = link.text
        id_match = re.search(r'constituency_id=(\d+)', url)
        if id_match:
            constituency_id = id_match.group(1)
            matches.append((name, url, constituency_id))

    # Return list of tuples (constituency_name, url, constituency_id)
    constituency_data = [(name.strip(), url, constituency_id)
                         for name, url, constituency_id in matches]

    print(f"Found {len(constituency_data)} constituencies")
    return constituency_data
