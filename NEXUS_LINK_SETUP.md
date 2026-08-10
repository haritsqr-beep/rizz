"""NeXuS-LinK - Quick Setup Guide"""

# NeXuS-LinK Container Repository - Setup Complete! ✅

## Project Structure

```
nexus-link/
├── src/
│   ├── core/
│   │   ├── searcher.py         - Multi-source search orchestration
│   │   ├── refiner.py          - Interactive refinement questions
│   │   └── aggregator.py       - Result cross-referencing
│   ├── models/
│   │   └── query.py            - Data models (SearchQuery, Hit, Result, Confirmation)
│   ├── sources/
│   │   └── demo.py             - Demo search providers (Phone, Social, Email)
│   └── web/
│       └── app.py              - Flask web API
├── Dockerfile                  - Container build
├── docker-compose.yml          - Multi-container orchestration
├── requirements.txt            - Python dependencies
├── README.md                   - Full documentation
├── LICENSE                     - MIT License
└── .gitignore                 - Git ignore rules
```

## Key Features

✅ **Multi-source OSINT search** - Queries phone, social media, email, and more
✅ **Interactive refinement** - Asks clarifying questions to confirm hits
✅ **Smart categorization** - Groups results as "confirmed" or "potential"
✅ **Cross-reference linking** - Finds same person across platforms
✅ **REST API** - Full API for programmatic access
✅ **Containerized** - Docker for easy deployment

## Quick Start

### Option 1: Docker (Recommended)
```bash
cd nexus-link
docker compose up
# Open http://localhost:5000
```

### Option 2: Manual
```bash
cd nexus-link
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m src.web.app
```

## API Endpoints

### POST /api/search
Start a search
```json
{
  "query": "+14155550123",
  "type": "phone",
  "auto_confirm": false,
  "sources": []
}
```

### GET /api/refinement-questions/<hit_id>
Get refinement questions for a hit

### POST /api/confirm
Submit confirmation answers
```json
{
  "search_id": "uuid",
  "hit_id": "uuid",
  "answers": {
    "name_match": "yes",
    "age_match": "maybe",
    "location_match": "yes"
  }
}
```

### GET /api/results/<search_id>
Get categorized results

## Search Flow

1. User enters query (phone, email, username, etc.)
2. NeXuS-LinK queries all available sources in parallel
3. For each hit, user answers refinement questions:
   - Does the name match?
   - Age correct?
   - Location match?
   - Timezone reasonable?
4. Results categorized based on confidence:
   - **Confirmed**: 75%+ confidence
   - **Potential**: 40-74% confidence
   - **Discarded**: <40% confidence
5. View all results with cross-reference connections

## Adding New Search Providers

Create a new file in `src/sources/`:

```python
from src.core.searcher import BaseSource
from src.models.query import Hit

class MyProvider(BaseSource):
    name = "my_source"
    supports_types = ["phone", "email", "username"]
    
    async def search(self, query, query_type):
        # Your search logic
        return [Hit(...), ...]
```

It's automatically loaded by SearchEngine!

## Customization

### Search Thresholds
Edit `docker-compose.yml`:
```yaml
environment:
  - NEXUS_CONFIDENCE_THRESHOLD=65  # % for "confirmed" category
```

### API Keys
Set environment variables for integrated providers:
```bash
NUMVERIFY_API_KEY=your_key
IPQS_API_KEY=your_key
```

## Clean & Simple

✨ **No Discord integration** - Clean codebase
✨ **Standalone repository** - No external dependencies
✨ **Proper credits** - Acknowledges inspiration without clutter
✨ **Ready to extend** - Add providers, customizations easily

## Next Steps

1. Commit this to your repository
2. Deploy to Docker/Kubernetes
3. Add real search providers (phone, social, email APIs)
4. Build frontend UI (React/Vue)
5. Integrate with your OSINT workflows

---

**Made for OSINT professionals who value clean code and thoughtful design.**
