import csv
import re
import os


def extract_candidates_from_markdown(markdown_content):
    """
    Extract candidate data from your markdown content and save as CSV.
    UPDATED: Now works with any state and year, not just Andhra Pradesh 2009.
    FIXED: Better bye-election detection with improved regex patterns.
    """

    print("🚀 Extracting candidate data from markdown...")

    # Debug: Show what bye-election patterns we're looking for
    bye_test = "bye" in markdown_content.lower() or "by-election" in markdown_content.lower()
    print(f"🔍 Debug: Contains 'bye' or 'by-election': {bye_test}")

    # Generic pattern for main election table - works for any state/year
    # Looks for: "### List of Winners in [ANY STATE] [ANY YEAR]"
    main_pattern = r'### List of Winners in [^#\n]*?(?:(?:19|20)\d{2}|Election).*?Sno \| Candidate.*?\n-+\|-+.*?\n(.*?)(?=### List of Winners in.*?Bye|### [^L]|$)'
    main_match = re.search(main_pattern, markdown_content, re.DOTALL)

    # FIXED bye-election patterns - improved to capture more content
    bye_patterns = [
        # Pattern 1: Standard format - capture until end markers
        r'### List of Winners in.*?(?:Bye-?Elections?|By-?Elections?).*?Sno \| Candidate.*?\n-+\|-+.*?\n(.*?)(?=\n\|.*?DONATE|\*\*Disclaimer|\nFollow us|\n### (?!List)|\n\n\||\n\n\*\*|$)',

        # Pattern 2: Capture everything from bye-election header - more greedy
        r'### List of Winners in.*?(?:Bye-?Elections?|By-?Elections?)(.*?)(?=\n\|.*?DONATE|\*\*Disclaimer|\nFollow us|\n### (?!List)|\n\n\||$)',

        # Pattern 3: Most greedy - capture until very specific end markers
        r'(?i)### List of Winners in.*?bye.*?elections?(.*?)(?=\*\*disclaimer|\n\|.*?donate|\nfollow us|\n### [^l]|$)',

        # Pattern 4: Alternative - look for bye section and grab everything until footer
        r'(?i)bye.*?elections?.*?(sno \| candidate.*?)(?=\*\*disclaimer|\|.*?donate|follow us|### |$)'
    ]

    main_candidates = []
    bye_candidates = []

    if main_match:
        main_table = main_match.group(1)
        main_candidates = parse_table_rows(main_table, "main_election")
        print(f"✅ Found {len(main_candidates)} main election candidates")
    else:
        print("⚠️ No main election table found - trying alternative pattern...")
        # Alternative pattern - just look for any table with candidates
        alt_pattern = r'Sno \| Candidate.*?\n-+\|-+.*?\n(.*?)(?=### |$)'
        alt_match = re.search(alt_pattern, markdown_content, re.DOTALL)
        if alt_match:
            main_table = alt_match.group(1)
            main_candidates = parse_table_rows(main_table, "main_election")
            print(f"✅ Found {len(main_candidates)} candidates using alternative pattern")

    # Try multiple bye-election patterns
    bye_match = None
    pattern_used = 0

    for i, pattern in enumerate(bye_patterns, 1):
        bye_match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)
        if bye_match:
            print(f"✅ Bye-election pattern {i} matched!")
            pattern_used = i
            break
        else:
            print(f"⚠️ Bye-election pattern {i} failed")

    if bye_match:
        bye_content = bye_match.group(1)
        print(f"🔍 Raw bye-election content length: {len(bye_content)} chars")
        print(f"🔍 First 300 chars: {bye_content[:300]}...")

        # Check for "Coming Soon" or similar placeholder text
        if any(phrase in bye_content.lower() for phrase in ['coming soon', 'under construction', 'not available']):
            print("⚠️ Bye-election section shows 'Coming Soon' - no data available")
            bye_candidates = []
        else:
            # Different processing based on content type
            if len(bye_content.strip()) <= 5:
                print("⚠️ Bye-election content too short - likely just a number or placeholder")
                bye_candidates = []
            elif 'sno | candidate' in bye_content.lower() or 'Sno | Candidate' in bye_content:
                print("🔍 Found table header in bye content, extracting table...")

                # Find table header (case insensitive)
                table_start = -1
                for marker in ['Sno | Candidate', 'sno | candidate', 'SNO | CANDIDATE']:
                    pos = bye_content.find(marker)
                    if pos >= 0:
                        table_start = pos
                        break

                if table_start >= 0:
                    table_content = bye_content[table_start:]

                    # Find the data rows (after header separator)
                    separator_patterns = ['---|---|', '---', '-+-']
                    data_start = -1

                    for sep in separator_patterns:
                        pos = table_content.find(sep)
                        if pos >= 0:
                            data_start = pos + len(sep)
                            break

                    if data_start >= 0:
                        bye_table = table_content[data_start:]
                        print(f"🔍 Extracted table data: {len(bye_table)} chars")
                        print(f"🔍 Table preview: {bye_table[:200]}...")
                        bye_candidates = parse_table_rows(bye_table, "bye_election")
                        print(f"✅ Found {len(bye_candidates)} bye-election candidates from table")
                    else:
                        print("⚠️ No table separator found, trying direct parse...")
                        bye_candidates = parse_table_rows(bye_content, "bye_election")
                        print(f"✅ Found {len(bye_candidates)} bye-election candidates (direct)")
                else:
                    print("⚠️ Table header found but position detection failed")
                    bye_candidates = []
            else:
                print("⚠️ No proper table structure found, trying to find table rows...")
                # Try to find ANY table-like structure
                lines = bye_content.split('\n')
                table_lines = []

                for line in lines:
                    # Look for lines that look like table rows (contain | and have multiple columns)
                    if '|' in line and len(line.split('|')) >= 6:
                        # Check if first column looks like a number
                        first_col = line.split('|')[0].strip()
                        if first_col.isdigit():
                            table_lines.append(line)

                if table_lines:
                    print(f"🔍 Found {len(table_lines)} potential table rows")
                    for i, line in enumerate(table_lines[:3]):
                        print(f"   Row {i + 1}: {line[:100]}...")

                    table_content = '\n'.join(table_lines)
                    bye_candidates = parse_table_rows(table_content, "bye_election")
                    print(f"✅ Extracted {len(bye_candidates)} candidates from table rows")
                else:
                    print("⚠️ No table rows found in bye-election content")
                    bye_candidates = []
    else:
        print("⚠️ No bye-election section found with any pattern")
        bye_candidates = []

    return main_candidates, bye_candidates


