"""
CSV utility functions for reading and writing candidate data.
"""
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional


def read_candidates_from_csv(csv_path: str, winners_only: bool = False) -> List[Dict[str, str]]:
    """
    Read candidate data from a CSV file.

    Args:
        csv_path: Path to the CSV file
        winners_only: If True, only include winners

    Returns:
        List of dictionaries containing candidate data
    """
    candidates = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            # Skip if winners_only and candidate is not a winner
            if winners_only and len(row) > 11 and row[11].strip().lower() != 'yes':
                continue

            # Extract candidate information
            if len(row) >= 13:
                candidate_name = row[4]
                candidate_link = row[12]

                # Validate that the link is a proper HTTP/HTTPS URL
                if candidate_link and isinstance(candidate_link, str) and (
                        candidate_link.startswith('http://') or candidate_link.startswith('https://')):
                    candidates.append({
                        'name': candidate_name,
                        'url': candidate_link,
                        'row_data': row
                    })

    return candidates


def log_missing_image(csv_path: str, candidate_name: str, candidate_url: str, reason: str,
                     state: Optional[str] = None, year: Optional[str] = None,
                     constituency: Optional[str] = None,
                     output_csv: str = "missing_profile_images.csv") -> None:
    """
    Log missing image information to a CSV file.

    Args:
        csv_path: Source CSV path
        candidate_name: Name of the candidate
        candidate_url: URL of the candidate profile
        reason: Reason why image is missing
        state: State name (optional)
        year: Election year (optional)
        constituency: Constituency name (optional)
        output_csv: Output CSV file path
    """
    csv_headers = ['timestamp', 'state', 'year', 'constituency', 'candidate_name',
                   'url', 'reason', 'source_csv']

    csv_exists = os.path.exists(output_csv)

    try:
        with open(output_csv, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            if not csv_exists:
                csv_writer.writerow(csv_headers)
                print(f"Created missing images tracking file: {output_csv}")

            # Extract info from path if not provided
            if not all([state, year, constituency]):
                path_parts = csv_path.replace('\\', '/').split('/')
                if len(path_parts) >= 4:
                    try:
                        year = year or path_parts[-4]
                        state = state or path_parts[-3]
                        constituency = constituency or path_parts[-2]
                    except IndexError:
                        pass

            csv_writer.writerow([
                datetime.now().isoformat(),
                state or "Unknown",
                year or "Unknown",
                constituency or "Unknown",
                candidate_name,
                candidate_url,
                reason,
                os.path.basename(csv_path)
            ])

    except Exception as e:
        print(f"Error writing to missing images CSV: {e}")


def write_candidates_to_csv(candidates: List[Dict], output_path: str,
                           headers: Optional[List[str]] = None) -> None:
    """
    Write candidate data to a CSV file.

    Args:
        candidates: List of candidate dictionaries
        output_path: Path to output CSV file
        headers: Optional list of column headers
    """
    if not candidates:
        print(f"No candidates to write to {output_path}")
        return

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Use provided headers or infer from first candidate
    if headers is None:
        headers = list(candidates[0].keys())

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(candidates)

    print(f"Wrote {len(candidates)} candidates to {output_path}")


def get_csv_path_from_json(json_output_file: str) -> str:
    """
    Extract CSV path from JSON file path.

    Args:
        json_output_file: Path to JSON file

    Returns:
        Path to corresponding CSV file
    """
    try:
        candidate_dir = os.path.dirname(json_output_file)
        parent_dir = os.path.dirname(candidate_dir)
        csv_files = [f for f in os.listdir(parent_dir) if f.endswith('.csv')]
        if csv_files:
            return os.path.join(parent_dir, csv_files[0])
    except:
        pass
    return "unknown.csv"
