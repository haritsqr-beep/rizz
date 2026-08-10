"""Search engine core - multi-source OSINT search"""
import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

from ..models.query import SearchQuery, Hit


logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """Base class for all search sources"""
    
    name: str = "base"
    supports_types: List[str] = []
    
    @abstractmethod
    async def search(self, query: str, query_type: str) -> List[Hit]:
        """Execute search. Return list of hits."""
        pass


class SearchEngine:
    """Orchestrates searches across multiple sources"""
    
    def __init__(self):
        self.sources: Dict[str, BaseSource] = {}
        self.search_history: List[SearchQuery] = []
    
    def register_source(self, source: BaseSource):
        """Register a search source"""
        self.sources[source.name] = source
        logger.info(f"Registered source: {source.name}")
    
    async def search(self, query: SearchQuery) -> List[Hit]:
        """
        Execute search across configured sources in parallel.
        Returns all hits from all sources.
        """
        if not query.sources:
            # Use all sources that support this query type
            query.sources = [
                name for name, source in self.sources.items()
                if query.query_type in source.supports_types
            ]
        
        logger.info(f"Search {query.query_id}: '{query.query}' ({query.query_type})")
        logger.info(f"Using sources: {query.sources}")
        
        # Run all sources in parallel
        tasks = [
            self.sources[source_name].search(query.query, query.query_type)
            for source_name in query.sources
            if source_name in self.sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and filter results
        all_hits: List[Hit] = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Source error: {result}")
                continue
            if result:
                all_hits.extend(result)
        
        logger.info(f"Found {len(all_hits)} total hits")
        self.search_history.append(query)
        return all_hits
