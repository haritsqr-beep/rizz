"""NeXuS-LinK Web Application"""
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import uuid
from datetime import datetime

from ..core.searcher import SearchEngine
from ..core.refiner import RefinementEngine
from ..core.aggregator import Aggregator
from ..models.query import SearchQuery, Result
from ..sources.demo import DemoPhoneSource, DemoSocialSource, DemoEmailSource


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize search engine
engine = SearchEngine()
engine.register_source(DemoPhoneSource())
engine.register_source(DemoSocialSource())
engine.register_source(DemoEmailSource())

# In-memory result storage (use database in production)
results_store = {}
hits_store = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route("/api/search", methods=["POST"])
async def search():
    """
    Start a new search.
    
    Request:
        {
            "query": "+14155550123",
            "type": "phone",  # phone, email, username, name
            "auto_confirm": false,
            "sources": ["demo_phone", "demo_social"]  # optional
        }
    
    Response:
        {
            "search_id": "uuid",
            "status": "searching",
            "hits": [...]
        }
    """
    try:
        data = request.get_json()
        query_text = data.get("query")
        query_type = data.get("type", "phone")
        auto_confirm = data.get("auto_confirm", False)
        sources = data.get("sources", [])
        
        if not query_text:
            return jsonify({"error": "query required"}), 400
        
        # Create search query
        search_id = str(uuid.uuid4())
        query = SearchQuery(
            query_id=search_id,
            query=query_text,
            query_type=query_type,
            auto_confirm=auto_confirm,
            sources=sources
        )
        
        # Execute search
        hits = await engine.search(query)
        
        # Store results
        hits_store[search_id] = hits
        
        logger.info(f"Search {search_id}: Found {len(hits)} hits")
        
        return jsonify({
            "search_id": search_id,
            "status": "complete",
            "hit_count": len(hits),
            "hits": [
                {
                    "hit_id": hit.hit_id,
                    "match": hit.match,
                    "platform": hit.platform,
                    "source": hit.source,
                    "confidence": hit.confidence,
                    "url": hit.url
                }
                for hit in hits
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/refinement-questions/<hit_id>", methods=["GET"])
def get_refinement_questions(hit_id):
    """
    Get refinement questions for a specific hit.
    
    Response:
        {
            "questions": [
                {
                    "id": "name_match",
                    "question": "Does the name match?",
                    "options": ["yes", "maybe", "no"],
                    "context": "Match: john_doe87",
                    "platform": "Instagram"
                }
            ]
        }
    """
    try:
        # Find the hit
        for hits in hits_store.values():
            hit = next((h for h in hits if h.hit_id == hit_id), None)
            if hit:
                questions = RefinementEngine.get_refinement_questions(hit)
                return jsonify({"questions": questions}), 200
        
        return jsonify({"error": "hit not found"}), 404
    
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/confirm", methods=["POST"])
def confirm_hit():
    """
    Submit confirmation answers for a hit.
    
    Request:
        {
            "search_id": "uuid",
            "hit_id": "uuid",
            "answers": {
                "name_match": "yes",
                "age_match": "maybe",
                "location_match": "yes"
            },
            "notes": "Optional notes"
        }
    
    Response:
        {
            "result_id": "uuid",
            "category": "confirmed",
            "confidence": 0.85
        }
    """
    try:
        data = request.get_json()
        search_id = data.get("search_id")
        hit_id = data.get("hit_id")
        answers = data.get("answers", {})
        notes = data.get("notes", "")
        
        # Find the hit
        hit = next(
            (h for hits in hits_store.values() for h in hits if h.hit_id == hit_id),
            None
        )
        if not hit:
            return jsonify({"error": "hit not found"}), 404
        
        # Process confirmation
        confirmation = RefinementEngine.process_confirmation(hit, answers, notes)
        
        # Create or get result
        result_id = search_id
        if result_id not in results_store:
            result = Result(
                result_id=result_id,
                search_query_id=search_id,
                hits=[hit]
            )
            results_store[result_id] = result
        else:
            result = results_store[result_id]
        
        # Store confirmation
        result.confirmations[hit_id] = confirmation
        
        # Update category
        result.update_category()
        
        logger.info(f"Confirmed {hit_id}: {confirmation.confidence_score():.1f}% - {result.category.value}")
        
        return jsonify({
            "result_id": result_id,
            "category": result.category.value,
            "confidence": confirmation.confidence_score()
        }), 200
    
    except Exception as e:
        logger.error(f"Confirmation error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/<search_id>", methods=["GET"])
def get_results(search_id):
    """
    Get all results for a search, grouped by category.
    
    Response:
        {
            "confirmed": [...],
            "potential": [...],
            "discarded": [...],
            "graph": {
                "nodes": [...],
                "edges": [...]
            }
        }
    """
    try:
        if search_id not in results_store:
            return jsonify({"error": "search not found"}), 404
        
        result = results_store[search_id]
        hits = hits_store.get(search_id, [])
        
        # Build connection graph
        graph = Aggregator.build_connection_graph(hits)
        
        return jsonify({
            "search_id": search_id,
            "category": result.category.value,
            "overall_confidence": result.overall_confidence,
            "hit_count": len(result.hits),
            "confirmed_count": len([c for c in result.confirmations.values() if c.confidence_score() >= 75]),
            "potential_count": len([c for c in result.confirmations.values() if 40 <= c.confidence_score() < 75]),
            "graph": graph
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/version", methods=["GET"])
def version():
    """Get NeXuS-LinK version info"""
    return jsonify({
        "name": "NeXuS-LinK",
        "version": "1.0.0",
        "description": "Smart OSINT Search Engine with Refinable Results"
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
