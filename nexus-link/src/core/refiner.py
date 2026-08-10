"""Refinement questions and confirmation flow"""
from typing import List, Dict, Any, Optional
from ..models.query import Hit, Confirmation, ConfidenceLevel


class RefinementEngine:
    """Generates and processes refinement questions for hits"""
    
    DEFAULT_QUESTIONS = {
        "name_match": {
            "question": "Does the name match what you're looking for?",
            "options": ["yes", "maybe", "no"],
            "field": "name_match"
        },
        "age_match": {
            "question": "If you know their age, does it match?",
            "options": ["yes", "maybe", "no", "unknown"],
            "field": "age_match"
        },
        "location_match": {
            "question": "Does the location/region match?",
            "options": ["yes", "maybe", "no", "unknown"],
            "field": "location_match"
        },
        "timezone_match": {
            "question": "Is the timezone reasonable for them?",
            "options": ["yes", "maybe", "no", "unknown"],
            "field": "timezone_match"
        }
    }
    
    @staticmethod
    def get_refinement_questions(hit: Hit) -> List[Dict[str, Any]]:
        """
        Get refinement questions for a hit.
        Questions are tailored based on what data is available.
        """
        questions = []
        
        # Always ask about name
        questions.append({
            "id": "name_match",
            "question": RefinementEngine.DEFAULT_QUESTIONS["name_match"]["question"],
            "options": RefinementEngine.DEFAULT_QUESTIONS["name_match"]["options"],
            "context": f"Match: {hit.match}",
            "platform": hit.platform
        })
        
        # Ask about age if we have location data
        if "location" in hit.raw_data:
            questions.append({
                "id": "age_match",
                "question": RefinementEngine.DEFAULT_QUESTIONS["age_match"]["question"],
                "options": RefinementEngine.DEFAULT_QUESTIONS["age_match"]["options"],
                "context": f"Location: {hit.raw_data.get('location', 'Unknown')}",
                "platform": hit.platform
            })
        
        # Ask about location if available
        if "location" in hit.raw_data or "region" in hit.raw_data:
            questions.append({
                "id": "location_match",
                "question": RefinementEngine.DEFAULT_QUESTIONS["location_match"]["question"],
                "options": RefinementEngine.DEFAULT_QUESTIONS["location_match"]["options"],
                "context": f"Region: {hit.raw_data.get('region', hit.raw_data.get('location', 'Unknown'))}",
                "platform": hit.platform
            })
        
        # Ask about timezone if we have time zone info
        if "timezone" in hit.raw_data:
            questions.append({
                "id": "timezone_match",
                "question": RefinementEngine.DEFAULT_QUESTIONS["timezone_match"]["question"],
                "options": RefinementEngine.DEFAULT_QUESTIONS["timezone_match"]["options"],
                "context": f"Timezone: {hit.raw_data.get('timezone')}",
                "platform": hit.platform
            })
        
        return questions
    
    @staticmethod
    def process_confirmation(hit: Hit, answers: Dict[str, str], notes: str = "") -> Confirmation:
        """
        Process user answers and create a Confirmation object.
        
        Args:
            hit: The Hit being confirmed
            answers: Dict mapping question_id to answer (yes/maybe/no/unknown)
            notes: Optional user notes
        
        Returns:
            Confirmation object with scored confidence
        """
        confirmation = Confirmation(
            hit_id=hit.hit_id,
            name_match=ConfidenceLevel(answers.get("name_match", "unknown")),
            age_match=ConfidenceLevel(answers.get("age_match", "unknown")) if "age_match" in answers else None,
            location_match=ConfidenceLevel(answers.get("location_match", "unknown")) if "location_match" in answers else None,
            timezone_match=ConfidenceLevel(answers.get("timezone_match", "unknown")) if "timezone_match" in answers else None,
            notes=notes
        )
        
        return confirmation