def parse_table_rows(table_content, election_type):
    """Parse table rows and extract candidate data"""
    candidates = []
    lines = table_content.split('\n')

    for line in lines:
        line = line.strip()
        if not line or '|' not in line:
            continue

        # Check if line starts with a number (candidate row)
        if re.match(r'^\d+\s*\|', line):
            candidate = parse_candidate_row(line, election_type)
            if candidate:
                candidates.append(candidate)

    return candidates


def parse_candidate_row(row, election_type):
    """Parse individual candidate row"""
    try:
        columns = [col.strip() for col in row.split('|')]

        if len(columns) < 7:
            return None

        # Extract candidate name and URL from column 1
        name_column = columns[1]

        # Pattern: [](url1)[Name](url2)
        name_pattern = r'\]\([^)]*\)\[([^\]]+)\]\(([^)]+)\)'
        name_match = re.search(name_pattern, name_column)

        if name_match:
            name = name_match.group(1).strip()
            candidate_url = name_match.group(2).strip()
        else:
            # Fallback: extract any name in brackets
            fallback_name = re.search(r'\[([^\]]+)\]', name_column)
            name = fallback_name.group(1).strip() if fallback_name else "Unknown"

            # Extract any URL in parentheses
            fallback_url = re.search(r'\(([^)]+)\)', name_column)
            candidate_url = fallback_url.group(1).strip() if fallback_url else ""

        # Extract criminal cases (look for **number**)
        criminal_text = columns[4].strip()
        criminal_match = re.search(r'\*\*(\d+)\*\*', criminal_text)
        criminal_cases = criminal_match.group(1) if criminal_match else "0"

        # Extract total assets
        assets_text = columns[6].strip() if len(columns) > 6 else ""
        assets_match = re.search(r'Rs ([\d,]+)', assets_text)
        total_assets = assets_match.group(1).replace(',', '') if assets_match else ""

        # Extract liabilities
        liabilities_text = columns[7].strip() if len(columns) > 7 else ""
        liabilities_match = re.search(r'Rs ([\d,]+)', liabilities_text)
        liabilities = liabilities_match.group(1).replace(',', '') if liabilities_match else ""

        return {
            'sno': columns[0].strip(),
            'name': name,
            'constituency': columns[2].strip(),
            'party': columns[3].strip(),
            'criminal_cases': criminal_cases,
            'education': columns[5].strip() if len(columns) > 5 else "",
            'total_assets': total_assets,
            'liabilities': liabilities,
            'candidate_url': candidate_url,
            'election_type': election_type
        }

    except Exception as e:
        print(f"⚠️ Error parsing row: {str(e)[:50]}...")
        return None


def save_to_csv(candidates, filename):
    """Save candidates to CSV file"""
    if not candidates:
        print(f"⚠️ No candidates to save for {filename}")
        return

    # Create directory if needed
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

    fieldnames = ['sno', 'name', 'constituency', 'party', 'criminal_cases',
                  'education', 'total_assets', 'liabilities', 'candidate_url', 'election_type']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for candidate in candidates:
            writer.writerow(candidate)

    print(f"✅ Saved {len(candidates)} candidates to: {filename}")


def print_csv_content(filename, num_rows=10):
    """Print CSV content"""
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    print(f"\n📋 CSV Content: {filename}")
    print("=" * 100)

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Print header
        print(f"{'No':<3} | {'Name':<25} | {'Constituency':<20} | {'Party':<8} | {'Criminal':<8} | {'URL':<30}")
        print("-" * 100)

        # Print rows
        for i, row in enumerate(reader):
            if i >= num_rows:
                with open(filename, 'r', encoding='utf-8') as f:
                    total_lines = sum(1 for _ in f) - 1  # Subtract header
                print(f"... and {total_lines - i} more rows")
                break

            name = row['name'][:25] if row['name'] else 'Unknown'
            constituency = row['constituency'][:20] if row['constituency'] else ''
            party = row['party'][:8] if row['party'] else ''
            criminal = row['criminal_cases'][:8] if row['criminal_cases'] else '0'
            url = row['candidate_url'][:30] if row['candidate_url'] else ''

            print(f"{row['sno']:<3} | {name:<25} | {constituency:<20} | {party:<8} | {criminal:<8} | {url:<30}")

    print("=" * 100)
