"""Dating sites search provider"""
import logging
import uuid
from typing import List

from ..core.searcher import BaseSource
from ..models.query_v2 import Hit, Gender


logger = logging.getLogger(__name__)


class DatingSourcesProvider(BaseSource):
    """Search dating and social platforms for registered accounts"""
    
    name = "dating_sources"
    supports_types = ["phone", "email"]
    
    # Popular dating sites to check
    DATING_PLATFORMS = [
        "Tinder",
        "Bumble",
        "Hinge",
        "Match",
        "OkCupid",
        "Plenty of Fish",
        "eHarmony",
        "Seeking",
        "Badoo",
        "Coffee Meets Bagel"
    ]
    
    async def search(self, query: str, query_type: str) -> List[Hit]:
        """
        Search for accounts on dating platforms.
        Returns whatever profile names are found (doesn't filter).
        
        Note: In production, this would query real dating site APIs
        or use account enumeration techniques. For now, returns demo data.
        """
        logger.info(f"DatingSourcesProvider: searching {query_type} on dating sites")
        
        hits = []
        
        # Mock data - would be real API calls in production
        if query_type == "phone":
            # Phone number searches
            hits.extend([
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="John D.",
                    platform="Tinder",
                    url=None,  # Dating apps don't have public profiles
                    confidence=0.88,
                    gender=Gender.MALE,
                    raw_data={
                        "platform_type": "dating_app",
                        "registration_method": "phone",
                        "age_range": "30-40"
                    }
                ),
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="jd_nyc",
                    platform="Bumble",
                    url=None,
                    confidence=0.85,
                    gender=Gender.MALE,
                    raw_data={
                        "platform_type": "dating_app",
                        "registration_method": "phone",
                        "bio": "NYC based, looking for something real"
                    }
                ),
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="Doe_Photography",
                    platform="Hinge",
                    url=None,
                    confidence=0.82,
                    gender=Gender.MALE,
                    raw_data={
                        "platform_type": "dating_app",
                        "registration_method": "phone",
                        "interests": "Photography, Travel"
                    }
                )
            ])
        
        elif query_type == "email":
            # Email searches
            hits.extend([
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="John Doe",
                    platform="Match",
                    url=None,
                    confidence=0.90,
                    gender=Gender.MALE,
                    raw_data={
                        "platform_type": "dating_site",
                        "registration_method": "email",
                        "profile_created": "2023-05-15"
                    }
                ),
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="JDoe35",
                    platform="OkCupid",
                    url=None,
                    confidence=0.87,
                    gender=Gender.MALE,
                    raw_data={
                        "platform_type": "dating_site",
                        "registration_method": "email",
                        "age": "35",
                        "location": "New York, NY"
                    }
                ),
                Hit(
                    hit_id=str(uuid.uuid4()),
                    source=self.name,
                    match="Photography_Lover",
                    platform="Plenty of Fish",
                    url=None,
                    confidence=0.79,
                    gender=Gender.UNKNOWN,
                    raw_data={
                        "platform_type": "dating_site",
                        "registration_method": "email",
                        "last_active": "2 weeks ago"
                    }
                )
            ])
        
        logger.info(f"Found {len(hits)} dating site accounts")
        return hits
