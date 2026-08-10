# NeXuS-LinK

**Smart OSINT Search Engine with Refinable Results**

A containerized, intelligent search aggregator that asks clarifying questions to refine results and categorizes findings as confirmed ("yes") or potential ("maybe").

## Overview

NeXuS-LinK improves on traditional OSINT tools by using **interactive refinement**:

1. **Initial Search** - Query multiple sources (lookup sites, dorking, social media)
2. **Clarifying Questions** - When hits are found, ask about age, name confidence, location
3. **Data Collection** - Compile address, social media, email, phone numbers, and other identifiers
4. **Smart Categorization** - Organize results into "confirmed" and "potential" categories
5. **Unified Dashboard** - View all cross-referenced data in one place

## Features

- 🔍 Multi-source OSINT search
- ❓ Interactive confirmation questions
- 📊 Categorized result buckets (yes / maybe)
- 🔗 Cross-reference matching (same person across platforms)
- 🐳 Fully containerized (Docker)
- 🌐 Web UI + CLI options
- 🚀 Extensible search providers

## Quick Start

```bash
# Clone and build
git clone https://github.com/yourusername/nexus-link.git
cd nexus-link
docker compose up

# Open the web interface
# → http://localhost:8080
```

## Using NeXuS-LinK

### Web Interface

1. Enter a search query (phone number, email, username, etc.)
2. Select search scope (phone lookup, social media, reverse email, etc.)
3. Start search → system queries all configured sources
4. **Refinement Step**: For each hit, answer clarifying questions:
   - Do you recognize this name? (Yes / Maybe / No)
   - Age match? (Yes / Maybe / No)
   - Location match? (Yes / Maybe / Unknown)
5. **View Results**:
   - **Confirmed** tab: High-confidence matches
   - **Potential** tab: Uncertain/partial matches
   - **Connections** tab: Cross-platform links

### CLI

```bash
# Search and export as JSON
nexus-link search +14155550123 --format json --output result.json

# Search with auto-confirmation (no UI)
nexus-link search "john.doe@example.com" --auto-confirm --threshold high

# Batch search from file
nexus-link batch-search numbers.txt --output report.html
```

## Architecture

```
nexus-link/
  src/
    core/
      searcher.py          - multi-source search engine
      refiner.py           - question/confirmation logic
      categorizer.py       - yes/maybe classification
      aggregator.py        - cross-reference linking
    sources/               - search provider plugins
      phone_lookup.py
      social_media.py
      email_reverse.py
      dorking.py
    models/
      query.py
      result.py
      confirmation.py
    web/                   - Flask/React web UI
      api/
      frontend/
    cli.py                 - CLI entry point
  docker-compose.yml
  Dockerfile
  requirements.txt
```

## Data Sources (Built-In)

| Source | Query Type | Data Points |
| --- | --- | --- |
| Phone Lookup | +1-555-0123 | Carrier, type, location |
| Reverse Phone | +1-555-0123 | People, addresses, social |
| Email Reverse | user@gmail.com | Associated names, numbers, social |
| Social Media Search | @username | Profiles, bio, links |
| Dorking | "name city" | Google indexed results |
| Domain WHOIS | user@company.com | Email registrations, linked domains |

## Refinement Questions

When a potential match is found:

```
✓ Hit found: jane_doe87 on Instagram

Confirm this match:
  □ Name matches? (yes/maybe/no)
  □ Age correct? (yes/maybe/no)  
  □ Location matches? (yes/maybe/unknown)
  □ Time zone reasonable? (yes/maybe/no)

Store as: [Confirmed] or [Potential]
```

## Viewing Results

### Confirmed Results
- All answers are "yes" or strong "maybe"
- Cross-referenced across 2+ sources
- Confidence score: 80%+

### Potential Results
- Some "maybe" answers
- Limited cross-reference data
- Confidence score: 40-79%

### Connections Graph
- Shows how sources connect
- Highlights discrepancies (different names, ages, locations)
- Suggests additional queries

## Installation

### With Docker (Recommended)

```bash
docker compose up
# Web: http://localhost:8080
# API: http://localhost:5000
```

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m nexus_link.web --port 8080
```

## Configuration

Set environment variables or edit `config.yaml`:

```bash
# Search behavior
NEXUS_AUTO_CONFIRM=false          # require manual confirmation
NEXUS_CONFIDENCE_THRESHOLD=65     # % for "confirmed" category
NEXUS_SOURCES=phone,social,email  # which sources to use

# API keys (optional - some features need these)
NUMVERIFY_API_KEY=...
IPQS_API_KEY=...
```

## API Examples

```bash
# Start a search
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "+14155550123", "type": "phone", "auto_confirm": false}'

# Get results with refinements
curl http://localhost:5000/results/search-id-123

# Refine a result
curl -X POST http://localhost:5000/refine \
  -H "Content-Type: application/json" \
  -d '{
    "result_id": "result-456",
    "name_match": "yes",
    "age_match": "maybe",
    "location_match": "yes"
  }'
```

## Adding Search Providers

Create a new file in `src/sources/`:

```python
# src/sources/my_provider.py
from src.core.searcher import BaseSource

class MyProvider(BaseSource):
    name = "my_provider"
    supports_types = ["phone", "email", "username"]
    
    async def search(self, query, query_type):
        # Return list of hits
        return [
            {
                "source": self.name,
                "match": "jane_doe",
                "platform": "Instagram",
                "url": "https://instagram.com/jane_doe",
                "confidence": 0.85
            }
        ]
```

It's automatically loaded and run alongside other providers.

## Safety & Ethics

NeXuS-LinK only queries:
- Publicly available data
- Official APIs (where authorized)
- Public search engines
- Published social media profiles

It **never**:
- Scrapes without permission
- Bypasses paywalls or restrictions
- Accesses leaked/breach data
- Logs into accounts
- Violates terms of service

**Use responsibly.** You are responsible for compliance with laws in your jurisdiction and the ToS of each provider.

## License

MIT - See LICENSE file.

## Contributing

Contributions welcome! Open an issue or submit a PR.

## Credits

NeXuS-LinK builds upon intelligent OSINT search patterns and incorporates search methodology concepts from prior research in the field. Special thanks to the open-source OSINT community for establishing best practices in ethical data collection and cross-reference validation.

---

Made with ❤️ for OSINT researchers and security professionals.
