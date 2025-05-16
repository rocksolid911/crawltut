import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_constituencies_from_html():
    # Load the HTML content
    with open("constituencies_raw.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main div containing the extracted results
    results_div = soup.find('div', id='extracted-results')

    # If this div doesn't exist, it may be the last div containing the h3 elements
    if not results_div:
        # Find all divs that might contain our data
        results_div = soup.find('div',
                                text=lambda text: text and 'Extracted Constituencies with Links by State' in text)
        if not results_div:
            # Look for the div containing h3 elements with state names
            h3_elements = soup.find_all('h3')
            if h3_elements:
                # Get the parent of the first h3 element
                results_div = h3_elements[0].parent

    # Initialize dictionary to store states and constituencies
    states_data = {}

    # Extract state sections
    if results_div:
        # Approach 1: Using h3 and ul structures
        state_sections = results_div.find_all(['h3', 'ul'])
        current_state = None

        for section in state_sections:
            if section.name == 'h3':
                # Extract state name and constituency count
                state_text = section.text
                state_match = re.match(r'(.+?)\s*\((\d+) constituencies\)', state_text)
                if state_match:
                    current_state = state_match.group(1).strip()
                    states_data[current_state] = []
            elif section.name == 'ul' and current_state:
                # Extract constituencies in this ul element
                for li in section.find_all('li'):
                    a_tag = li.find('a')
                    if a_tag:
                        constituency_name = a_tag.text.strip()
                        constituency_href = a_tag.get('href', '')

                        # Make the URL absolute if it's relative
                        base_url = "https://www.myneta.info/LokSabha2024/"
                        if constituency_href and not constituency_href.startswith('http'):
                            constituency_href = urljoin(base_url, constituency_href)

                        states_data[current_state].append({
                            'name': constituency_name,
                            'href': constituency_href
                        })

    # If the approach above didn't work, try a more generic approach
    if not states_data:
        # Look for all button elements that might be state names
        state_buttons = soup.select('button')

        for button in state_buttons:
            state_name = button.text.strip()
            if state_name and not state_name.startswith('DONATE') and not state_name.startswith('About'):
                # Find the associated dropdown content
                closest_div = button.find_next('div')
                if closest_div:
                    # Find all constituency links
                    constituency_links = closest_div.select('a')
                    if constituency_links:
                        states_data[state_name] = []

                        # Skip the first link which is usually "ALL CONSTITUENCIES"
                        for link in constituency_links[1:]:
                            constituency_name = link.text.strip()
                            constituency_href = link.get('href', '')

                            # Make the URL absolute if it's relative
                            base_url = "https://www.myneta.info/LokSabha2024/"
                            if constituency_href and not constituency_href.startswith('http'):
                                constituency_href = urljoin(base_url, constituency_href)

                            states_data[state_name].append({
                                'name': constituency_name,
                                'href': constituency_href
                            })

    # Generate text file
    with open("constituencies_links.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write("CONSTITUENCY LINKS BY STATE\n")
        txt_file.write("==========================\n\n")

        total_constituencies = 0

        for state, constituencies in states_data.items():
            txt_file.write(f"{state} ({len(constituencies)} constituencies)\n")
            txt_file.write("-" * (len(state) + 4 + len(str(len(constituencies))) + 16) + "\n")

            total_constituencies += len(constituencies)

            for constituency in constituencies:
                txt_file.write(f"  {constituency['name']}: {constituency['href']}\n")

            txt_file.write("\n")

        txt_file.write(f"\nTotal: {total_constituencies} constituencies across {len(states_data)} states/UTs\n")

    # Generate markdown file
    with open("constituencies_links.md", "w", encoding="utf-8") as md_file:
        md_file.write("# Constituency Links By State\n\n")

        total_constituencies = 0

        for state, constituencies in states_data.items():
            md_file.write(f"## {state} ({len(constituencies)} constituencies)\n\n")

            total_constituencies += len(constituencies)

            for constituency in constituencies:
                md_file.write(f"- [{constituency['name']}]({constituency['href']})\n")

            md_file.write("\n")

        md_file.write(f"**Total: {total_constituencies} constituencies across {len(states_data)} states/UTs**\n")

    print(f"Successfully extracted constituency links and saved to files.")
    print(f"Found {total_constituencies} constituencies across {len(states_data)} states/UTs")
    print(f"Files created: constituencies_links.txt and constituencies_links.md")

    return states_data


# # Run the extraction
# extract_constituencies_from_html()