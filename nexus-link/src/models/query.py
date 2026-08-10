"""Core models for NeXuS-LinK"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ConfidenceLevel(str, Enum):
    YES = "yes"
    MAYBE = "maybe"
    NO = "no"
    UNKNOWN = "unknown"


class ResultCategory(str, Enum):
    CONFIRMED = "confirmed"
    POTENTIAL = "potential"
    DISCARDED = "discarded"


@dataclass
class SearchQuery:
    """Represents a user search query"""
    query_id: str
    query: str
    query_type: str  # phone, email, username, name, etc.
    created_at: datetime = field(default_factory=datetime.utcnow)
    auto_confirm: bool = False
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
    raw_data: Dict[str, Any] = field(default_factory=dict)
    found_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Confirmation:
    """User confirmation answers for a hit"""
    hit_id: str
    name_match: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    age_match: Optional[ConfidenceLevel] = None
    location_match: Optional[ConfidenceLevel] = None
    timezone_match: Optional[ConfidenceLevel] = None
    notes: str = ""
    confirmed_at: datetime = field(default_factory=datetime.utcnow)
    
    def confidence_score(self) -> float:
        """Calculate overall confidence score (0-100)"""
        scores = []
        if self.name_match == ConfidenceLevel.YES:
            scores.append(100)
        elif self.name_match == ConfidenceLevel.MAYBE:
            scores.append(60)
        elif self.name_match == ConfidenceLevel.NO:
            scores.append(0)
        
        for field_match in [self.age_match, self.location_match, self.timezone_match]:
            if field_match == ConfidenceLevel.YES:
                scores.append(100)
            elif field_match == ConfidenceLevel.MAYBE:
                scores.append(60)
            elif field_match == ConfidenceLevel.NO:
                scores.append(0)
        
        return sum(scores) / len(scores) if scores else 50


@dataclass
class Result:
    """Final categorized result with all data"""
    result_id: str
    search_query_id: str
    hits: List[Hit] = field(default_factory=list)
    confirmations: Dict[str, Confirmation] = field(default_factory=dict)
    category: ResultCategory = ResultCategory.POTENTIAL
    overall_confidence: float = 0.0
    cross_refs: List[str] = field(default_factory=list)  # URLs/usernames found across platforms
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_category(self, threshold_confirmed: float = 75.0, threshold_potential: float = 40.0):
        """Auto-categorize based on confidence scores"""
        if not self.confirmations:
            return
        
        avg_confidence = sum(c.confidence_score() for c in self.confirmations.values()) / len(self.confirmations)
        self.overall_confidence = avg_confidence
        
        if avg_confidence >= threshold_confirmed:
            self.category = ResultCategory.CONFIRMED
        elif avg_confidence >= threshold_potential:
            self.category = ResultCategory.POTENTIAL
        else:
            self.category = ResultCategory.DISCARDED
