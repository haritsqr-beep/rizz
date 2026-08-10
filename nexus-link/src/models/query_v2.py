"""Core models for NeXuS-LinK"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


@dataclass
class PersonProfile:
    """What the user knows about the person being searched"""
    phone: str
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Gender = Gender.UNKNOWN


@dataclass
class SearchQuery:
    """Represents a user search query with known person profile"""
    query_id: str
    profile: PersonProfile
    created_at: datetime = field(default_factory=datetime.utcnow)
    sources: List[str] = field(default_factory=list)


@dataclass
class Hit:
    """A single search result from a source"""
    hit_id: str
    source: str
    match: str
    platform: str
    url: Optional[str] = None
    confidence: float = 0.5
    gender: Gender = Gender.UNKNOWN
    location: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    found_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Result:
    """Final consolidated result for the person"""
    result_id: str
    search_query_id: str
    profile: PersonProfile
    confirmed_accounts: List[Hit] = field(default_factory=list)
    potential_accounts: List[Hit] = field(default_factory=list)
    discarded_accounts: List[Hit] = field(default_factory=list)
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def total_accounts(self) -> int:
        """Total number of accounts found"""
        return len(self.confirmed_accounts) + len(self.potential_accounts)
