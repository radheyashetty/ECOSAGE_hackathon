"""Conversation management: slot-filling, clarifying questions, session memory."""
from __future__ import annotations
import uuid
import re
from typing import Optional
from ecosage.models import EnvironmentalMetrics, EcoSageInput

# The 5 critical data categories for reasoning
CRITICAL_CATEGORIES = {
    "soil": {
        "fields": ["soil_organic_carbon_pct", "soil_ph", "soil_moisture_pct"],
        "question": "What is your soil condition? Specifically, do you know your soil organic carbon percentage (SOC%), soil pH, or soil moisture level?",
        "priority": 1,  # highest priority for reasoning
    },
    "land_use": {
        "fields": ["land_use_type", "crop"],
        "question": "What is the current land use? For example: monoculture farming, agroforestry, pasture, forest, or degraded land? What crops are grown?",
        "priority": 2,
    },
    "climate": {
        "fields": ["rainfall", "rainfall_mm_annual", "temperature_avg_c", "region"],
        "question": "What is the rainfall pattern in your area (low/moderate/high, or mm/year)? What is your region type (semi-arid, tropical, temperate)?",
        "priority": 3,
    },
    "biodiversity": {
        "fields": ["species_richness_index", "habitat_diversity_score"],
        "question": "Do you have any biodiversity data for your land? For example, species richness observations or habitat diversity assessments?",
        "priority": 4,
    },
    "human_impact": {
        "fields": ["pollution_index", "deforestation_rate_pct"],
        "question": "Are there human impact factors to consider? Such as pollution levels, deforestation rates, or nearby development?",
        "priority": 5,
    },
}

# In-memory session store
_sessions: dict[str, dict] = {}

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, dict]:
    """Get existing session or create new one. Returns (session_id, session_data)."""
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    _sessions[sid] = {
        "metrics": {},
        "conversation_history": [],
        "categories_filled": set(),
        "questions_asked": [],
    }
    return sid, _sessions[sid]

def update_session_metrics(session_id: str, metrics: dict):
    """Merge new metrics into session, preserving previously supplied values."""
    if session_id not in _sessions:
        get_or_create_session(session_id)
    
    session = _sessions[session_id]
    for k, v in metrics.items():
        if v is not None:
            session["metrics"][k] = v
            
    session["categories_filled"] = get_filled_categories(session["metrics"])

def extract_metrics_from_text(text: str) -> dict:
    """Use heuristics to extract environmental metrics from free-text input.
    E.g., 'SOC is 0.3%' -> {"soil_organic_carbon_pct": 0.3}
    'rainfall is low' -> {"rainfall": "low"}
    'monoculture wheat' -> {"crop": "monoculture wheat", "land_use_type": "monoculture"}
    'semi-arid region' -> {"region": "semi-arid"}
    """
    text_lower = text.lower()
    metrics = {}
    
    # SOC
    soc_match = re.search(r'soc\s*(?:is\s*)?(?:around\s*)?(\d+\.?\d*)\s*%', text_lower)
    if not soc_match:
        soc_match = re.search(r'soil organic carbon\s*(?:is\s*)?(?:around\s*)?(\d+\.?\d*)\s*%', text_lower)
    if soc_match:
        metrics["soil_organic_carbon_pct"] = float(soc_match.group(1))
        
    # pH
    ph_match = re.search(r'ph\s*(?:is\s*)?(?:of\s*)?(\d+\.?\d*)', text_lower)
    if ph_match:
        metrics["soil_ph"] = float(ph_match.group(1))
        
    # Rainfall categories
    if re.search(r'\b(low|moderate|high)\s+rainfall\b', text_lower):
        match = re.search(r'\b(low|moderate|high)\s+rainfall\b', text_lower)
        if match:
             metrics["rainfall"] = match.group(1)
    elif re.search(r'rainfall\s+is\s+(low|moderate|high)', text_lower):
        match = re.search(r'rainfall\s+is\s+(low|moderate|high)', text_lower)
        if match:
             metrics["rainfall"] = match.group(1)
             
    # Rainfall mm
    rain_mm_match = re.search(r'(\d+)\s*mm(?:\s*per\s*year|\s*/\s*yr|\s*annually)', text_lower)
    if rain_mm_match:
        metrics["rainfall_mm_annual"] = float(rain_mm_match.group(1))

    # Region
    regions = ["semi-arid", "tropical", "temperate", "arid", "mediterranean", "boreal"]
    for region in regions:
        if f"{region} region" in text_lower or f"in a {region}" in text_lower:
            metrics["region"] = region
            break
            
    # Land use
    land_uses = ["monoculture", "agroforestry", "pasture", "forest", "degraded", "polyculture"]
    for lu in land_uses:
        if lu in text_lower:
            metrics["land_use_type"] = lu
            break
            
    # Crop (simple heuristic)
    crop_match = re.search(r'(?:growing|grow|plant|planted|crop(?:s)?\s*(?:are|is)?)\s+([a-z\s]+)(?:[,\.]|$)', text_lower)
    if crop_match:
        crop_candidate = crop_match.group(1).strip()
        # filter out some stop words if needed, but keeping it simple
        if len(crop_candidate.split()) <= 3:
            metrics["crop"] = crop_candidate
            
    return metrics

def get_filled_categories(metrics: dict) -> set[str]:
    """Determine which of the 5 critical categories have data."""
    filled = set()
    for cat_name, cat_info in CRITICAL_CATEGORIES.items():
        if any(field in metrics for field in cat_info["fields"]):
            filled.add(cat_name)
    return filled

def get_clarifying_questions(metrics: dict, max_questions: int = 1) -> list[str]:
    """Generate targeted clarifying questions for missing critical data.
    Prioritized by impact on reasoning quality.
    Only asks for categories not yet filled.
    Returns at most max_questions questions."""
    filled = get_filled_categories(metrics)
    
    # Sort categories by priority
    sorted_cats = sorted(CRITICAL_CATEGORIES.items(), key=lambda x: x[1]["priority"])
    
    questions = []
    for cat_name, cat_info in sorted_cats:
        if cat_name not in filled:
            questions.append(cat_info["question"])
            if len(questions) >= max_questions:
                break
                
    return questions

def needs_clarification(metrics: dict) -> bool:
    """Return True if fewer than 3 critical categories are filled."""
    filled = get_filled_categories(metrics)
    return len(filled) < 3

def build_query_from_session(session_id: str, current_query: str) -> tuple[str, dict]:
    """Combine session history with current query to build full context.
    Returns (enriched_query, all_metrics)."""
    if session_id not in _sessions:
        return current_query, {}
        
    session = _sessions[session_id]
    all_metrics = session["metrics"]
    
    # Build enriched query
    parts = []
    if current_query:
        parts.append(f"Query: {current_query}")
        
    if all_metrics:
        metrics_str = ", ".join([f"{k}={v}" for k, v in all_metrics.items()])
        parts.append(f"Context metrics: {metrics_str}")
        
    enriched_query = "\n".join(parts)
    return enriched_query, all_metrics
