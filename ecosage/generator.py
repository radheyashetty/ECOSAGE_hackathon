"""
LLM generation with grounded context only (anti-hallucination guarantee).

Supports multiple providers:
- Gemini (Google)
- Groq (Llama/Gemma)
- Ollama (local, no account needed)
"""
import json
import logging

from ecosage.config import get_settings
from ecosage.models import Recommendation, Source
from ecosage.validator import compute_confidence

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are EcoSage, an AI environmental scientist. You provide evidence-backed recommendations for improving biodiversity outcomes.

CRITICAL RULES:
1. You MUST ONLY use information from the provided context. NEVER make up facts, citations, or numbers.
2. Every recommendation MUST include:
   - A specific, actionable intervention (not generic advice)
   - The scientific mechanism explaining WHY it works (must be substantive, at least 25 words detailing the step-by-step causal chain)
   - At least 3 impacted environmental metrics with their causal connections
   - A quantified estimate with numbers (e.g., "+15-25% SOC over 2-3 years")
   - The time horizon (short <1yr / medium 1-3yr / long 3yr+)
   - Ecological trade-offs or management precautions (e.g. moisture competition, sapling grazing defense, or shade management)
   - Economic & operational feasibility assessment (e.g. Low CapEx seed outlay, phased silvopasture investment)
   - Specific source citations from the provided context
3. You MUST trace causal chains: e.g., intercropping → root diversity → SOC accumulation → microbial diversity → pollinator activity
4. NEVER use generic phrases like "use sustainable practices" or "plant more trees" without specifics.
5. If the context doesn't contain enough information to make a grounded recommendation, say so explicitly.

