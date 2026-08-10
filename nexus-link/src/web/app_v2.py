"""NeXuS-LinK Web Application - Simplified API"""
import os
import logging
import asyncio
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS

from src.core.searcher import SearchEngine
from src.core.matcher import ResultMatcher
from src.models.query_v2 import SearchQuery, PersonProfile, Gender
from src.sources.demo import DemoPhoneSource, DemoSocialSource, DemoEmailSource
from src.sources.dating import DatingSourcesProvider


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
engine.register_source(DatingSourcesProvider())

# In-memory result storage
results_store = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "ok"}), 200


@app.route("/api/version", methods=["GET"])
def version():
    """Get NeXuS-LinK version info"""
    return jsonify({
        "name": "NeXuS-LinK",
        "version": "2.0.0",
        "description": "Smart OSINT Search with Intelligent Filtering"
    }), 200


@app.route("/api/search", methods=["POST"])
def search():
    """
    Start a search with known person profile.
    
    Request:
        {
            "phone": "+14155550123",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "gender": "male"  # male, female, unknown
        }
    
    Response:
        {
            "search_id": "uuid",
            "status": "complete",
            "profile": {...},
            "confirmed_accounts": [...],
            "potential_accounts": [...],
            "dating_accounts": [...],
            "confidence": 0.85,
            "summary": "Found 5 confirmed accounts, 3 possible matches, 2 dating profiles"
        }
    """
    try:
        data = request.get_json()
        phone = data.get("phone")
        email = data.get("email")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        age = data.get("age")
        gender = data.get("gender", "unknown")
        
        if (not phone and not email) or not first_name or not last_name:
            return jsonify({"error": "phone or email, first_name, last_name required"}), 400
        
        # Use phone or email for search (prefer phone)
        search_identifier = phone or email
        search_type = "phone" if phone else "email"
        
        # Create person profile
        try:
            gender_enum = Gender(gender.lower())
        except ValueError:
            gender_enum = Gender.UNKNOWN
        
        profile = PersonProfile(
            phone=phone or "",
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender_enum
        )
        
        # Create search query
        search_id = str(uuid.uuid4())
        query = SearchQuery(
            query_id=search_id,
            profile=profile,
            sources=[]  # Use all available sources
        )
        
        # Execute searches for both phone and email
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Search by phone if provided
            phone_hits = []
            if phone:
                phone_hits = loop.run_until_complete(engine.search(query, query_type="phone"))
            
            # Search by email if provided
            email_hits = []
            if email:
                query.sources = []  # Reset sources for new search
                email_hits = loop.run_until_complete(engine.search(query, query_type="email"))
            
            # Combine all hits
            all_hits = phone_hits + email_hits
        finally:
            loop.close()
        
        # Filter and consolidate results
        result = ResultMatcher.filter_and_consolidate(search_id, profile, all_hits)
        results_store[search_id] = result
        
        # Separate dating accounts from general accounts
        dating_accounts = [h for h in result.potential_accounts if h.source == "dating_sources"]
        general_potential = [h for h in result.potential_accounts if h.source != "dating_sources"]
        
        # Build response with dating accounts as separate section
        confirmed = [
            {
                "name": h.match,
                "platform": h.platform,
                "url": h.url,
                "gender": h.gender.value,
                "location": h.location,
                "confidence": ResultMatcher.overall_match_score(h, profile)
            }
            for h in result.confirmed_accounts
        ]
        
        potential = [
            {
                "name": h.match,
                "platform": h.platform,
                "url": h.url,
                "gender": h.gender.value,
                "location": h.location,
                "confidence": ResultMatcher.overall_match_score(h, profile)
            }
            for h in general_potential
        ]
        
        dating = [
            {
                "name": h.match,
                "platform": h.platform,
                "url": h.url,
                "gender": h.gender.value,
                "confidence": ResultMatcher.overall_match_score(h, profile),
                "note": "Account found on dating platform (may use different name)"
            }
            for h in dating_accounts
        ]
        
        logger.info(f"Search {search_id}: {len(confirmed)} confirmed, {len(general_potential)} potential, {len(dating)} dating profiles")
        
        return jsonify({
            "search_id": search_id,
            "status": "complete",
            "profile": {
                "phone": profile.phone,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "age": profile.age,
                "gender": profile.gender.value
            },
            "confirmed_accounts": confirmed,
            "potential_accounts": potential,
            "dating_accounts": dating,
            "confidence": result.confidence_score,
            "summary": f"Found {len(confirmed)} confirmed accounts, {len(general_potential)} possible matches, {len(dating)} dating profiles"
        }), 200
    
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/<search_id>", methods=["GET"])
def get_results(search_id):
    """
    Get detailed results for a search.
    
    Shows:
    - Confirmed accounts (high confidence match)
    - Potential accounts (possibly linked to this person)
    - Detailed scoring breakdown
    """
    try:
        if search_id not in results_store:
            return jsonify({"error": "search not found"}), 404
        
        result = results_store[search_id]
        
        confirmed = [
            {
                "name": h.match,
                "platform": h.platform,
                "url": h.url,
                "gender": h.gender.value,
                "location": h.location,
                "confidence": ResultMatcher.overall_match_score(h, result.profile),
                "source": h.source
            }
            for h in result.confirmed_accounts
        ]
        
        potential = [
            {
                "name": h.match,
                "platform": h.platform,
                "url": h.url,
                "gender": h.gender.value,
                "location": h.location,
                "confidence": ResultMatcher.overall_match_score(h, result.profile),
                "source": h.source,
                "note": "Possibly linked to this person - verify manually"
            }
            for h in result.potential_accounts
        ]
        
        return jsonify({
            "search_id": search_id,
            "profile": {
                "phone": result.profile.phone,
                "name": f"{result.profile.first_name} {result.profile.last_name}",
                "age": result.profile.age,
                "gender": result.profile.gender.value
            },
            "confirmed_accounts": {
                "count": len(confirmed),
                "accounts": confirmed,
                "note": "High confidence matches to the person profile"
            },
            "potential_accounts": {
                "count": len(potential),
                "accounts": potential,
                "note": "Possibly linked to this person - lower confidence, verify before use"
            },
            "overall_confidence": result.confidence_score,
            "total_accounts_found": result.total_accounts()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
