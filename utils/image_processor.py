"""
Image processing utilities.
Centralizes image downloading and processing to eliminate duplication.
"""
import asyncio
import re
import io
import os
from typing import Optional, List, Tuple
import aiohttp
import requests
from PIL import Image
from urllib.parse import urljoin, urlparse

from .file_manager import FileManager


class ImageProcessor:
    """Utility class for image operations."""
    
    @staticmethod
    async def download_image_async(image_url: str, output_path: str, 
                                  timeout: int = 10, max_size: Tuple[int, int] = None) -> bool:
        """
        Download image asynchronously with error handling.
        
        Args:
            image_url: URL of the image to download
            output_path: Local path to save the image
            timeout: Request timeout in seconds
            max_size: Optional tuple (width, height) to resize image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=timeout) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Process and save image
                        return ImageProcessor._save_image_data(
                            image_data, output_path, max_size
                        )
                    else:
                        print(f"Failed to download image: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Error downloading image from {image_url}: {str(e)}")
            return False
    
    @staticmethod
    def download_image_sync(image_url: str, output_path: str, 
                           timeout: int = 10, max_size: Tuple[int, int] = None) -> bool:
        """
        Download image synchronously with error handling.
        
        Args:
            image_url: URL of the image to download
            output_path: Local path to save the image
            timeout: Request timeout in seconds
            max_size: Optional tuple (width, height) to resize image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=timeout)
            response.raise_for_status()
            
            # Process and save image
            return ImageProcessor._save_image_data(
                response.content, output_path, max_size
            )
            
        except Exception as e:
            print(f"Error downloading image from {image_url}: {str(e)}")
            return False
    
    @staticmethod
    def extract_image_urls_from_markdown(markdown_content: str, 
                                       base_url: str = None) -> List[str]:
        """
        Extract image URLs from markdown content.
        
        Args:
            markdown_content: Markdown text content
            base_url: Base URL to resolve relative URLs
            
        Returns:
            List of image URLs found in the markdown
        """
        if not markdown_content:
            return []
        
        image_urls = []
        
        # Pattern for markdown images: ![alt](url)
        markdown_pattern = r'!\[.*?\]\((.*?)\)'
        markdown_matches = re.findall(markdown_pattern, markdown_content)
        
        # Pattern for HTML img tags: <img src="url">
        html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        html_matches = re.findall(html_pattern, markdown_content, re.IGNORECASE)
        
        # Combine all matches
        all_urls = markdown_matches + html_matches
        
        for url in all_urls:
            # Clean and validate URL
            url = url.strip()
            if url:
                # Convert relative URLs to absolute if base_url provided
                if base_url and not url.startswith(('http://', 'https://')):
                    url = urljoin(base_url, url)
                
                # Validate URL
                if ImageProcessor.is_valid_image_url(url):
                    image_urls.append(url)
        
        return list(set(image_urls))  # Remove duplicates
    
    @staticmethod
    def extract_profile_image_from_markdown(markdown_content: str, 
                                          base_url: str = None) -> Optional[str]:
        """
        Extract the main profile image URL from markdown content.
        
        Args:
            markdown_content: Markdown text content
            base_url: Base URL to resolve relative URLs
            
        Returns:
            First valid image URL found, or None
        """
        image_urls = ImageProcessor.extract_image_urls_from_markdown(
            markdown_content, base_url
        )
        
        # Return first image URL (usually the profile image)
        return image_urls[0] if image_urls else None
    
    @staticmethod
    def is_valid_image_url(url: str) -> bool:
        """
        Check if URL is a valid image URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if valid image URL
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check if it's a proper HTTP/HTTPS URL
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # Check for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        url_lower = url.lower()
        
        # Check URL path for image extension
        parsed_url = urlparse(url_lower)
        path = parsed_url.path
        
        return any(path.endswith(ext) for ext in image_extensions)
    
    @staticmethod
    def resize_image(image_path: str, max_size: Tuple[int, int], 
                    output_path: str = None) -> bool:
        """
        Resize an image to maximum dimensions.
        
        Args:
            image_path: Path to input image
            max_size: Tuple (max_width, max_height)
            output_path: Optional output path (overwrites input if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate new size maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save resized image
                save_path = output_path or image_path
                img.save(save_path, format='JPEG', quality=85)
                
                return True
                
        except Exception as e:
            print(f"Error resizing image {image_path}: {str(e)}")
            return False
    
    @staticmethod
    def create_candidate_image_path(candidate_dir: str, candidate_name: str, 
                                   extension: str = ".jpg") -> str:
        """
        Create standardized image path for candidate.
        
        Args:
            candidate_dir: Candidate directory path
            candidate_name: Candidate name
            extension: Image file extension
            
        Returns:
            Full image file path
        """
        safe_name = FileManager.create_safe_filename(candidate_name)
        return os.path.join(candidate_dir, f"{safe_name}{extension}")
    
    @staticmethod
    async def download_candidate_images_batch(candidate_data: List[dict], 
                                            base_output_dir: str,
                                            concurrent_downloads: int = 10) -> dict:
        """
        Download images for multiple candidates concurrently.
        
        Args:
            candidate_data: List of candidate dictionaries with image URLs
            base_output_dir: Base directory for saving images
            concurrent_downloads: Number of concurrent downloads
            
        Returns:
            Dictionary with download statistics
        """
        semaphore = asyncio.Semaphore(concurrent_downloads)
        tasks = []
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        async def download_single_candidate(candidate):
            async with semaphore:
                candidate_name = candidate.get('name', 'unknown')
                image_url = candidate.get('image_url')
                
                if not image_url:
                    stats['skipped'] += 1
                    return
                
                # Create candidate directory
                candidate_dir = FileManager.create_candidate_directory(
                    base_output_dir, candidate_name
                )
                
                # Create image path
                image_path = ImageProcessor.create_candidate_image_path(
                    candidate_dir, candidate_name
                )
                
                # Skip if image already exists
                if FileManager.file_exists_and_not_empty(image_path):
                    stats['skipped'] += 1
                    return
                
                # Download image
                success = await ImageProcessor.download_image_async(
                    image_url, image_path, max_size=(800, 800)
                )
                
                if success:
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
        
        # Create tasks for all candidates
        for candidate in candidate_data:
            tasks.append(download_single_candidate(candidate))
        
        # Execute all downloads
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return stats
    
    # Private helper methods
    @staticmethod
    def _save_image_data(image_data: bytes, output_path: str, 
                        max_size: Tuple[int, int] = None) -> bool:
        """Save image data to file with optional resizing."""
        try:
            # Ensure output directory exists
            FileManager.ensure_directory(os.path.dirname(output_path))
            
            # Open and process image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if max_size specified
            if max_size:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save image
            image.save(output_path, format='JPEG', quality=85)
            return True
            
        except Exception as e:
            print(f"Error saving image to {output_path}: {str(e)}")
            return False