import os
import re
import csv
import glob

def extract_candidate_tables_to_csv(base_dir="constituency_data"):
    """
    Extract candidate tables from Markdown files and create district-specific CSV files.

    Args:
        base_dir: Base directory containing the constituency data
    """
    # Fields to extract - adding CandidateURL field
    csv_fields = ["Year", "State", "Constituency", "SerialNo", "CandidateName", "Party",
                  "CriminalCases", "Education", "Age", "TotalAssets", "Liabilities", "Winner", "CandidateURL"]

    # Find all Markdown files recursively
    md_files = glob.glob(os.path.join(base_dir, "**", "*.md"), recursive=True)
    print(f"Found {len(md_files)} markdown files to process")

    # Group files by directory
    dir_to_files = {}
    for md_file in md_files:
        directory = os.path.dirname(md_file)
        if directory not in dir_to_files:
            dir_to_files[directory] = []
        dir_to_files[directory].append(md_file)

    total_candidates = 0
    total_csvs = 0

    # Process each directory
    for directory, files in dir_to_files.items():
        candidates_data = []

        # Extract path components
        path_parts = directory.split(os.sep)
        if len(path_parts) < 4:
            continue  # Skip if a path does not have a year/state/district structure

        year = path_parts[-3] if path_parts[-3].isdigit() else "unknown_year"
        state = path_parts[-2].replace('%20', ' ')
        district = path_parts[-1].replace('%20', ' ')

        # Process each markdown file in the directory
        for md_file in files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract constituency ID from filename
                filename = os.path.basename(md_file)
                constituency_id = re.search(r'_(\d+)\.md$', filename)
                constituency_id = constituency_id.group(1) if constituency_id else "unknown"

                # Look for candidate rows directly - each row starts with a number followed by a pipe
                # This is more reliable than looking for table headers
                candidate_pattern = r'^\s*(\d+)\s*\|\s*\[(.*?)\]'

                # Find all candidate rows
                for line in content.split('\n'):
                    # Skip empty lines and separator lines
                    if not line.strip() or '---|---' in line:
                        continue

                    # Check if this looks like a candidate row (starts with a number)
                    row_match = re.match(candidate_pattern, line, re.MULTILINE)
                    if not row_match:
                        continue

                    # It's a candidate row - now parse it
                    cells = [cell.strip() for cell in line.split('|')]
                    cells = [cell for cell in cells if cell]  # Remove empty cells

                    if len(cells) < 7:
                        continue  # Not enough data

                    try:
                        serial_no = cells[0].strip()

                        # Extract candidate name from Markdown link
                        candidate_cell = cells[1]

                        # Extract both name and URL from markdown link [Name](URL)
                        link_match = re.search(r'\[(.*?)\]\((.*?)\)', candidate_cell)
                        if link_match:
                            candidate_name = link_match.group(1)
                            candidate_url = link_match.group(2)
                        else:
                            # Try alternative pattern [Name]
                            name_match = re.search(r'\[(.*?)\]', candidate_cell)
                            candidate_name = name_match.group(1) if name_match else candidate_cell.strip()
                            candidate_url = ""  # No URL found

                        # Check if candidate is winner
                        is_winner = "Yes" if "** Winner **" in candidate_cell else "No"

                        # Get remaining fields
                        party = cells[2].strip() if len(cells) > 2 else ""
                        criminal_cases = cells[3].strip('* ') if len(cells) > 3 else ""
                        education = cells[4].strip() if len(cells) > 4 else ""
                        age = cells[5].strip() if len(cells) > 5 else ""

                        # Assets and liabilities might contain image references
                        assets = cells[6].strip() if len(cells) > 6 else ""
                        if "image_v2.php" in assets:
                            assets = "Not Available"

                        liabilities = cells[7].strip() if len(cells) > 7 else ""
                        if "image_v2.php" in liabilities:
                            liabilities = "Not Available"

                        candidates_data.append({
                            "Year": year,
                            "State": state,
                            "Constituency": district,
                            "SerialNo": serial_no,
                            "CandidateName": candidate_name,
                            "Party": party,
                            "CriminalCases": criminal_cases,
                            "Education": education,
                            "Age": age,
                            "TotalAssets": assets,
                            "Liabilities": liabilities,
                            "Winner": is_winner,
                            "CandidateURL": candidate_url
                        })
                    except Exception as e:
                        print(f"Error processing row in {md_file}: {str(e)}")

            except Exception as e:
                print(f"Error processing {md_file}: {str(e)}")

        # Create a CSV for this district if we have data
        if candidates_data:
            # Create CSV filename
            csv_filename = f"{district}.csv"
            csv_path = os.path.join(directory, csv_filename)

            # Write data to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
                writer.writeheader()
                writer.writerows(candidates_data)

            total_candidates += len(candidates_data)
            total_csvs += 1
            print(f"Created CSV for {year}/{state}/{district} with {len(candidates_data)} candidates")

    print(f"Process complete: Created {total_csvs} CSV files with {total_candidates} total candidates.")

if __name__ == "__main__":
    extract_candidate_tables_to_csv()