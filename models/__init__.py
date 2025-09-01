"""
Data models package for structured data handling.

This package provides data models for:
- Candidate information with validation
- Collection utilities for groups of candidates
- Standardized data structures across the application
"""

from .candidate import Candidate, CandidateCollection

__all__ = ['Candidate', 'CandidateCollection']