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


# def main():
#     """Main function to process your markdown content"""
#
#     # Your markdown content goes here
#     markdown_content = """List of Winners:Andhra Pradesh 2009 Election
# **Myneta.info is an open data repository platform of Association for Democratic Reforms (ADR).**
# [![Myneta Logo](https://www.myneta.info/lib/img/myneta-logo.png)](https://www.myneta.info/) | [![Myneta Logo](https://www.myneta.info/lib/img/adr-logo.png)](https://adrindia.org)
# ---|---
# [Home](https://www.myneta.info/) [Lok Sabha](https://www.myneta.info/#ls "Lok Sabha") [ State Assemblies ](https://www.myneta.info/#sa "State Assemblies") [Rajya Sabha](https://www.myneta.info/#rs "Rajya Sabha") [Political Parties ](https://www.myneta.info/party "Political Parties") [ Electoral Bonds ](https://www.myneta.info/electoral_bonds "Electoral Bonds") [ || माय नेता हिंदी में || ](https://translate.google.co.in/translate?prev=hp&hl=en&js=y&u=www.myneta.info&sl=en&tl=hi&history_state0=) [ About MyNeta ](https://adrindia.org/content/about-myneta) [ About ADR ](https://adrindia.org/about-adr/who-we-are) [☰](javascript:void\(0\))
# [ State Assemblies ](https://www.myneta.info/#sa "State Assemblies") [ Rajya Sabha ](https://www.myneta.info/#rs "Rajya Sabha") [ Political Parties ](https://www.myneta.info/party "Political Parties")
# |
# ---|---
# ![](https://www.myneta.info/lib/img/banner/banner-1.png)![](https://www.myneta.info/lib/img/banner/banner-2.png)![](https://www.myneta.info/lib/img/banner/banner-3.png)![](https://www.myneta.info/lib/img/banner/banner-4.png)
# 1  2  3  4
# [Home](https://www.myneta.info/) → [Andhra Pradesh 2009](https://www.myneta.info/ap09/) → **List of Winners**
# ###
# ## Andhra Pradesh 2009
# ###  Election Summary
# HIGHLIGHTS OF CANDIDATES
# ---
# Total number of constituencies analyzed |  293
# Total candidates analyzed by NEW | **[3100](https://www.myneta.info/ap09/index.php?action=summary&subAction=candidates_analyzed&sort=candidate#summary) **
# Candidates with declared criminal cases | **[381(12%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=crime&sort=candidate#summary) **
# Candidates with declared serious criminal cases| **[244(8%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=serious_crime&sort=candidate#summary) **
# Crorepati candidates | **[484(16%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=crorepati&sort=candidate#summary) **
# Candidates who are graduate or above | **[1275 (41%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=education&sort=candidate#summary) **
# Candidates who have not declared PAN | **[2038 (66%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=without_pan&sort=candidate#summary) **
# Total women candidates | **[242 (8%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=women_candidate&sort=candidate#summary) **
# HIGHLIGHTS OF WINNERS
# ---
# Total winners analyzed by NEW | **[259](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_analyzed&sort=candidate#summary) **
# Winners with declared criminal cases | **[71 (27%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_crime&sort=candidate#summary) **
# Winners with declared serious criminal cases | **[41 (16%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_serious_crime&sort=candidate#summary)**
# Crorepati winners | **[138 (53%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_crorepati&sort=candidate#summary) **
# Winners who are graduate or above | **[157 (61%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_education&sort=candidate#summary) **
# Winners who have not declared PAN | **[65 (25%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_without_pan&sort=candidate#summary) **
# Total women winners | **[29 (11%)](https://www.myneta.info/ap09/index.php?action=summary&subAction=winner_women&sort=candidate#summary) **
# ### List of Winners in Andhra Pradesh 2009
# Sort By
# [Candidate ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=candidate) [ Constituency ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=default) [Party](https://www.myneta.info/ap09/index.php?action=show_winners&sort=party) [Criminal Cases](https://www.myneta.info/ap09/index.php?action=show_winners&sort=criminal) [Education](https://www.myneta.info/ap09/index.php?action=show_winners&sort=edu) [Total Assets ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=asset) [Liabilities](https://www.myneta.info/ap09/index.php?action=show_winners&sort=liabi)
# Sno | Candidate | Constituency ∇ | Party  | Criminal Case  | Education  | Total Assets | Liabilities
# ---|---|---|---|---|---|---|---
# 1 | [](https://www.myneta.info/candidate.php?candidate_id=2964)[Kanna Lakshmi Narayana](https://www.myneta.info/ap09/candidate.php?candidate_id=2964)|  GUNTUR WEST | INC | 0 | Graduate | Rs 2,80,45,883 ~ 2 Crore+ | Rs 36,77,143 ~ 36 Lacs+
# 2 | [](https://www.myneta.info/candidate.php?candidate_id=2655)[Kurasala Kannababu](https://www.myneta.info/ap09/candidate.php?candidate_id=2655)|  KAKINADA RURAL | PRAP | 0 | Post Graduate | Rs 5,53,590 ~ 5 Lacs+ | Rs 0 ~
# 3 | [](https://www.myneta.info/candidate.php?candidate_id=2807)[Routu Surya Prakasa Rao](https://www.myneta.info/ap09/candidate.php?candidate_id=2807)|  RAJAHMUNDRY CITY | INC | **3** | Graduate Professional | ![](https://myneta.info/image_v2.php?myneta_folder=ap09&candidate_id=2807&col=ta) | ![](https://myneta.info/image_v2.php?myneta_folder=ap09&candidate_id=2807&col=lia)
# 4 | [](https://www.myneta.info/candidate.php?candidate_id=654)[Baswaraju Saraiah](https://www.myneta.info/ap09/candidate.php?candidate_id=654)|  WARANGAL EAST | INC | 0 | 10th Pass | Rs 64,36,500 ~ 64 Lacs+ | Rs 3,50,000 ~ 3 Lacs+
# 5 | [](https://www.myneta.info/candidate.php?candidate_id=639)[D Vinaya Bhasker](https://www.myneta.info/ap09/candidate.php?candidate_id=639)|  WARANGAL WEST | TRS | **2** | Graduate | Rs 38,71,867 ~ 38 Lacs+ | Rs 0 ~
# ### List of Winners in Andhra Pradesh 2009 Bye-Elections
# Sort By
# [Candidate ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=candidate) [ Constituency ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=default) [Party](https://www.myneta.info/ap09/index.php?action=show_winners&sort=party) [Criminal Cases](https://www.myneta.info/ap09/index.php?action=show_winners&sort=criminal) [Education](https://www.myneta.info/ap09/index.php?action=show_winners&sort=edu) [Total Assets ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=asset) [Liabilities](https://www.myneta.info/ap09/index.php?action=show_winners&sort=liabi)
# Sno | Candidate | Constituency ∇ | Party  | Criminal Case  | Education  | Total Assets | Liabilities
# ---|---|---|---|---|---|---|---
# 1 | [](https://www.myneta.info/candidate.php?candidate_id=2984)[Shaik Mastan Vali](https://www.myneta.info/ap09/candidate.php?candidate_id=2984)|  GUNTUR EAST | INC | 0 | Post Graduate | Rs 10,00,000 ~ 10 Lacs+ | Rs 0 ~
# 2 | [](https://www.myneta.info/candidate.php?candidate_id=3256)[Dasyam Vinay Bhaskar](https://www.myneta.info/ap09/candidate.php?candidate_id=3256)|  Warangal West: Bye Election on 2010 | TRS |  2  | Graduate | Rs 36,83,269 ~ 36 Lacs+ | Rs 8,25,000 ~ 8 Lacs+
# """
#
#     print("🎯 ANDHRA PRADESH 2009 CANDIDATE DATA EXTRACTOR")
#     print("=" * 60)
#
#     # Extract candidates
#     main_candidates, bye_candidates = extract_candidates_from_markdown(markdown_content)
#
#     # Initialize file variables
#     main_file = None
#     bye_file = None
#
#     # Save to CSV files
#     if main_candidates:
#         main_file = "andhra_pradesh_2009_winners.csv"
#         save_to_csv(main_candidates, main_file)
#         print_csv_content(main_file, 10)
#
#     if bye_candidates:
#         bye_file = "andhra_pradesh_2009_bye_elections.csv"
#         save_to_csv(bye_candidates, bye_file)
#         print_csv_content(bye_file, 5)
#
#     # Summary
#     total_candidates = len(main_candidates) + len(bye_candidates)
#     print(f"\n🎯 EXTRACTION SUMMARY:")
#     print(f"   • Main election winners: {len(main_candidates)}")
#     print(f"   • Bye-election winners: {len(bye_candidates)}")
#     print(f"   • Total candidates extracted: {total_candidates}")
#
#     created_files = []
#     if main_file:
#         created_files.append(main_file)
#     if bye_file:
#         created_files.append(bye_file)
#
#     print(f"   • Files created: {', '.join(created_files) if created_files else 'None'}")
#
#
# # Function to process your full markdown content
# def process_your_markdown(your_full_markdown_content, output_dir=".", base_filename="election_data"):
#     """
#     Use this function to process your complete markdown content.
#
#     Usage:
#         process_your_markdown(your_markdown_string, "output_folder", "filename_base")
#
#     Returns:
#         tuple: (main_candidates, bye_candidates)
#     """
#     try:
#         main_candidates, bye_candidates = extract_candidates_from_markdown(your_full_markdown_content)
#
#         # Create output directory
#         os.makedirs(output_dir, exist_ok=True)
#
#         # Initialize file tracking
#         created_files = []
#
#         # Process main election candidates
#         if main_candidates:
#             main_file = os.path.join(output_dir, f"{base_filename}_winners.csv")
#             save_to_csv(main_candidates, main_file)
#             print_csv_content(main_file, 10)
#             created_files.append(main_file)
#
#         # Process bye-election candidates
#         if bye_candidates:
#             bye_file = os.path.join(output_dir, f"{base_filename}_bye_elections.csv")
#             save_to_csv(bye_candidates, bye_file)
#             print_csv_content(bye_file, 10)
#             created_files.append(bye_file)
#
#         # Summary - no more undefined variable errors
#         total_candidates = len(main_candidates) + len(bye_candidates)
#         print(f"\n🎯 PROCESSING SUMMARY:")
#         print(f"   • Main election winners: {len(main_candidates)}")
#         print(f"   • Bye-election winners: {len(bye_candidates)}")
#         print(f"   • Total candidates extracted: {total_candidates}")
#         print(f"   • Files created: {', '.join(created_files) if created_files else 'None'}")
#
#         return main_candidates, bye_candidates
#
#     except Exception as e:
#         print(f"❌ Error processing markdown: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return [], []
#
#
# # Enhanced function for file processing with better error handling
# def process_markdown_file_safe(markdown_content, state_name="Unknown", year="Unknown", output_dir="."):
#     """
#     Safe function to process markdown files without variable scope errors.
#     """
#     try:
#         print(f"🔄 Processing {state_name} {year} election data...")
#
#         main_candidates, bye_candidates = extract_candidates_from_markdown(markdown_content)
#
#         # Create filenames
#         base_name = f"{state_name.replace(' ', '_')}_{year}"
#         main_filename = f"{base_name}_winners.csv"
#         bye_filename = f"{base_name}_bye_elections.csv"
#
#         # Create output directory
#         os.makedirs(output_dir, exist_ok=True)
#
#         # Track created files
#         files_created = []
#
#         # Save main election data
#         if main_candidates:
#             main_path = os.path.join(output_dir, main_filename)
#             save_to_csv(main_candidates, main_path)
#             files_created.append(main_path)
#             print(f"✅ Saved {len(main_candidates)} main candidates")
#
#         # Save bye-election data
#         if bye_candidates:
#             bye_path = os.path.join(output_dir, bye_filename)
#             save_to_csv(bye_candidates, bye_path)
#             files_created.append(bye_path)
#             print(f"✅ Saved {len(bye_candidates)} bye-election candidates")
#
#         # Summary
#         total = len(main_candidates) + len(bye_candidates)
#         print(f"📊 Total: {total} candidates in {len(files_created)} files")
#
#         return {
#             'success': True,
#             'main_candidates': len(main_candidates),
#             'bye_candidates': len(bye_candidates),
#             'files_created': files_created,
#             'total_candidates': total
#         }
#
#     except Exception as e:
#         print(f"❌ Error processing {state_name} {year}: {str(e)}")
#         return {
#             'success': False,
#             'error': str(e),
#             'main_candidates': 0,
#             'bye_candidates': 0,
#             'files_created': [],
#             'total_candidates': 0
#         }
#
#
# # Test function to debug bye-election extraction
# def debug_bye_election_extraction(markdown_content):
#     """
#     Debug function to see exactly what's happening with bye-election extraction.
#     """
#     print("🔍 DEBUGGING BYE-ELECTION EXTRACTION")
#     print("=" * 50)
#
#     # Check if bye-election text exists
#     bye_keywords = ["bye-election", "by-election", "bye election", "by election"]
#     for keyword in bye_keywords:
#         if keyword in markdown_content.lower():
#             print(f"✅ Found keyword: '{keyword}'")
#             # Find and show context around this keyword
#             start = markdown_content.lower().find(keyword)
#             context = markdown_content[max(0, start - 100):start + 200]
#             print(f"   Context: ...{context}...")
#             break
#     else:
#         print("❌ No bye-election keywords found")
#
#     # Try to find the bye-election section manually
#     lines = markdown_content.split('\n')
#     bye_section_start = -1
#
#     for i, line in enumerate(lines):
#         if 'bye' in line.lower() and 'list of winners' in line.lower():
#             print(f"✅ Found bye-election header at line {i}: {line.strip()}")
#             bye_section_start = i
#             break
#
#     if bye_section_start >= 0:
#         # Show the next 20 lines after the header
#         print(f"\n📋 Next 20 lines after bye-election header:")
#         for i in range(bye_section_start, min(bye_section_start + 20, len(lines))):
#             print(f"{i:3d}: {lines[i]}")
#
#         # Look for table structure
#         table_found = False
#         for i in range(bye_section_start, min(bye_section_start + 15, len(lines))):
#             if 'sno | candidate' in lines[i].lower():
#                 print(f"✅ Found table header at line {i}")
#                 table_found = True
#                 break
#
#         if not table_found:
#             print("⚠️ No table header found in bye-election section")
#
#     print("=" * 50)


