# 🌿 EcoSage — AI Environmental Scientist for Biodiversity Intelligence

> An evidence-grounded, multi-metric reasoning system that behaves like an environmental scientist — not a chatbot.

[![CI](https://github.com/YOUR_USERNAME/ecosage/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ecosage/actions)

## 🎯 What is EcoSage?

EcoSage is a conversational AI system that ingests soil, land-use, biodiversity, climate, and human-impact data; retrieves grounded scientific evidence from an indexed knowledge base; and produces **multi-variable, evidence-backed recommendations** to improve biodiversity outcomes on a given parcel of land.

### Key Differentiators
- **Not a prompt wrapper**: Every recommendation is traceable to retrieved source documents
- **Multi-metric causal reasoning**: Links ≥3 environmental variables per recommendation (e.g., soil organic carbon → microbial diversity → pollinator activity)
- **Anti-hallucination guarantee**: The LLM is never called without grounded, source-tagged context
- **Output validation**: Post-generation validator rejects generic/ungrounded recommendations

## 🏗️ Architecture

```
User Input (text/JSON)
       │
       ▼
┌───────────────────────┐
│  Input Handler &       │
│  Slot-Filling Validator │
└───────────┬───────────┘
            │
     ┌──────┴──────┐
     │ Input        │
     │ Complete?    │
     └───┬────┬────┘
    No  │    │  Yes
        │    │
        ▼    ▼
  Clarifying   Reasoning
  Questions    Orchestrator
                    │
          ┌────────┼────────┐
          ▼         ▼         ▼
    ChromaDB    Causal     Reference
    Vector DB   Graph      Tables
          │         │         │
          └────────┼────────┘
                    ▼
          Context Assembly
                    │
                    ▼
          LLM Generation
          (grounded only)
                    │
                    ▼
          Output Validator
          (✓ citation, ✓ quant,
           ✓ mechanism, ✓ ≥3 metrics)
                    │
                    ▼
          Structured Response
          + Sources Panel
```

### Component Details

| Component | File | Purpose |
|---|---|---|
| Input Handler | `ecosage/conversation.py` | Slot-filling, metric extraction, session memory |
| Retrieval Layer | `ecosage/retrieval.py` | ChromaDB vector search with trace logging |
| Knowledge Base | `corpus/` | 8 source documents + 3 structured reference tables |
| Causal Graph | `ecosage/causal_graph.py` | 20+ source-tagged edges linking environmental variables |
| Generator | `ecosage/generator.py` | LLM generation with mandatory grounded context |
| Validator | `ecosage/validator.py` | Rejects generic/ungrounded outputs |
| Orchestrator | `ecosage/orchestrator.py` | Coordinates full reasoning pipeline |
| API | `ecosage/api.py` | FastAPI REST endpoints |
| UI | `ui/app.py` | Streamlit chat interface with sources panel |

## 📚 Knowledge Base

### Source Documents (8 indexed documents)
| Source ID | Document | Key Data |
|---|---|---|
| FAO-SOC-2017 | FAO Soil Organic Carbon Report | SOC benchmarks, restoration rates |
| IPCC-AR6-LU | IPCC AR6 Land Use Chapter | Climate-biodiversity interactions, fragmentation |
| COVER-CROP-2019 | Cover Cropping Meta-Analysis | SOC +8-15%, erosion reduction 40-60% |
| AGROFOR-BIO-2020 | Agroforestry & Biodiversity | Bird richness +40-60%, SOC +15-25% |
| INTERCROP-2021 | Intercropping in Semi-Arid | Water efficiency +15-25%, N fixation |
| FRAG-ECO-2018 | Habitat Fragmentation Thresholds | Species decline 20-50% below 10ha |
| POLLIN-ECO-2020 | Pollinator Ecology | Diversity -30-50% in monoculture |
| MICRO-SOIL-2021 | Soil Microbiome | SOC-microbiome feedback, r²=0.72 |

### Structured Reference Tables
- `soc_benchmarks.json` — SOC % ranges by biome/land-use
- `species_richness.json` — Species richness indices by land-use type
- `rainfall_biodiversity.json` — Rainfall-biodiversity correlations

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- A free Google Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ecosage.git
cd ecosage

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Ingest knowledge base into ChromaDB
python -m ecosage.ingest

# Start the API server
uvicorn ecosage.api:app --reload --port 8000

# In a new terminal, start the Streamlit UI
streamlit run ui/app.py
```

## 🧪 Testing

```bash
# Run unit tests (no API key needed)
pytest tests/test_validator.py -v

# Run acceptance tests (requires API key + ingested KB)
pytest tests/test_acceptance.py -v -m acceptance

# Lint
ruff check ecosage/ tests/ ui/
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Main conversation endpoint |
| GET | `/debug/retrieval/{session_id}` | Inspect retrieval traces |
| GET | `/health` | Health check |
| POST | `/ingest` | Re-ingest knowledge base |

### Example Request
```json
{
  "session_id": "demo-001",
  "metrics": {
    "soil_organic_carbon_pct": 0.3,
    "rainfall": "low",
    "crop": "monoculture wheat",
    "region": "semi-arid"
  },
  "query_text": "Biodiversity is declining on my land"
}
```

### Example Response (abbreviated)
```json
{
  "session_id": "demo-001",
  "recommendations": [
    {
      "action": "Introduce agroforestry with nitrogen-fixing tree species",
      "mechanism": "Agroforestry increases root diversity → SOC accumulation → microbial diversity → pollinator habitat",
      "impacted_metrics": ["soil_organic_carbon_pct", "species_richness_index", "habitat_diversity_score"],
      "quantified_estimate": "+15-25% SOC over 2-3 years",
      "time_horizon": "medium",
      "confidence": "High",
      "sources": [{"name": "FAO Soil Organic Carbon Report", "id": "FAO-SOC-2017"}]
    }
  ]
}
```

## 🔗 Multi-Metric Causal Graph

EcoSage's reasoning engine traverses a causal graph of 20+ source-tagged relationships:

```
intercropping → root_diversity → soil_organic_carbon → microbial_diversity → nutrient_cycling
                                         ↓
                               soil_moisture_retention → species_survival
                                         ↑
                                      rainfall

land_use_intensification → habitat_fragmentation → species_richness
                                                        ↑
crop_diversity → pollinator_diversity ─────────────────┘
```

Every edge is tagged with its source document and quantification.

## 🛡️ Anti-Hallucination Guarantees

1. **Retrieval-first**: LLM never generates without source-tagged context
2. **Output validator**: Checks every response for:
   - ✓ Named citation present
   - ✓ Quantified estimate (contains numbers)
   - ✓ Mechanism with ≥2 metrics linked
   - ✓ No generic phrases (blocklist enforced)
   - ✓ Source IDs match retrieval trace
3. **Confidence scoring**: Rule-based (similarity ≥ 0.80 + ≥2 sources = High)
4. **Retry on failure**: Up to 2 retries with stricter prompting if validation fails

## 📁 Project Structure

```
darukaa/
├── corpus/                  # Knowledge base
│   ├── raw/                 # Source documents (8 .md files)
│   └── tables/              # Structured reference tables (3 .json)
├── ecosage/                 # Core application
│   ├── api.py               # FastAPI endpoints
│   ├── causal_graph.py      # Multi-metric causal graph
│   ├── config.py            # Settings
│   ├── conversation.py      # Session memory & slot-filling
│   ├── generator.py         # LLM generation (grounded)
│   ├── ingest.py            # Corpus ingestion pipeline
│   ├── models.py            # Pydantic schemas
│   ├── orchestrator.py      # Reasoning pipeline
│   ├── retrieval.py         # Vector search + traces
│   └── validator.py         # Output validation
├── ui/
│   └── app.py               # Streamlit chat UI
├── tests/
│   ├── test_acceptance.py   # PRD Section 6 test
│   └── test_validator.py    # Validator unit tests
├── .github/workflows/ci.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🏆 Evaluation Criteria Mapping

| Criterion | Weight | How Satisfied |
|---|---|---|
| Depth of Reasoning | 30% | Multi-metric causal graph with 20+ edges; output validator rejects shallow advice |
| Scientific Grounding | 25% | RAG over 8 real-source documents; mandatory citations |
| Knowledge System | 20% | ChromaDB + structured tables; `/debug/retrieval` endpoint |
| Conversational Intelligence | 15% | Slot-filling; session memory; persona detection |
| Output Clarity | 10% | Fixed JSON contract; Sources panel in UI |

## ⚖️ Tech Stack

| Component | Technology | Cost |
|---|---|---|
| Backend | Python, FastAPI | Free |
| Vector Store | ChromaDB (local) | Free |
| Embeddings | Google Gemini text-embedding-004 | Free tier |
| LLM | Google Gemini 2.0 Flash | Free tier |
| UI | Streamlit | Free |
| CI/CD | GitHub Actions | Free |

## 📄 License

MIT
