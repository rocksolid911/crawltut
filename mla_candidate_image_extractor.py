import asyncio
import os
import re
import aiohttp
import csv
from pathlib import Path
from urllib.parse import urljoin
from crawl4ai import BrowserConfig, CrawlerRunConfig, CacheMode, AsyncWebCrawler
from datetime import datetime


async def download_profile_image(image_url, output_path):
    """Download profile image from URL and save to the specified path."""
    if not image_url.startswith(('http://', 'https://')):
        print(f"⚠️ Invalid image URL: {image_url}")
        return False

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Write image content to file
                    with open(output_path, 'wb') as f:
                        f.write(await response.read())

                    print(f"✅ Image saved to {output_path}")
                    return True
                else:
                    print(f"❌ Failed to download image: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error downloading image: {str(e)}")
        return False


async def extract_and_download_profile_images(base_path="state_assembly", output_base="candidate_data"):
    """
    Extract profile images from candidate profiles and download them

    Args:
        base_path: Base directory containing candidate CSV files
        output_base: Base directory for output
    """
    print("🔍 Finding candidate CSV files...")

    # Initialize CSV file for tracking missing images
    missing_images_csv = "missing_profile_images.csv"
    csv_headers = ['timestamp', 'state', 'year', 'constituency', 'candidate_name', 'url', 'reason']

    # Create or append to CSV file
    csv_exists = os.path.exists(missing_images_csv)
    csv_file = open(missing_images_csv, 'a', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    if not csv_exists:
        csv_writer.writerow(csv_headers)
        print(f"📝 Created missing images tracking file: {missing_images_csv}")
    else:
        print(f"📝 Appending to existing tracking file: {missing_images_csv}")

    try:
        # Find all CSV files
        csv_files = []
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith("_winners.csv"):
                    csv_files.append(os.path.join(root, file))

        print(f"📊 Found {len(csv_files)} winner CSV files")

        if not csv_files:
            print("❌ No candidate CSV files found!")
            return

        # Configure browser settings for crawling
        browser_config = BrowserConfig(
            headless=True,
            browser_type="chromium",
        )

        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id="profile_image_crawler",
        )

        # Process each CSV file to get candidate URLs
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for csv_file_path in csv_files:
                # Extract state and year from file path
                path_parts = csv_file_path.split(os.sep)
                if len(path_parts) >= 3:
                    state = path_parts[-3]
                    year = path_parts[-2]
                    print(f"\n📄 Processing {state} {year} winners from {csv_file_path}")

                    # Use pandas to read CSV and find candidate URLs
                    import pandas as pd
                    try:
                        # Try different encodings
                        encodings = ['utf-8', 'latin-1', 'cp1252']
                        df = None

                        for encoding in encodings:
                            try:
                                df = pd.read_csv(csv_file_path, encoding=encoding)
                                break
                            except UnicodeDecodeError:
                                continue

                        if df is None or df.empty:
                            print(f"❌ Could not read CSV file: {csv_file_path}")
                            continue

                        # Try to find URL column
                        url_column = None
                        for col in df.columns:
                            if 'url' in col.lower() or 'link' in col.lower() or 'profile' in col.lower():
                                url_column = col
                                break

                        # If not found, look for a column with URLs
                        if url_column is None:
                            for col in df.columns:
                                sample = df[col].iloc[0] if not df.empty else ""
                                if isinstance(sample, str) and (
                                        sample.startswith('http://') or sample.startswith('https://')):
                                    url_column = col
                                    break

                        # If we found a URL column, process the candidates
                        if url_column:
                            print(f"✅ Found URL column: {url_column}")

                            # Process each candidate
                            for i, row in df.iterrows():
                                url = row[url_column]
                                if pd.notna(url) and isinstance(url, str) and url.strip():
                                    url = url.strip()

                                    # Get candidate name for file naming
                                    name_column = None
                                    for col in ['name', 'candidate', 'candidate_name']:
                                        if col in df.columns:
                                            name_column = col
                                            break

                                    name = row[name_column] if name_column else f"candidate_{i + 1}"
                                    name = str(name).strip()
                                    safe_name = "".join([c if c.isalnum() else "_" for c in name]).rstrip("_")
                                    if not safe_name:
                                        safe_name = f"candidate_{i + 1}"

                                    # Get constituency name
                                    constituency_column = None
                                    for col in ['constituency', 'ac_name', 'ac no & name', 'constituency_name']:
                                        if col in df.columns:
                                            constituency_column = col
                                            break

                                    constituency = row[constituency_column] if constituency_column else "Unknown"
                                    constituency = str(constituency).strip()

                                    # Check for by-election
                                    is_by_election = False
                                    if isinstance(constituency, str):
                                        is_by_election = bool(re.search(r'\b(by[-\s]election|by[-\s]poll)\b',
                                                                        constituency, re.IGNORECASE))

                                    # Determine output directory
                                    if is_by_election:
                                        candidate_dir = os.path.join(output_base, str(year), state, "by_elections",
                                                                     safe_name)
                                    else:
                                        candidate_dir = os.path.join(output_base, str(year), state, safe_name)

                                    # Create directory if it doesn't exist
                                    os.makedirs(candidate_dir, exist_ok=True)

                                    # Path for profile image
                                    image_path = os.path.join(candidate_dir, f"{safe_name}.jpg")

                                    # Skip if image already exists
                                    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                                        print(f"✅ Skipping {name}: Image already exists")
                                        continue

                                    print(f"🔍 Processing URL: {url} for candidate: {name}")

                                    # Crawl the candidate profile page
                                    try:
                                        result = await crawler.arun(url, config=run_config)
                                        markup = result.html

                                        # Enhanced debugging: Log the URL being processed
                                        print(f"🔍 Analyzing content from URL: {url}")

                                        # ENHANCED: Multiple comprehensive patterns for different page layouts
                                        image_url = None
                                        found_pattern = None

                                        # Pattern 1: Look for profile images with alt="profile image"
                                        profile_img_pattern1 = re.compile(
                                            r'<img[^>]*src="([^"]*(?:myneta\.info/)?images_candidate/[^"]*\.(?:jpg|png|jpeg))"[^>]*alt="profile image"',
                                            re.IGNORECASE
                                        )

                                        # Pattern 2: Any image in images_candidate directory (absolute URL)
                                        profile_img_pattern2 = re.compile(
                                            r'<img[^>]*src="(https?://[^"]*myneta\.info/images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
                                            re.IGNORECASE
                                        )

                                        # Pattern 3: Relative paths to images_candidate
                                        profile_img_pattern3 = re.compile(
                                            r'<img[^>]*src="(/images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
                                            re.IGNORECASE
                                        )

                                        # Pattern 4: Any images_candidate reference
                                        profile_img_pattern4 = re.compile(
                                            r'<img[^>]*src="([^"]*images_candidate/[^"]*\.(?:jpg|png|jpeg))"',
                                            re.IGNORECASE
                                        )

                                        # Pattern 5: Look for the specific structure found in your HTML
                                        profile_img_pattern5 = re.compile(
                                            r'<img[^>]+src="([^"]+\.(?:jpg|png|jpeg))"[^>]*(?:alt="profile[^"]*"|class="[^"]*profile[^"]*")',
                                            re.IGNORECASE
                                        )

                                        patterns = [
                                            (profile_img_pattern1, "Profile image with alt text"),
                                            (profile_img_pattern2, "Absolute URL to images_candidate"),
                                            (profile_img_pattern3, "Relative path to images_candidate"),
                                            (profile_img_pattern4, "Any images_candidate reference"),
                                            (profile_img_pattern5, "Profile-related image"),
                                        ]

                                        # Try all patterns in order of preference
                                        for pattern, description in patterns:
                                            match = pattern.search(markup)
                                            if match:
                                                image_url = match.group(1)
                                                found_pattern = description
                                                print(f"✅ Found image using pattern: {description}")
                                                break

                                        # Additional debugging: Look for any images at all
                                        if not image_url:
                                            all_images = re.findall(r'<img[^>]*src="([^"]+\.(?:jpg|png|jpeg))"', markup,
                                                                    re.IGNORECASE)
                                            print(f"🔍 Found {len(all_images)} total images in the page")

                                            # Look specifically for images_candidate in the content
                                            candidate_images = [img for img in all_images if
                                                                'images_candidate' in img.lower()]
                                            if candidate_images:
                                                print(f"🎯 Found {len(candidate_images)} candidate images")
                                                image_url = candidate_images[0]  # Use the first one found
                                                found_pattern = "Fallback candidate image detection"

                                        if image_url:
                                            # Make sure it's an absolute URL
                                            original_url = image_url
                                            if not image_url.startswith(('http://', 'https://')):
                                                if image_url.startswith('/'):
                                                    image_url = 'https://myneta.info' + image_url
                                                else:
                                                    image_url = 'https://myneta.info/' + image_url

                                            print(f"✅ Found image URL: {image_url} (pattern: {found_pattern})")

                                            # Download the image
                                            success = await download_profile_image(image_url, image_path)
                                            if success:
                                                print(f"🎉 Successfully downloaded profile image for {name}")
                                            else:
                                                print(f"❌ Failed to download image for {name}")
                                                # Log failed download to CSV
                                                csv_writer.writerow([
                                                    datetime.now().isoformat(),
                                                    state,
                                                    year,
                                                    constituency,
                                                    name,
                                                    url,
                                                    f"Image found but download failed: {image_url}"
                                                ])
                                        else:
                                            print(f"❌ No profile image found for {name}")

                                            # Determine the reason for missing image
                                            reason = "No profile image found"
                                            if 'candidate.php' not in url.lower():
                                                reason = "URL does not appear to be a candidate profile page"
                                            elif len(all_images) == 0:
                                                reason = "No images found on page"
                                            elif 'images_candidate' not in markup.lower():
                                                reason = "No candidate image directory references found"

                                            # Log missing image to CSV
                                            csv_writer.writerow([
                                                datetime.now().isoformat(),
                                                state,
                                                year,
                                                constituency,
                                                name,
                                                url,
                                                reason
                                            ])
                                            print(f"📝 Logged missing image: {name} ({reason})")

                                    except Exception as e:
                                        print(f"❌ Error processing {name}: {str(e)}")
                                        # Log error to CSV
                                        csv_writer.writerow([
                                            datetime.now().isoformat(),
                                            state,
                                            year,
                                            constituency,
                                            name,
                                            url,
                                            f"Processing error: {str(e)}"
                                        ])

                        else:
                            print(f"❌ No URL column found in CSV file: {csv_file_path}")

                    except Exception as e:
                        print(f"❌ Error processing CSV file {csv_file_path}: {str(e)}")

    finally:
        csv_file.close()
        print(f"📝 Missing images tracking saved to: {missing_images_csv}")


