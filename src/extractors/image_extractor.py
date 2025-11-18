"""
Image extraction and download utilities.
"""
import io
import os
import re
from typing import Optional

import aiohttp
import requests
from PIL import Image


def extract_image_url_from_markdown(markdown_content: str) -> Optional[str]:
    """
    Extract image URL from markdown content.

    Args:
        markdown_content: Markdown content

    Returns:
        Image URL or None
    """
    # Pattern to match markdown images: ![alt](url)
    match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', markdown_content)
    if match:
        return match.group(1)
    return None


def extract_profile_image_from_html(html_content: str) -> Optional[str]:
    """
    Extract profile image URL from HTML content using multiple patterns.

    Args:
        html_content: HTML content

    Returns:
        Image URL or None
    """
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

    patterns = [
        (profile_img_pattern1, "Profile image with alt text"),
        (profile_img_pattern2, "Absolute URL to images_candidate"),
        (profile_img_pattern3, "Relative path to images_candidate"),
        (profile_img_pattern4, "Any images_candidate reference"),
    ]

    # Try all patterns in order of preference
    for pattern, description in patterns:
        match = pattern.search(html_content)
        if match:
            image_url = match.group(1)
            # Make sure it's an absolute URL
            if not image_url.startswith(('http://', 'https://')):
                if image_url.startswith('/'):
                    image_url = 'https://myneta.info' + image_url
                else:
                    image_url = 'https://myneta.info/' + image_url
            return image_url

    # Fallback: Look for any images_candidate references
    all_images = re.findall(r'<img[^>]*src="([^"]+\.(?:jpg|png|jpeg))"', html_content, re.IGNORECASE)
    candidate_images = [img for img in all_images if 'images_candidate' in img.lower()]
    if candidate_images:
        image_url = candidate_images[0]
        if not image_url.startswith(('http://', 'https://')):
            if image_url.startswith('/'):
                image_url = 'https://myneta.info' + image_url
            else:
                image_url = 'https://myneta.info/' + image_url
        return image_url

    return None


async def download_image_async(image_url: str, output_path: str) -> bool:
    """
    Download an image asynchronously.

    Args:
        image_url: URL of the image
        output_path: Path to save the image

    Returns:
        True if successful, False otherwise
    """
    if not image_url.startswith(('http://', 'https://')):
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

                    print(f"Image saved: {os.path.basename(output_path)}")
                    return True
                else:
                    print(f"Failed to download image: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False


def download_image_sync(image_url: str, output_path: str) -> bool:
    """
    Download an image synchronously.

    Args:
        image_url: URL of the image
        output_path: Path to save the image

    Returns:
        True if successful, False otherwise
    """
    if not image_url.startswith(('http://', 'https://')):
        return False

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        # Convert and save as JPEG
        image = Image.open(io.BytesIO(response.content)).convert('RGB')

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        image.save(output_path, format='JPEG')
        print(f"Image saved: {os.path.basename(output_path)}")
        return True

    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False


async def download_image_from_markdown(markdown_content: str, output_path: str,
                                      candidate_name: str) -> bool:
    """
    Extract image URL from markdown and download it.

    Args:
        markdown_content: Markdown content containing image
        output_path: Path to save the image
        candidate_name: Name of the candidate (for logging)

    Returns:
        True if successful, False otherwise
    """
    image_url = extract_image_url_from_markdown(markdown_content)

    if not image_url:
        print(f"No image found in markdown for {candidate_name}")
        return False

    try:
        return download_image_sync(image_url, output_path)
    except Exception as e:
        print(f"Failed to download image for {candidate_name}: {e}")
        return False