# if __name__ == "__main__":
#     # Test with your specific content that has bye-elections
#     test_content = """### List of Winners in Andhra Pradesh 2009 Bye-Elections
# Sort By
# [Candidate ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=candidate) [ Constituency ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=default) [Party](https://www.myneta.info/ap09/index.php?action=show_winners&sort=party) [Criminal Cases](https://www.myneta.info/ap09/index.php?action=show_winners&sort=criminal) [Education](https://www.myneta.info/ap09/index.php?action=show_winners&sort=edu) [Total Assets ](https://www.myneta.info/ap09/index.php?action=show_winners&sort=asset) [Liabilities](https://www.myneta.info/ap09/index.php?action=show_winners&sort=liabi)
# Sno | Candidate | Constituency ∇ | Party  | Criminal Case  | Education  | Total Assets | Liabilities
# ---|---|---|---|---|---|---|---
# 1 | [](https://www.myneta.info/candidate.php?candidate_id=2984)[Shaik Mastan Vali](https://www.myneta.info/ap09/candidate.php?candidate_id=2984)|  GUNTUR EAST | INC | 0 | Post Graduate | Rs 10,00,000 ~ 10 Lacs+ | Rs 0 ~
# 2 | [](https://www.myneta.info/candidate.php?candidate_id=3256)[Dasyam Vinay Bhaskar](https://www.myneta.info/ap09/candidate.php?candidate_id=3256)|  Warangal West: Bye Election on 2010 | TRS |  2  | Graduate | Rs 36,83,269 ~ 36 Lacs+ | Rs 8,25,000 ~ 8 Lacs+"""
#
#     print("🧪 Testing with bye-election content...")
#     debug_bye_election_extraction(test_content)
#
#     print("\n" + "=" * 60)
#     print("🚀 Running extraction...")
#     main_candidates, bye_candidates = extract_candidates_from_markdown(test_content)
#
#     print(f"\n📊 Results:")
#     print(f"   • Main candidates: {len(main_candidates)}")
#     print(f"   • Bye candidates: {len(bye_candidates)}")
#
#     if bye_candidates:
#         print(f"\n📋 Bye-election candidates found:")
#         for candidate in bye_candidates:
#             print(f"   • {candidate['name']} ({candidate['constituency']})")
#
#     main()