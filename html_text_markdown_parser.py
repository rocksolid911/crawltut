import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from election_year_folder_creater import create_output_folder


def extract_constituencies_from_html(html_content=None, input_file=None, output_folder=None, url=None):
    """
    Extract constituency information from HTML and save to specified output folder

    Args:
        html_content: HTML content as a string (takes precedence over input_file)
        input_file: Path to HTML file (used if html_content is not provided)
        output_folder: Path to save output files (default: created based on URL)
        url: URL of the data source (used for folder naming if output_folder not provided)
    """
    # If no output folder is specified, create one based on URL
    if not output_folder:
        output_folder = create_output_folder(url)

    # Extract year from URL for file naming
    year = "unknown_year"
    if url:
        # Try to extract year from different URL patterns
        year_match = re.search(r'LokSabha(\d{4})|ls(\d{4})', url, re.IGNORECASE)
        if year_match:
            year = year_match.group(1) or year_match.group(2)

    # File paths in output folder with year in filename
    txt_file_path = os.path.join(output_folder, f"constituencies_links_{year}.txt")
    md_file_path = os.path.join(output_folder, f"constituencies_links_{year}.md")
    raw_html_path = os.path.join(output_folder, f"raw_result_{year}.html")

    # Load HTML content - either from the provided string or from a file
    if html_content is None:
        # Default input file if not specified
        if not input_file:
            input_file = input("Enter path to HTML file (default: raw_result.html): ").strip() or "raw_result.html"

        # Check if the input path is absolute or should be under the output folder
        if not os.path.isabs(input_file) and not os.path.exists(input_file):
            # Try looking in the output folder
            potential_path = os.path.join(output_folder, input_file)
            if os.path.exists(potential_path):
                input_file = potential_path

        # Load the HTML content from file
        try:
            with open(input_file, "r", encoding="utf-8") as file:
                html_content = file.read()
        except FileNotFoundError:
            print(f"Error: HTML file '{input_file}' not found.")
            return None

    # Save the HTML content to a file in the output folder for reference
    with open(raw_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved raw HTML to {raw_html_path}")

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
                        if url:
                            base_url = url
                        else:
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
                            base_url = url or "https://www.myneta.info/LokSabha2024/"
                            if constituency_href and not constituency_href.startswith('http'):
                                constituency_href = urljoin(base_url, constituency_href)

                            states_data[state_name].append({
                                'name': constituency_name,
                                'href': constituency_href
                            })

    # If we still have no data, return an error
    if not states_data:
        print("Error: Could not extract constituency data from the HTML.")
        return None

    # Generate text file
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
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
    with open(md_file_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Constituency Links By State\n\n")

        total_constituencies = 0

        for state, constituencies in states_data.items():
            md_file.write(f"## {state} ({len(constituencies)} constituencies)\n\n")

            total_constituencies += len(constituencies)

            for constituency in constituencies:
                md_file.write(f"- [{constituency['name']}]({constituency['href']})\n")

            md_file.write("\n")

        md_file.write(f"**Total: {total_constituencies} constituencies across {len(states_data)} states/UTs**\n")

    print(f"Successfully extracted constituency links and saved to files in {output_folder}")
    print(f"Found {total_constituencies} constituencies across {len(states_data)} states/UTs")
    print(f"Files created: {txt_file_path}, {md_file_path},")

    return states_data

# # Run the extraction
# extract_constituencies_from_html()