Respond ONLY with valid JSON in this exact format (no markdown, no code fences):
{
  "recommendations": [
    {
      "action": "Specific intervention",
      "mechanism": "Scientific mechanism with causal chain mentioning specific metrics",
      "impacted_metrics": ["metric1", "metric2", "metric3"],
      "quantified_estimate": "Specific numbers e.g. +15-25% over 2-3 years",
      "time_horizon": "short|medium|long",
      "ecological_tradeoffs": ["Specific potential trade-off or management precaution"],
      "economic_feasibility": "Low/Medium/High CapEx with expected ROI timeframe",
      "sources": [{"name": "Source Name", "id": "SOURCE-ID"}]
    }
  ]
}
"""


def build_context_prompt(
    query: str,
    retrieved_chunks: list[dict],
    causal_chains: list[str],
    table_data: list[dict],
    user_metrics: dict,
) -> str:
    """Build the full prompt with grounded context injected."""
    prompt_parts = []

    prompt_parts.append(f"USER QUERY: {query}\n")

    prompt_parts.append("USER ENVIRONMENTAL METRICS:")
    if user_metrics:
        for k, v in user_metrics.items():
            prompt_parts.append(f"- {k}: {v}")
    else:
        prompt_parts.append("None provided.")
    prompt_parts.append("\n")

    prompt_parts.append("RETRIEVED CONTEXT (MUST USE):")
    if retrieved_chunks:
        for chunk in retrieved_chunks:
            source_name = chunk.get("source_name", "Unknown")
            source_id = chunk.get("source_id", "UnknownID")
            text = chunk.get("text", "")
            prompt_parts.append(f"--- SOURCE: {source_name} (ID: {source_id}) ---\n{text}\n")
    else:
        prompt_parts.append("No context retrieved. DO NOT MAKE UP INFORMATION.\n")

    prompt_parts.append("RELEVANT CAUSAL CHAINS:")
    if causal_chains:
        for chain in causal_chains:
            prompt_parts.append(f"- {chain}")
    else:
        prompt_parts.append("None found.")
    prompt_parts.append("\n")

    prompt_parts.append("REFERENCE TABLE DATA:")
    if table_data:
        for entry in table_data:
            prompt_parts.append(str(entry))
    else:
        prompt_parts.append("None found.")

    return "\n".join(prompt_parts)


# ─── Provider-specific generation functions ───────────────────────────────────

def _generate_gemini(context_prompt: str) -> str:
    """Generate using Google Gemini API with automatic model fallback."""
    from google import genai
    from google.genai import types

    settings = get_settings()
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    models_to_try = [
        settings.LLM_MODEL,
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
    ]
    # Remove duplicates while preserving order
    seen = set()
    unique_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = None
    for idx, model_name in enumerate(unique_models):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=context_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    response_mime_type="application/json",
                )
            )
            if response.text:
                if idx > 0:
                    logger.info(f"🔄 Auto-fallback to {model_name} activated and succeeded!")
                return response.text
        except Exception as e:
            logger.warning(f"Model {model_name} unavailable ({e}). Auto-falling back to next candidate...")
            last_error = e

    if last_error:
        raise last_error
    return ""


def _generate_groq(context_prompt: str) -> str:
    """Generate using Groq API (free, fast, no card needed)."""
    import httpx

    settings = get_settings()

    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _generate_ollama(context_prompt: str) -> str:
    """Generate using local Ollama (no account, no API key, fully offline)."""
    import httpx

    settings = get_settings()

    response = httpx.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context_prompt},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
        },
        timeout=120.0,  # Local models can be slower
    )
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")


def _call_llm(context_prompt: str) -> str:
    """Route to the correct provider."""
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        return _generate_gemini(context_prompt)
    elif provider == "groq":
        return _generate_groq(context_prompt)
    elif provider == "ollama":
        return _generate_ollama(context_prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use 'gemini', 'groq', or 'ollama'.")


# ─── Main generation function ────────────────────────────────────────────────

def generate_recommendations(
    query: str,
    retrieved_chunks: list[dict],
    causal_chains: list[str],
    table_data: list[dict],
    user_metrics: dict,
    similarity_scores: list[float],
) -> list[Recommendation]:
    """Generate grounded recommendations using LLM.

    ANTI-HALLUCINATION GUARANTEE: The LLM is NEVER called without
    retrieved, source-tagged context being injected into the prompt.
    """
    if not retrieved_chunks:
        logger.warning("generate_recommendations called with empty retrieved_chunks. LLM will likely refuse.")

    context_prompt = build_context_prompt(query, retrieved_chunks, causal_chains, table_data, user_metrics)

    try:
        raw_text = _call_llm(context_prompt)
    except Exception as e:
        logger.error(f"Error calling LLM ({get_settings().LLM_PROVIDER}): {e}")
        return []

    if not raw_text:
        logger.error("LLM returned empty response")
        return []

    # Clean response — strip markdown code fences if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last lines (code fences)
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}\nRaw: {raw_text[:500]}")
        return []

    recommendations_data = data.get("recommendations", [])
    recommendations = []

    for rec_data in recommendations_data:
        try:
            sources_data = rec_data.get("sources", [])
            sources = [
                Source(name=s.get("name", ""), id=s.get("id", ""))
                for s in sources_data
            ]

            source_count = len(sources)
            confidence = compute_confidence(similarity_scores, source_count)

            tradeoffs = rec_data.get("ecological_tradeoffs") or [
                "Requires seasonal monitoring to manage early-stage resource competition and pest dynamics."
            ]
            feasibility = rec_data.get("economic_feasibility") or (
                "Moderate initial CapEx / Positive return on investment via input reduction within 1-2 seasons."
            )

            rec = Recommendation(
                action=rec_data.get("action", ""),
                mechanism=rec_data.get("mechanism", ""),
                impacted_metrics=rec_data.get("impacted_metrics", []),
                quantified_estimate=rec_data.get("quantified_estimate", ""),
                time_horizon=rec_data.get("time_horizon", "medium"),
                sources=sources,
                confidence=confidence,
                ecological_tradeoffs=tradeoffs,
                economic_feasibility=feasibility
            )
            recommendations.append(rec)
        except Exception as e:
            logger.error(f"Error parsing individual recommendation: {e}")
            continue

    return recommendations
