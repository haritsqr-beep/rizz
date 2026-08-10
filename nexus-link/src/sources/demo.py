"""Example search sources for NeXuS-LinK"""
import logging
import uuid
from datetime import datetime
from typing import List

from ..core.searcher import BaseSource
from ..models.query import Hit


logger = logging.getLogger(__name__)


class DemoPhoneSource(BaseSource):
    """Demo phone lookup source (returns mock data)"""
    
    name = "demo_phone"
    supports_types = ["phone"]
    
    async def search(self, query: str, query_type: str) -> List[Hit]:
        """Simulate phone lookup"""
        logger.info(f"DemoPhoneSource: searching for {query}")
        
        # Mock data
        hits = [
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="John Doe",
                platform="TruePeopleSearch",
                url="https://www.truepeople search.com/results",
                confidence=0.92,
                raw_data={
                    "location": "New York, NY",
                    "region": "New York",
                    "age": "32-38",
                    "timezone": "EST"
                }
            ),
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="J. Doe",
                platform="WhitePages",
                url="https://www.whitepages.com/results",
                confidence=0.87,
                raw_data={
                    "location": "Brooklyn, NY",
                    "region": "New York",
                    "timezone": "EST"
                }
            )
        ]
        
        return hits


class DemoSocialSource(BaseSource):
    """Demo social media search source"""
    
    name = "demo_social"
    supports_types = ["username", "email", "phone"]
    
    async def search(self, query: str, query_type: str) -> List[Hit]:
        """Simulate social media search"""
        logger.info(f"DemoSocialSource: searching for {query}")
        
        hits = [
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="johndoe_ny",
                platform="Instagram",
                url="https://instagram.com/johndoe_ny",
                confidence=0.78,
                raw_data={
                    "bio": "NYC based | Photographer",
                    "followers": 1250
                }
            ),
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="john_doe_32",
                platform="Twitter",
                url="https://twitter.com/john_doe_32",
                confidence=0.71,
                raw_data={
                    "bio": "Software engineer, NYC",
                    "followers": 340
                }
            )
        ]
        
        return hits


class DemoEmailSource(BaseSource):
    """Demo email reverse lookup source"""
    
    name = "demo_email"
    supports_types = ["email"]
    
    async def search(self, query: str, query_type: str) -> List[Hit]:
        """Simulate email reverse lookup"""
        logger.info(f"DemoEmailSource: searching for {query}")
        
        hits = [
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="John Doe",
                platform="LinkedIn",
                url="https://linkedin.com/in/johndoe",
                confidence=0.89,
                raw_data={
                    "location": "New York, USA",
                    "title": "Senior Engineer",
                    "company": "TechCorp"
                }
            ),
            Hit(
                hit_id=str(uuid.uuid4()),
                source=self.name,
                match="john.doe@techcorp.com",
                platform="Google Dorking",
                url=None,
                confidence=0.76,
                raw_data={
                    "domain": "techcorp.com",
                    "context": "Found in leaked data list (public source)"
                }
            )
        ]
        
        return hits
