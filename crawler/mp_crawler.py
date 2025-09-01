"""
MP (Lok Sabha) specific crawler implementation.
Handles Member of Parliament election data crawling with specialized logic.
"""
import asyncio
import json
import os
from typing import List, Dict, Any, Optional

from .base_crawler import BaseCrawler
from .core import WebCrawlerConfig
from utils.csv_processor import CSVProcessor
from utils.file_manager import FileManager
from utils.image_processor import ImageProcessor


class MPCrawler(BaseCrawler):
    """Specialized crawler for MP (Lok Sabha) election data."""
    
    def __init__(self, year: int, batch_size: int = 50):
        """Initialize MP crawler for specific election year."""
        super().__init__(batch_size=batch_size)
        self.year = year
        self.base_output_dir = f"mp_data_{year}"
        
    async def crawl_constituency_links(self, base_url: str = "https://www.myneta.info") -> List[str]:
        """
        Crawl and extract constituency links for MP elections.
        
        Args:
            base_url: Base URL for myneta.info
            
        Returns:
            List of constituency URLs
        """
        constituency_url = f"{base_url}/LokSabha{self.year}/"
        run_config = WebCrawlerConfig.get_constituency_config(f"mp_constituency_{self.year}")
        
        print(f"Crawling MP constituency links for year {self.year}")
        
        # Use base crawler to get constituency page
        results = await self.crawl_urls_batch([constituency_url], run_config)
        
        if results and results[0]:
            # Extract constituency links from the result
            return self._extract_constituency_links_from_content(results[0].markdown)
        
        return []
    
    async def crawl_candidates_from_constituencies(self, constituency_urls: List[str], 
                                                 winners_only: bool = False) -> Dict[str, Any]:
        """
        Crawl candidate data from constituency URLs.
        
        Args:
            constituency_urls: List of constituency URLs
            winners_only: Whether to crawl only winners
            
        Returns:
            Dictionary with crawling statistics
        """
        run_config = WebCrawlerConfig.get_candidate_config(f"mp_candidates_{self.year}")
        stats = {'constituencies': 0, 'candidates': 0, 'errors': 0}
        
        def process_constituency_result(result, url):
            try:
                if result and hasattr(result, 'markdown'):
                    constituency_name = self._extract_constituency_name_from_url(url)
                    candidates = self._parse_candidates_from_markdown(result.markdown, winners_only)
                    
                    if candidates:
                        self._save_constituency_data(constituency_name, candidates, result.markdown)
                        stats['candidates'] += len(candidates)
                        stats['constituencies'] += 1
                    
            except Exception as e:
                print(f"Error processing constituency {url}: {str(e)}")
                stats['errors'] += 1
        
        # Crawl all constituencies
        await self.crawl_urls_batch(constituency_urls, run_config, process_constituency_result)
        
        return stats
    
    async def download_candidate_images_from_csv(self, csv_path: str, 
                                               winners_only: bool = False) -> Dict[str, int]:
        """
        Download candidate images from CSV data.
        
        Args:
            csv_path: Path to CSV file containing candidate data
            winners_only: Whether to process only winners
            
        Returns:
            Dictionary with download statistics
        """
        # Read candidate data from CSV
        candidates = CSVProcessor.read_candidate_data(csv_path, winners_only)
        
        # Prepare candidate data for image processing
        candidate_image_data = []
        for candidate in candidates:
            name = candidate.get('name') or candidate.get('candidate_name', 'unknown')
            profile_url = self._extract_candidate_profile_url(candidate)
            
            if profile_url:
                candidate_image_data.append({
                    'name': name,
                    'profile_url': profile_url,
                    'candidate_data': candidate
                })
        
        # Download profile images for each candidate
        return await self._download_candidate_profile_images(candidate_image_data)
    
    async def generate_candidate_profiles(self, candidate_urls: Dict[str, str], 
                                        force_regenerate: bool = False, 
                                        skip_if_force_regenerated: bool = True) -> Dict[str, int]:
        """
        Generate detailed candidate profiles by crawling individual pages.
        
        Args:
            candidate_urls: Dictionary mapping candidate names to their profile URLs
            force_regenerate: If True, regenerate files even if they exist
            skip_if_force_regenerated: If True, skip candidates already processed
            
        Returns:
            Statistics dictionary
        """
        run_config = WebCrawlerConfig.get_candidate_config(f"mp_profiles_{self.year}")
        stats = {'profiles_generated': 0, 'images_downloaded': 0, 'errors': 0, 'skipped': 0}
        
        # Convert dict to list of tuples for batch processing
        candidate_pairs = [(name, url) for name, url in candidate_urls.items()]
        
        def process_candidate_result(result, url, candidate_name):
            try:
                if result and hasattr(result, 'markdown'):
                    # Create candidate directory
                    candidate_dir = FileManager.create_candidate_directory(
                        self.base_output_dir, candidate_name
                    )
                    
                    safe_name = FileManager.create_safe_filename(candidate_name)
                    json_path = os.path.join(candidate_dir, f"{safe_name}.json")
                    image_path = ImageProcessor.create_candidate_image_path(candidate_dir, candidate_name)
                    
                    # Check if files already exist
                    json_exists = FileManager.file_exists_and_not_empty(json_path)
                    image_exists = FileManager.file_exists_and_not_empty(image_path)
                    
                    # Check if this was previously regenerated
                    was_force_regenerated = False
                    if json_exists:
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                                was_force_regenerated = existing_data.get('force_regenerated', False)
                        except:
                            pass  # If can't read, treat as not regenerated
                    
                    # Skip logic based on your original implementation
                    if json_exists and image_exists and not force_regenerate:
                        print(f"⏭️  Skipping {candidate_name}: Files already exist")
                        stats['skipped'] += 1
                        return
                    
                    if was_force_regenerated and skip_if_force_regenerated:
                        print(f"⏭️  Skipping {candidate_name}: Already regenerated (use --include-regenerated to process)")
                        stats['skipped'] += 1
                        return
                    
                    # Determine what needs to be processed
                    need_json = not json_exists or force_regenerate
                    need_image = not image_exists or force_regenerate
                    
                    print(f"🔄 Processing {candidate_name} (JSON: {need_json}, Image: {need_image})")
                    
                    # Save profile data as JSON
                    if need_json:
                        profile_data = {
                            'name': candidate_name,
                            'url': url,
                            'year': self.year,
                            'crawl_timestamp': str(asyncio.get_event_loop().time()),
                            'markdown_content': result.markdown,
                            'force_regenerated': force_regenerate
                        }
                        
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(profile_data, f, indent=2, ensure_ascii=False)
                        
                        stats['profiles_generated'] += 1
                    
                    # Extract and download profile image
                    if need_image:
                        image_url = ImageProcessor.extract_profile_image_from_markdown(result.markdown, url)
                        if image_url:
                            # Download image synchronously (in the callback)
                            if ImageProcessor.download_image_sync(image_url, image_path):
                                stats['images_downloaded'] += 1
                        
            except Exception as e:
                print(f"❌ Error processing candidate {candidate_name}: {str(e)}")
                stats['errors'] += 1
        
        # Crawl all candidate profiles
        await self.crawl_url_pairs_batch(candidate_pairs, run_config, process_candidate_result)
        
        return stats
    
    def _extract_constituency_links_from_content(self, content: str) -> List[str]:
        """Extract constituency links from HTML/markdown content."""
        import re
        
        # Pattern to match constituency links
        pattern = rf'https://www\.myneta\.info/LokSabha{self.year}/.*\.php'
        links = re.findall(pattern, content)
        
        # Remove duplicates and filter valid links
        unique_links = list(set(links))
        return [link for link in unique_links if 'constituency' in link or 'winner' in link]
    
    def _extract_constituency_name_from_url(self, url: str) -> str:
        """Extract constituency name from URL."""
        # Simple extraction - could be improved based on actual URL patterns
        parts = url.split('/')
        if parts:
            filename = parts[-1].replace('.php', '').replace('_', ' ').title()
            return filename
        return "unknown_constituency"
    
    def _parse_candidates_from_markdown(self, content: str, winners_only: bool = False) -> List[Dict[str, Any]]:
        """Parse candidate data from markdown content."""
        # This would need to be implemented based on the actual structure
        # of the myneta.info pages for MP candidates
        candidates = []
        
        # Placeholder implementation - would need actual parsing logic
        # based on the HTML/markdown structure of the pages
        
        return candidates
    
    def _save_constituency_data(self, constituency_name: str, candidates: List[Dict[str, Any]], 
                               raw_content: str):
        """Save constituency data to files."""
        # Create constituency directory
        constituency_dir = os.path.join(self.base_output_dir, FileManager.create_safe_filename(constituency_name))
        FileManager.ensure_directory(constituency_dir)
        
        # Save candidates as CSV
        csv_path = os.path.join(constituency_dir, f"{FileManager.create_safe_filename(constituency_name)}_candidates.csv")
        CSVProcessor.write_csv_data(csv_path, candidates)
        
        # Save raw content
        raw_path = os.path.join(constituency_dir, f"{FileManager.create_safe_filename(constituency_name)}_raw.md")
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
    
    def _extract_candidate_profile_url(self, candidate: Dict[str, Any]) -> Optional[str]:
        """Extract profile URL from candidate data."""
        # Try common URL field names
        url_fields = ['url', 'link', 'profile_url', 'candidate_link']
        
        for field in url_fields:
            if field in candidate and candidate[field]:
                url = candidate[field].strip()
                if url.startswith(('http://', 'https://')):
                    return url
        
        return None
    
    async def _download_candidate_profile_images(self, candidate_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Download profile images for candidates by crawling their profile pages."""
        stats = {'processed': 0, 'images_found': 0, 'images_downloaded': 0, 'errors': 0}
        
        # Extract profile URLs
        profile_urls = [(c['name'], c['profile_url']) for c in candidate_data if c.get('profile_url')]
        
        if not profile_urls:
            return stats
        
        run_config = WebCrawlerConfig.get_candidate_config(f"mp_images_{self.year}")
        
        def process_image_result(result, url, candidate_name):
            try:
                stats['processed'] += 1
                
                if result and hasattr(result, 'markdown'):
                    # Extract image URL from profile page
                    image_url = ImageProcessor.extract_profile_image_from_markdown(result.markdown, url)
                    
                    if image_url:
                        stats['images_found'] += 1
                        
                        # Create candidate directory
                        candidate_dir = FileManager.create_candidate_directory(
                            self.base_output_dir, candidate_name
                        )
                        
                        # Download image
                        image_path = ImageProcessor.create_candidate_image_path(candidate_dir, candidate_name)
                        
                        if ImageProcessor.download_image_sync(image_url, image_path):
                            stats['images_downloaded'] += 1
                            
            except Exception as e:
                print(f"Error downloading image for {candidate_name}: {str(e)}")
                stats['errors'] += 1
        
        # Crawl profile pages to get images
        await self.crawl_url_pairs_batch(profile_urls, run_config, process_image_result)
        
        return stats