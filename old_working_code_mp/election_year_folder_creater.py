import re
import os


def create_output_folder(url):
    # Base output folder
    base_folder = "constituency_data"

    # Extract year from URL or use default
    year_match = re.search(r'LokSabha(\d{4})|ls(\d{4})', url, re.IGNORECASE)
    if year_match:
        # Use the first non-None group (either group 1 or group 2)
        year_folder = year_match.group(1) or year_match.group(2)
    else:
        year_folder = "unknown_year"

    output_folder = os.path.join(base_folder, year_folder)

    # Create the directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")
    else:
        print(f"Using existing directory: {output_folder}")

    return output_folder
