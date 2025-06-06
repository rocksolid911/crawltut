import asyncio
import os
import re
import glob

from mla_link_crawler import crawl_mla_data_with_link


def extract_all_winners_links():
    """
    Extract all Winners links from the state assembly markdown files

    Returns:
        List of all winner URLs extracted from markdown files
    """
    base_dir = "state_assembly"
    winners_links = []

    # Check if the base directory exists
    if not os.path.exists(base_dir):
        print(f"Error: Base directory '{base_dir}' not found.")
        return winners_links

    # Find all markdown files in the state_assembly directory and its subdirectories
    markdown_files = glob.glob(os.path.join(base_dir, "**/*.md"), recursive=True)

    # Regular expression to extract Winners links
    winners_pattern = r'\* \[Winners\]\((https?://[^\s)]+)\)'

    for file_path in markdown_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Extract state and year from file path
                path_parts = file_path.split(os.sep)
                state = path_parts[1] if len(path_parts) > 1 else "Unknown"
                year = path_parts[2] if len(path_parts) > 2 else "Unknown"

                # Find all winners links
                matches = re.findall(winners_pattern, content)

                for url in matches:
                    # winners_links.append({
                    #     "state": state,
                    #     "year": year,
                    #     "url": url
                    # })
                    print(f"Processing winners link for {state} {year}: {url}")
                    asyncio.run(crawl_mla_data_with_link(url, state, year))

                    print(f"Found winners link for {state} {year}: {url}")

        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

    print(f"Total winners links found: {len(winners_links)}")

    # # Save to a file
    # with open("all_winners_links.txt", "w", encoding="utf-8") as f:
    #     for item in winners_links:
    #         f.write(f"{item['state']},{item['year']},{item['url']}\n")
    #
    # print("All winners links saved to all_winners_links.txt")
    #
    # return winners_links

# Example usage:
# winners_links = extract_all_winners_links()