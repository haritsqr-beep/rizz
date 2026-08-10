"""Result aggregation and cross-referencing"""
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import logging

from ..models.query import Hit, Result, ResultCategory


logger = logging.getLogger(__name__)


class Aggregator:
    """Aggregates hits from multiple sources and finds cross-references"""
    
    @staticmethod
    def find_cross_references(hits: List[Hit]) -> Dict[str, List[str]]:
        """
        Find cross-references between hits.
        
        Returns dict mapping source identifiers to other sources where they appear.
        """
        cross_refs: Dict[str, List[str]] = defaultdict(set)
        
        # Simple name-based matching (can be enhanced)
        matches_by_name: Dict[str, List[Hit]] = defaultdict(list)
        
        for hit in hits:
            normalized_name = hit.match.lower().strip()
            matches_by_name[normalized_name].append(hit)
        
        # Find hits with same name across different platforms
        for name, name_hits in matches_by_name.items():
            if len(name_hits) > 1:
                platforms = [h.platform for h in name_hits]
                urls = [h.url for h in name_hits if h.url]
                
                for hit in name_hits:
                    cross_refs[hit.hit_id] = urls
        
        return {k: list(v) for k, v in cross_refs.items()}
    
    @staticmethod
    def build_connection_graph(hits: List[Hit]) -> Dict[str, Dict[str, any]]:
        """
        Build a graph showing connections between hits.
        
        Returns:
            Dict with nodes and edges for visualization
        """
        nodes = []
        edges = []
        hit_map = {}
        
        # Create nodes
        for hit in hits:
            node_id = hit.hit_id
            hit_map[node_id] = hit
            nodes.append({
                "id": node_id,
                "label": hit.match,
                "platform": hit.platform,
                "source": hit.source,
                "url": hit.url,
                "confidence": hit.confidence
            })
        
        # Create edges based on cross-references
        cross_refs = Aggregator.find_cross_references(hits)
        seen_edges = set()
        
        for hit_id, ref_urls in cross_refs.items():
            for other_hit in hits:
                if other_hit.hit_id != hit_id and other_hit.url in ref_urls:
                    edge_key = tuple(sorted([hit_id, other_hit.hit_id]))
                    if edge_key not in seen_edges:
                        edges.append({
                            "from": hit_id,
                            "to": other_hit.hit_id,
                            "type": "cross_ref"
                        })
                        seen_edges.add(edge_key)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_hits": len(hits),
                "unique_platforms": len(set(h.platform for h in hits)),
                "cross_references": len(cross_refs)
            }
        }
    
    @staticmethod
    def merge_duplicate_hits(hits: List[Hit], name_threshold: float = 0.85) -> List[Hit]:
        """
        Merge hits that appear to be duplicates or very similar matches.
        
        Args:
            hits: List of hits to merge
            name_threshold: String similarity threshold (0-1)
        
        Returns:
            Deduplicated list of hits
        """
        merged = []
        seen = set()
        
        # Simple deduplication by exact match and platform
        for hit in sorted(hits, key=lambda h: h.confidence, reverse=True):
            key = (hit.match.lower(), hit.platform)
            if key not in seen:
                merged.append(hit)
                seen.add(key)
        
        logger.info(f"Merged {len(hits)} hits down to {len(merged)}")
        return merged
    
    @staticmethod
    def group_by_category(hits: List[Hit], results: List[Result]) -> Dict[str, List[Result]]:
        """
        Group results by their category (confirmed/potential/discarded).
        
        Returns:
            Dict mapping category names to lists of results
        """
        grouped = {
            "confirmed": [],
            "potential": [],
            "discarded": []
        }
        
        for result in results:
            category_name = result.category.value
            grouped[category_name].append(result)
        
        logger.info(f"Grouped results: {len(grouped['confirmed'])} confirmed, "
                   f"{len(grouped['potential'])} potential, "
                   f"{len(grouped['discarded'])} discarded")
        
        return grouped
