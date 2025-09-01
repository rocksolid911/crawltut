"""
MLA (State Assembly) specific crawler implementation.
Handles Member of Legislative Assembly election data crawling with specialized logic.
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


class MLACrawler(BaseCrawler):
    """Specialized crawler for MLA (State Assembly) election data."""
    
    def __init__(self, state: str, year: int, batch_size: int = 50):
        """Initialize MLA crawler for specific state and election year."""
        super().__init__(batch_size=batch_size)
        self.state = state
        self.year = year
        self.base_output_dir = f"mla_data_{state}_{year}"
        
    async def crawl_state_assembly_page(self, state_url: str) -> Optional[str]:
        """
        Crawl state assembly main page to get election year links.
        
        Args:
            state_url: URL for state assembly page
            
        Returns:
            Content of the state assembly page
        """
        run_config = WebCrawlerConfig.get_constituency_config(f"mla_state_{self.state}")
        
        print(f"Crawling state assembly page for {self.state}")
        
        results = await self.crawl_urls_batch([state_url], run_config)
        
        if results and results[0]:
            return results[0].markdown
        
        return None
    
    async def crawl_winners_from_state(self, winners_url: str) -> Dict[str, Any]:
        """
        Crawl winners data from state assembly winners page.
        
        Args:
            winners_url: URL for winners page
            
        Returns:
            Dictionary with crawling statistics
        """
        run_config = WebCrawlerConfig.get_candidate_config(f"mla_winners_{self.state}_{self.year}")
        stats = {'winners_found': 0, 'constituencies': 0, 'errors': 0}
        
        def process_winners_result(result, url):
            try:
                if result and hasattr(result, 'markdown'):
                    winners_data = self._parse_winners_from_markdown(result.markdown)
                    
                    if winners_data:
                        self._save_winners_data(winners_data, result.markdown)
                        stats['winners_found'] = len(winners_data)
                        stats['constituencies'] = len(set(w.get('constituency', '') for w in winners_data))
                    
            except Exception as e:
                print(f"Error processing winners from {url}: {str(e)}")
                stats['errors'] += 1
        
        await self.crawl_urls_batch([winners_url], run_config, process_winners_result)
        
        return stats
    
    async def crawl_all_candidates_from_constituencies(self, constituency_urls: List[str]) -> Dict[str, Any]:
        """
        Crawl all candidates (not just winners) from constituency pages.
        
        Args:
            constituency_urls: List of constituency URLs
            
        Returns:
            Dictionary with crawling statistics
        """
        run_config = WebCrawlerConfig.get_candidate_config(f"mla_all_candidates_{self.state}_{self.year}")
        stats = {'constituencies': 0, 'candidates': 0, 'errors': 0}
        
        def process_constituency_result(result, url):
            try:
                if result and hasattr(result, 'markdown'):
                    constituency_name = self._extract_constituency_name_from_url(url)
                    candidates = self._parse_all_candidates_from_markdown(result.markdown)
                    
                    if candidates:
                        self._save_constituency_candidates(constituency_name, candidates, result.markdown)
                        stats['candidates'] += len(candidates)
                        stats['constituencies'] += 1
                    
            except Exception as e:
                print(f"Error processing constituency {url}: {str(e)}")
                stats['errors'] += 1
        
        await self.crawl_urls_batch(constituency_urls, run_config, process_constituency_result)
        
        return stats
    
    async def download_mla_candidate_images(self, csv_path: str, winners_only: bool = True) -> Dict[str, int]:
        """
        Download candidate images for MLA candidates.
        
        Args:
            csv_path: Path to CSV file containing candidate data
            winners_only: Whether to process only winners
            
        Returns:
            Dictionary with download statistics
        """
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
                    'state': self.state,
                    'year': self.year,
                    'candidate_data': candidate
                })
        
        return await self._download_mla_profile_images(candidate_image_data)
    
    async def extract_candidate_urls_from_csv_files(self, csv_directory: str) -> Dict[str, str]:
        """
        Extract candidate URLs from all CSV files in a directory.
        
        Args:
            csv_directory: Directory containing CSV files
            
        Returns:
            Dictionary mapping candidate names to URLs
        """
        csv_files = CSVProcessor.find_csv_files(csv_directory)
        all_candidate_urls = {}
        
        for csv_file in csv_files:
            candidate_urls = CSVProcessor.extract_candidate_urls(csv_file)
            all_candidate_urls.update(candidate_urls)
        
        print(f"Found {len(all_candidate_urls)} candidate URLs from {len(csv_files)} CSV files")
        return all_candidate_urls
    
    def get_state_assembly_url(self, base_url: str = "https://www.myneta.info") -> str:
        """Get the state assembly URL for this state."""
        state_encoded = self.state.replace(' ', '%20')
        return f"{base_url}/state_assembly.php?state={state_encoded}"
    
    def get_winners_url_for_year(self, base_url: str = "https://www.myneta.info") -> str:
        """Get the winners URL for this state and year."""
        # This would need to be customized based on actual myneta.info URL patterns
        state_code = self._get_state_code(self.state)
        return f"{base_url}/{state_code}{str(self.year)[-2:]}/index.php?action=show_winners&sort=default"
    
    def _parse_winners_from_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse winners data from markdown content."""
        winners = []
        
        # This would need actual parsing logic based on myneta.info structure
        # Placeholder implementation
        
        return winners
    
    def _parse_all_candidates_from_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse all candidates data from markdown content."""
        candidates = []
        
        # This would need actual parsing logic based on myneta.info structure
        # Placeholder implementation
        
        return candidates
    
    def _save_winners_data(self, winners_data: List[Dict[str, Any]], raw_content: str):
        """Save winners data to files."""
        FileManager.ensure_directory(self.base_output_dir)
        
        # Save winners as CSV
        csv_path = os.path.join(self.base_output_dir, f"{self.state}_{self.year}_winners.csv")
        CSVProcessor.write_csv_data(csv_path, winners_data)
        
        # Save raw content
        raw_path = os.path.join(self.base_output_dir, f"{self.state}_{self.year}_winners_raw.md")
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
    
    def _save_constituency_candidates(self, constituency_name: str, candidates: List[Dict[str, Any]], 
                                    raw_content: str):
        """Save constituency candidates data to files."""
        constituency_dir = os.path.join(self.base_output_dir, 
                                      FileManager.create_safe_filename(constituency_name))
        FileManager.ensure_directory(constituency_dir)
        
        # Save candidates as CSV
        csv_path = os.path.join(constituency_dir, 
                               f"{FileManager.create_safe_filename(constituency_name)}_candidates.csv")
        CSVProcessor.write_csv_data(csv_path, candidates)
        
        # Save raw content
        raw_path = os.path.join(constituency_dir, 
                               f"{FileManager.create_safe_filename(constituency_name)}_raw.md")
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(raw_content)
    
    def _extract_constituency_name_from_url(self, url: str) -> str:
        """Extract constituency name from URL."""
        parts = url.split('/')
        if parts:
            filename = parts[-1].replace('.php', '').replace('_', ' ').title()
            return filename
        return "unknown_constituency"
    
    def _extract_candidate_profile_url(self, candidate: Dict[str, Any]) -> Optional[str]:
        """Extract profile URL from candidate data."""
        url_fields = ['url', 'link', 'profile_url', 'candidate_link']
        
        for field in url_fields:
            if field in candidate and candidate[field]:
                url = candidate[field].strip()
                if url.startswith(('http://', 'https://')):
                    return url
        
        return None
    
    def _get_state_code(self, state_name: str) -> str:
        """Get state code for URL construction."""
        # Common state codes mapping - would need to be comprehensive
        state_codes = {
            'Andhra Pradesh': 'ap',
            'Assam': 'assam',
            'Bihar': 'bihar',
            'Gujarat': 'gujarat',
            'Karnataka': 'karnataka',
            'Kerala': 'kerala',
            'Madhya Pradesh': 'mp',
            'Maharashtra': 'maharashtra',
            'Odisha': 'odisha',
            'Punjab': 'punjab',
            'Rajasthan': 'rajasthan',
            'Tamil Nadu': 'tn',
            'Telangana': 'telangana',
            'Uttar Pradesh': 'up',
            'West Bengal': 'wb'
        }
        
        return state_codes.get(state_name.title(), state_name.lower().replace(' ', ''))
    
    async def _download_mla_profile_images(self, candidate_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Download profile images for MLA candidates."""
        stats = {'processed': 0, 'images_found': 0, 'images_downloaded': 0, 'errors': 0}
        
        # Extract profile URLs
        profile_urls = [(c['name'], c['profile_url']) for c in candidate_data if c.get('profile_url')]
        
        if not profile_urls:
            return stats
        
        run_config = WebCrawlerConfig.get_candidate_config(f"mla_images_{self.state}_{self.year}")
        
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