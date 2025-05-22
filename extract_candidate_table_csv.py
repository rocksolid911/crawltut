import os
import re
import csv
import glob
from bs4 import BeautifulSoup

def extract_candidate_tables_to_csv(base_dir="constituency_data", output_file="candidates_data.csv"):
    """
    Extract candidate tables from all markdown files and export to a CSV.

    Args:
        base_dir: Base directory containing the constituency data
        output_file: Output CSV filename
    """
    # Fields to extract
    csv_fields = ["Year", "State", "Constituency", "SerialNo", "CandidateName", "Party",
                  "CriminalCases", "Education", "Age", "TotalAssets", "Liabilities", "Winner"]

    candidates_data = []

    # Find all markdown files recursively
    md_files = glob.glob(os.path.join(base_dir, "**", "*.md"), recursive=True)
    print(f"Found {len(md_files)} markdown files to process")

    for md_file in md_files:
        try:
            # Extract year, state and constituency from file path
            path_parts = md_file.split(os.sep)
            if len(path_parts) >= 4:  # Ensure path has enough parts
                year = path_parts[-4] if path_parts[-4].isdigit() else None
                state = path_parts[-3].replace('%20', ' ')
                constituency = path_parts[-2].replace('%20', ' ')

                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find the candidates table using regex
                table_pattern = r'\| SNo\s+\| Candidate.*?\n(.*?)(?=\n\n|\**DONATE NOW|\Z)'
                table_match = re.search(table_pattern, content, re.DOTALL)

                if not table_match:
                    continue

                table_content = table_match.group(1)
                rows = table_content.split('\n')

                for row in rows:
                    if not row.strip() or '---|---' in row:
                        continue

                    # Extract cells from the row
                    cells = re.split(r'\s*\|\s*', row.strip('| \t'))

                    # Ensure we have enough cells
                    if len(cells) >= 7:
                        serial_no = cells[0].strip()

                        # Extract candidate name from markdown link
                        candidate_link = re.search(r'\[(.*?)\]', cells[1])
                        candidate_name = candidate_link.group(1) if candidate_link else cells[1].strip()

                        # Check if candidate is winner
                        is_winner = "Yes" if "** Winner **" in cells[1] else "No"

                        party = cells[2].strip()
                        criminal_cases = cells[3].strip('* ')
                        education = cells[4].strip()
                        age = cells[5].strip()
                        assets = cells[6].strip()
                        liabilities = cells[7].strip() if len(cells) > 7 else ""

                        # Clean up values that contain image references
                        if "image_v2.php" in assets:
                            assets = "Not Available"
                        if "image_v2.php" in liabilities:
                            liabilities = "Not Available"

                        candidates_data.append({
                            "Year": year,
                            "State": state,
                            "Constituency": constituency,
                            "SerialNo": serial_no,
                            "CandidateName": candidate_name,
                            "Party": party,
                            "CriminalCases": criminal_cases,
                            "Education": education,
                            "Age": age,
                            "TotalAssets": assets,
                            "Liabilities": liabilities,
                            "Winner": is_winner
                        })

        except Exception as e:
            print(f"Error processing {md_file}: {str(e)}")

    # Write data to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(candidates_data)

    print(f"CSV file created with {len(candidates_data)} candidates at {output_file}")
    return output_file

if __name__ == "__main__":
    extract_candidate_tables_to_csv()