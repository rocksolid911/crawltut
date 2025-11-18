"""
Data models for candidates.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Candidate:
    """Model representing a political candidate."""

    name: str
    constituency: str
    party: str
    url: str

    # Optional fields
    sno: Optional[int] = None
    criminal_cases: Optional[int] = None
    education: Optional[str] = None
    total_assets: Optional[str] = None
    liabilities: Optional[str] = None
    election_type: Optional[str] = None  # main_election, bye_election
    is_winner: Optional[bool] = None
    state: Optional[str] = None
    year: Optional[int] = None
    image_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert candidate to dictionary."""
        return {
            'sno': self.sno,
            'name': self.name,
            'constituency': self.constituency,
            'party': self.party,
            'criminal_cases': self.criminal_cases,
            'education': self.education,
            'total_assets': self.total_assets,
            'liabilities': self.liabilities,
            'url': self.url,
            'election_type': self.election_type,
            'is_winner': self.is_winner,
            'state': self.state,
            'year': self.year,
            'image_url': self.image_url,
        }

    def get_safe_name(self) -> str:
        """Get a filesystem-safe version of the candidate name."""
        return "".join([c if c.isalnum() else "_" for c in self.name]).rstrip("_")


@dataclass
class Constituency:
    """Model representing a constituency."""

    name: str
    url: str
    constituency_id: str
    state: Optional[str] = None
    year: Optional[int] = None

    def get_safe_name(self) -> str:
        """Get a filesystem-safe version of the constituency name."""
        clean_name = self.name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        return clean_name
