# processors/csv_processor.py
"""
Enhanced CSV processing for different election types
"""
import os
import re
import csv
import glob
from typing import List, Dict, Optional
from config.election_config import ElectionConfig


class CSVProcessor:
    """Processes markdown data and creates CSV files"""

    def __init__(self, config: ElectionConfig):
        self.config = config
        self.csv_fields = [
            "Year", "State", "Constituency", "SerialNo", "CandidateName",
            "Party", "CriminalCases", "Education", "Age", "TotalAssets",
            "Liabilities", "Winner", "CandidateURL"
        ]

    def extract_candidate_tables_to_csv(self, base_dir: str = ".") -> None:
        """Extract candidate tables from Markdown files and create CSV files"""
        # Find all markdown files for this election type
        if self.config.constituency_type == "lok_sabha":
            search_pattern = os.path.join(base_dir, "constituency_data", "*", "**", "*.md")
        else:
            search_pattern = os.path.join(base_dir, "state_assembly", self.config.state_name, "**", "*.md")

        md_files = glob.glob(search_pattern, recursive=True)

        print(f"Found {len(md_files)} markdown files to process for {self.config.name}")

        # Group files by directory for district-level CSVs
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

            # Extract path components based on election type
            path_info = self._extract_path_info(directory)
            if not path_info:
                continue

            year, state, constituency = path_info

            # Process each markdown file in the directory
            for md_file in files:
                try:
                    candidates = self._extract_candidates_from_md(md_file, year, state, constituency)
                    candidates_data.extend(candidates)
                except Exception as e:
                    print(f"Error processing {md_file}: {str(e)}")

            # Create CSV for this constituency/district
            if candidates_data:
                csv_filename = f"{constituency}.csv"
                csv_path = os.path.join(directory, csv_filename)

                self._write_csv(csv_path, candidates_data)

                total_candidates += len(candidates_data)
                total_csvs += 1
                print(f"Created CSV for {year}/{state}/{constituency} with {len(candidates_data)} candidates")

        print(f"Process complete: Created {total_csvs} CSV files with {total_candidates} total candidates.")

    def _extract_path_info(self, directory: str) -> Optional[tuple]:
        """Extract year, state, constituency from directory path based on folder structure"""
        path_parts = directory.split(os.sep)

        if self.config.constituency_type == "lok_sabha":
            # constituency_data/{year}/{state}/{district}/
            if "constituency_data" in path_parts:
                idx = path_parts.index("constituency_data")
                if len(path_parts) > idx + 3:
                    year = path_parts[idx + 1]
                    state = path_parts[idx + 2].replace('%20', ' ')
                    district = path_parts[idx + 3].replace('%20', ' ')
                    return year, state, district
        else:
            # state_assembly/{state_name}/{district}/
            if "state_assembly" in path_parts:
                idx = path_parts.index("state_assembly")
                if len(path_parts) > idx + 2:
                    state = path_parts[idx + 1].replace('%20', ' ')
                    district = path_parts[idx + 2].replace('%20', ' ')
                    # For assembly, we extract year from config or use current year
                    year = "2024"  # You can make this more dynamic
                    return year, state, district

        return None

    def _extract_candidates_from_md(self, md_file: str, year: str, state: str, constituency: str) -> List[Dict]:
        """Extract candidate data from a single markdown file"""
        candidates_data = []

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract constituency ID from filename
        filename = os.path.basename(md_file)
        constituency_id = re.search(r'_(\d+)\.md', filename)
        constituency_id = constituency_id.group(1) if constituency_id else "unknown"

        # Candidate row pattern - more flexible for different election types
        candidate_pattern = r'^\s*(\d+)\s*\|\s*\[(.*?)\]'

        for line in content.split('\n'):
            if not line.strip() or '---|---' in line:
                continue

            row_match = re.match(candidate_pattern, line, re.MULTILINE)
            if not row_match:
                continue

            # Parse the candidate row
            cells = [cell.strip() for cell in line.split('|')]
            cells = [cell for cell in cells if cell]

            if len(cells) < 7:
                continue

            try:
                candidate_data = self._parse_candidate_row(cells, year, state, constituency)
                if candidate_data:
                    candidates_data.append(candidate_data)
            except Exception as e:
                print(f"Error processing row in {md_file}: {str(e)}")

        return candidates_data

    def _parse_candidate_row(self, cells: List[str], year: str, state: str, constituency: str) -> Optional[Dict]:
        """Parse individual candidate row"""
        try:
            serial_no = cells[0].strip()

            # Extract candidate name and URL from markdown link
            candidate_cell = cells[1]
            link_match = re.search(r'\[(.*?)\]\((.*?)\)', candidate_cell)

            if link_match:
                candidate_name = link_match.group(1)
                candidate_url = link_match.group(2)
            else:
                name_match = re.search(r'\[(.*?)\]', candidate_cell)
                candidate_name = name_match.group(1) if name_match else candidate_cell.strip()
                candidate_url = ""

            # Check if candidate is winner
            is_winner = "Yes" if "** Winner **" in candidate_cell else "No"

            # Extract other fields with better error handling
            party = cells[2].strip() if len(cells) > 2 else ""
            criminal_cases = cells[3].strip('* ') if len(cells) > 3 else ""
            education = cells[4].strip() if len(cells) > 4 else ""
            age = cells[5].strip() if len(cells) > 5 else ""

            # Handle assets and liabilities (might contain image references)
            assets = cells[6].strip() if len(cells) > 6 else ""
            if "image_v2.php" in assets or "Rs ~" in assets:
                assets = re.sub(r'Rs ~\s*', '', assets)
                assets = "Not Available" if "image_v2.php" in assets else assets

            liabilities = cells[7].strip() if len(cells) > 7 else ""
            if "image_v2.php" in liabilities or "Rs ~" in liabilities:
                liabilities = re.sub(r'Rs ~\s*', '', liabilities)
                liabilities = "Not Available" if "image_v2.php" in liabilities else liabilities

            return {
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
                "Winner": is_winner,
                "CandidateURL": candidate_url
            }
        except Exception as e:
            print(f"Error parsing candidate row: {e}")
            return None

    def _write_csv(self, csv_path: str, candidates_data: List[Dict]) -> None:
        """Write candidate data to CSV file"""
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.csv_fields)
            writer.writeheader()
            writer.writerows(candidates_data)