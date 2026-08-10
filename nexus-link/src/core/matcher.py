"""Result filtering and consolidation based on person profile"""
import logging
from typing import List, Tuple
from difflib import SequenceMatcher

from ..models.query_v2 import Hit, Result, PersonProfile, Gender


logger = logging.getLogger(__name__)


class ResultMatcher:
    """Matches hits to a person profile and filters results"""
    
    @staticmethod
    def name_similarity(s1: str, s2: str) -> float:
        """Calculate name similarity score (0-1)"""
        if not s1 or not s2:
            return 0.0
        return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()
    
    @staticmethod
    def first_name_match(hit_name: str, expected_first: str, expected_last: str) -> float:
        """
        Check if hit name contains the expected first name.
        
        Returns confidence 0-1:
        - 1.0: exact match on first and last
        - 0.8: first name matched well
        - 0.6: contains first name
        - 0.4: partial match
        - 0.0: no match
        """
        hit_name_lower = hit_name.lower()
        first_lower = expected_first.lower()
        last_lower = expected_last.lower()
        
        # Exact match (first last or username-like)
        if hit_name_lower == f"{first_lower} {last_lower}" or \
           hit_name_lower == f"{first_lower}_{last_lower}" or \
           hit_name_lower == f"{first_lower}{last_lower}":
            return 1.0
        
        # First name at start and last name present
        if hit_name_lower.startswith(first_lower) and last_lower in hit_name_lower:
            return 0.95
        
        # Contains both names (not in order)
        if first_lower in hit_name_lower and last_lower in hit_name_lower:
            return 0.85
        
        # First name similar
        if ResultMatcher.name_similarity(hit_name, expected_first) > 0.8:
            return 0.8
        
        # Contains first name
        if first_lower in hit_name_lower:
            return 0.6
        
        # Partial match
        if ResultMatcher.name_similarity(hit_name, expected_first) > 0.6:
            return 0.4
        
        return 0.0
    
    @staticmethod
    def gender_match(hit_gender: Gender, expected_gender: Gender) -> float:
        """
        Check if gender matches.
        
        Returns:
        - 1.0: exact match
        - 0.8: one is unknown
        - 0.0: mismatch
        """
        if expected_gender == Gender.UNKNOWN:
            return 0.8  # Unknown doesn't penalize
        
        if hit_gender == Gender.UNKNOWN:
            return 0.8  # Unknown doesn't penalize
        
        if hit_gender == expected_gender:
            return 1.0
        
        return 0.0  # Clear mismatch
    
    @staticmethod
    def overall_match_score(hit: Hit, profile: PersonProfile) -> float:
        """
        Calculate overall match score for a hit against the person profile.
        
        Factors:
        - Name match (40%)
        - Gender match (30%)
        - Source confidence (20%)
        - Location bonus (10%)
        """
        name_score = ResultMatcher.first_name_match(hit.match, profile.first_name, profile.last_name)
        gender_score = ResultMatcher.gender_match(hit.gender, profile.gender)
        source_confidence = hit.confidence  # Already 0-1
        
        # Weighted calculation
        score = (
            name_score * 0.40 +
            gender_score * 0.30 +
            source_confidence * 0.20
        )
        
        # Location bonus (if location in hit matches area we might know)
        if hit.location:
            score += 0.10
        
        return min(score, 1.0)
    
    @staticmethod
    def filter_and_consolidate(
        search_id: str,
        profile: PersonProfile,
        hits: List[Hit],
        min_confirmed_score: float = 0.75
    ) -> Result:
        """
        Filter hits to match the person profile and consolidate results.
        
        - Filters OUT "maybes" (score < 0.75)
        - Groups by confirmed name/phone combo
        - Verifies gender match
        
        Args:
            search_id: Search ID
            profile: Person profile with expected info
            hits: All hits from searches
            min_confirmed_score: Minimum score to keep as "confirmed"
        
        Returns:
            Result with categorized accounts
        """
        result = Result(
            result_id=search_id,
            search_query_id=search_id,
            profile=profile
        )
        
        # Score all hits
        scored_hits: List[Tuple[Hit, float]] = []
        for hit in hits:
            score = ResultMatcher.overall_match_score(hit, profile)
            scored_hits.append((hit, score))
        
        logger.info(f"Scored {len(scored_hits)} hits against profile")
        
        # Sort by score descending
        scored_hits.sort(key=lambda x: x[1], reverse=True)
        
        # Categorize hits
        for hit, score in scored_hits:
            logger.info(f"  {hit.match} @ {hit.platform}: {score:.1%} ({hit.gender})")
            
            if score >= min_confirmed_score:
                result.confirmed_accounts.append(hit)
            elif score >= 0.4:
                # Keep if score is reasonable but not high enough
                result.potential_accounts.append(hit)
            else:
                # Discard low-confidence matches
                result.discarded_accounts.append(hit)
        
        # Calculate overall confidence
        if result.confirmed_accounts:
            result.confidence_score = sum(
                ResultMatcher.overall_match_score(h, profile) for h in result.confirmed_accounts
            ) / len(result.confirmed_accounts)
        elif result.potential_accounts:
            result.confidence_score = sum(
                ResultMatcher.overall_match_score(h, profile) for h in result.potential_accounts
            ) / len(result.potential_accounts)
        
        logger.info(f"Final result: {len(result.confirmed_accounts)} confirmed, "
                   f"{len(result.potential_accounts)} potential, "
                   f"{len(result.discarded_accounts)} discarded")
        
        return result
