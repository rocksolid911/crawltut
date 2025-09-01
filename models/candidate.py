"""
Data models for candidate information.
Provides structured data classes for consistent candidate data handling.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Candidate:
    """Represents a political candidate with standardized fields."""
    
    # Basic Information
    name: str
    constituency: str
    party: str
    year: int
    election_type: str  # "mp" or "mla"
    
    # Optional Information
    state: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    
    # Election Results
    is_winner: bool = False
    votes_received: Optional[int] = None
    vote_percentage: Optional[float] = None
    margin: Optional[int] = None
    position: Optional[int] = None
    
    # URLs and References
    profile_url: Optional[str] = None
    image_url: Optional[str] = None
    
    # Financial Information
    assets: Optional[str] = None
    liabilities: Optional[str] = None
    
    # Legal Information
    criminal_cases: Optional[int] = None
    
    # Processing Information
    crawl_timestamp: Optional[datetime] = field(default_factory=datetime.now)
    source_file: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert candidate to dictionary for CSV/JSON export."""
        return {
            'name': self.name,
            'constituency': self.constituency,
            'party': self.party,
            'year': self.year,
            'election_type': self.election_type,
            'state': self.state,
            'age': self.age,
            'gender': self.gender,
            'education': self.education,
            'occupation': self.occupation,
            'is_winner': self.is_winner,
            'votes_received': self.votes_received,
            'vote_percentage': self.vote_percentage,
            'margin': self.margin,
            'position': self.position,
            'profile_url': self.profile_url,
            'image_url': self.image_url,
            'assets': self.assets,
            'liabilities': self.liabilities,
            'criminal_cases': self.criminal_cases,
            'crawl_timestamp': self.crawl_timestamp.isoformat() if self.crawl_timestamp else None,
            'source_file': self.source_file
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Candidate':
        """Create candidate from dictionary data."""
        # Extract required fields
        name = data.get('name') or data.get('candidate_name', '')
        constituency = data.get('constituency') or data.get('constituency_name', '')
        party = data.get('party') or data.get('party_name', '')
        year = int(data.get('year', 0)) if data.get('year') else 0
        election_type = data.get('election_type', 'unknown')
        
        # Create candidate with required fields
        candidate = cls(
            name=name,
            constituency=constituency,
            party=party,
            year=year,
            election_type=election_type
        )
        
        # Set optional fields if available
        candidate.state = data.get('state')
        candidate.age = int(data.get('age')) if data.get('age') and str(data.get('age')).isdigit() else None
        candidate.gender = data.get('gender')
        candidate.education = data.get('education')
        candidate.occupation = data.get('occupation')
        
        # Election results
        candidate.is_winner = str(data.get('is_winner', '')).lower() in ['yes', 'true', '1', 'winner']
        candidate.votes_received = int(data.get('votes_received')) if data.get('votes_received') and str(data.get('votes_received')).isdigit() else None
        candidate.vote_percentage = float(data.get('vote_percentage')) if data.get('vote_percentage') else None
        candidate.margin = int(data.get('margin')) if data.get('margin') and str(data.get('margin')).isdigit() else None
        candidate.position = int(data.get('position')) if data.get('position') and str(data.get('position')).isdigit() else None
        
        # URLs
        candidate.profile_url = data.get('profile_url') or data.get('url') or data.get('link')
        candidate.image_url = data.get('image_url')
        
        # Financial information
        candidate.assets = data.get('assets')
        candidate.liabilities = data.get('liabilities')
        
        # Legal information
        candidate.criminal_cases = int(data.get('criminal_cases')) if data.get('criminal_cases') and str(data.get('criminal_cases')).isdigit() else None
        
        # Processing information
        if data.get('crawl_timestamp'):
            try:
                candidate.crawl_timestamp = datetime.fromisoformat(data['crawl_timestamp'])
            except:
                candidate.crawl_timestamp = datetime.now()
        
        candidate.source_file = data.get('source_file')
        candidate.raw_data = data
        
        return candidate
    
    def get_safe_filename(self) -> str:
        """Get a safe filename for this candidate."""
        from utils.file_manager import FileManager
        return FileManager.create_safe_filename(self.name)
    
    def get_display_name(self) -> str:
        """Get formatted display name for the candidate."""
        return f"{self.name} ({self.party}) - {self.constituency}"
    
    def is_valid(self) -> bool:
        """Check if candidate has minimum required information."""
        return bool(self.name and self.constituency and self.year)


@dataclass 
class CandidateCollection:
    """Collection of candidates with utility methods."""
    
    candidates: List[Candidate] = field(default_factory=list)
    
    def add_candidate(self, candidate: Candidate):
        """Add a candidate to the collection."""
        self.candidates.append(candidate)
    
    def get_winners(self) -> List[Candidate]:
        """Get only winning candidates."""
        return [c for c in self.candidates if c.is_winner]
    
    def get_by_party(self, party: str) -> List[Candidate]:
        """Get candidates by party name."""
        return [c for c in self.candidates if c.party.lower() == party.lower()]
    
    def get_by_constituency(self, constituency: str) -> List[Candidate]:
        """Get candidates by constituency."""
        return [c for c in self.candidates if c.constituency.lower() == constituency.lower()]
    
    def get_by_state(self, state: str) -> List[Candidate]:
        """Get candidates by state."""
        return [c for c in self.candidates if c.state and c.state.lower() == state.lower()]
    
    def get_by_year(self, year: int) -> List[Candidate]:
        """Get candidates by election year."""
        return [c for c in self.candidates if c.year == year]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics."""
        total = len(self.candidates)
        winners = len(self.get_winners())
        
        parties = set(c.party for c in self.candidates if c.party)
        constituencies = set(c.constituency for c in self.candidates if c.constituency)
        states = set(c.state for c in self.candidates if c.state)
        years = set(c.year for c in self.candidates if c.year)
        
        return {
            'total_candidates': total,
            'total_winners': winners,
            'total_parties': len(parties),
            'total_constituencies': len(constituencies),
            'total_states': len(states),
            'years_covered': sorted(list(years)),
            'with_profile_urls': sum(1 for c in self.candidates if c.profile_url),
            'with_images': sum(1 for c in self.candidates if c.image_url),
        }
    
    def to_csv_data(self) -> List[Dict[str, Any]]:
        """Convert collection to CSV-compatible data."""
        return [candidate.to_dict() for candidate in self.candidates]
    
    def filter_valid(self) -> 'CandidateCollection':
        """Return new collection with only valid candidates."""
        valid_candidates = [c for c in self.candidates if c.is_valid()]
        return CandidateCollection(valid_candidates)
    
    def sort_by_name(self) -> 'CandidateCollection':
        """Return new collection sorted by candidate name."""
        sorted_candidates = sorted(self.candidates, key=lambda c: c.name.lower())
        return CandidateCollection(sorted_candidates)
    
    def sort_by_constituency(self) -> 'CandidateCollection':
        """Return new collection sorted by constituency."""
        sorted_candidates = sorted(self.candidates, key=lambda c: c.constituency.lower())
        return CandidateCollection(sorted_candidates)
    
    def __len__(self) -> int:
        """Return number of candidates in collection."""
        return len(self.candidates)
    
    def __iter__(self):
        """Iterate over candidates in collection."""
        return iter(self.candidates)