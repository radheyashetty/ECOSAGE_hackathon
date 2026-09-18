"""Reasoning orchestrator: coordinates retrieval, graph traversal, generation, and validation."""
from __future__ import annotations

from ecosage.causal_graph import (
    get_causal_chain,
    get_edges_for_intervention,
    get_related_metrics,
    render_chain_text,
)
from ecosage.conversation import (
    build_query_from_session,
    extract_metrics_from_text,
    get_clarifying_questions,
    get_or_create_session,
    needs_clarification,
    update_session_metrics,
)
from ecosage.failsafe import generate_failsafe_recommendations
from ecosage.generator import generate_recommendations
from ecosage.geo_inference import infer_climate_priors
from ecosage.logger import get_logger
from ecosage.models import EcoSageInput, EcoSageResponse
from ecosage.retrieval import get_retrieval_trace, link_trace_to_recommendations, lookup_structured_table, retrieve
from ecosage.validator import validate_response

logger = get_logger("orchestrator")

MAX_RETRIES = 2

def process_input(input_data: EcoSageInput) -> EcoSageResponse:
    """Main reasoning pipeline.
    
    Steps:
    1. Parse & validate input
    2. Get/create session, merge metrics
    3. Extract metrics from free text if present
    4. Check if sufficient data exists
    5. If not enough data -> return clarifying questions
    6. If enough data:
       a. Retrieve relevant context from knowledge base
       b. Traverse causal graph for relevant chains
       c. Look up structured reference tables
       d. Generate recommendations with grounded context
       e. Validate output
       f. Retry if validation fails (max 2 retries)
    7. Return structured response with reasoning trace
    """
    
    # Step 1-2: Session management
    session_id, session = get_or_create_session(input_data.session_id)
    
    # Step 3: Extract and merge metrics
    all_metrics = {}
    if input_data.metrics:
        metrics_dict = input_data.metrics.model_dump(exclude_none=True)
        all_metrics.update(metrics_dict)
    
    if input_data.query_text:
        extracted = extract_metrics_from_text(input_data.query_text)
        all_metrics.update(extracted)

    # Step 3b: Geo-Coordinate Regional Prior Inference (PRD Bonus FR-5.3)
    if input_data.geo and input_data.geo.lat is not None and input_data.geo.lng is not None:
        priors = infer_climate_priors(input_data.geo.lat, input_data.geo.lng)
        for k, v in priors.items():
            if k not in all_metrics and k != "_geo_inferred_zone":
                all_metrics[k] = v

    update_session_metrics(session_id, all_metrics)
    
    # Step 4-5: Check completeness
    if needs_clarification(session["metrics"]):
        questions = get_clarifying_questions(session["metrics"])
        return EcoSageResponse(
            session_id=session_id,
            clarifying_questions=questions,
            recommendations=[],
            reasoning_trace={"slots": dict(session["metrics"])},
        )
    
    # Step 6: Full reasoning pipeline
    query, merged_metrics = build_query_from_session(session_id, input_data.query_text or "")
    
    # 6a: Retrieve
    retrieval_results = retrieve(query, session_id=session_id)
    retrieved_chunks = [
        {"text": r.chunk_text, "source_id": r.source_id, "source_name": r.source_name, "similarity": r.similarity_score}
        for r in retrieval_results
    ] if retrieval_results else []
    similarity_scores = [r.similarity_score for r in retrieval_results] if retrieval_results else []
    retrieved_source_ids = {r.source_id for r in retrieval_results} if retrieval_results else set()
    
    # 6b: Causal graph traversal
    # Find relevant causal chains based on metrics
    causal_chains = []
    # Determine which interventions might be relevant
    # Get chains connecting soil->biodiversity, water->species, land_use->habitat
    key_chains = [
        ("soil_organic_carbon", "species_richness"),
        ("rainfall", "species_survival"),
        ("land_use_intensification", "species_richness"),
    ]
    for start, end in key_chains:
        try:
            paths = get_causal_chain(start, end)
            for path in paths:
                causal_chains.append(render_chain_text(path))
        except Exception as e:
            logger.warning(f"Error getting causal chain {start}->{end}: {e}")
    
    # Also get intervention-specific chains
    for intervention in ["agroforestry", "intercropping", "cover_cropping"]:
        try:
            edges = get_edges_for_intervention(intervention)
            if edges:
                for edge in edges:
                    related = get_related_metrics(edge["target_metric"], depth=2)
                    if related:
                        causal_chains.append(f"Intervention {intervention} targets {edge['target_metric']} affecting {', '.join(related.keys())}")
        except Exception as e:
            logger.warning(f"Error getting edges for intervention {intervention}: {e}")
    
    # 6c: Structured table lookup
    table_data = []
    try:
        if "region" in merged_metrics:
            soc_data = lookup_structured_table("soc_benchmarks", {"biome": merged_metrics.get("region", "")})
            table_data.extend(soc_data)
        if "land_use_type" in merged_metrics or "crop" in merged_metrics:
            species_data = lookup_structured_table("species_richness", {})
            table_data.extend(species_data)
        if "rainfall" in merged_metrics:
            rainfall_data = lookup_structured_table("rainfall_biodiversity", {"rainfall_category": merged_metrics.get("rainfall", "")})
            table_data.extend(rainfall_data)
    except Exception as e:
        logger.warning(f"Error looking up structured tables: {e}")
    
    # 6d: Generate
    try:
        recommendations = generate_recommendations(
            query=query,
            retrieved_chunks=retrieved_chunks,
            causal_chains=causal_chains,
            table_data=table_data,
            user_metrics=merged_metrics,
            similarity_scores=similarity_scores,
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        recommendations = []
    
    response = EcoSageResponse(
        session_id=session_id,
        recommendations=recommendations,
        reasoning_trace={
            "retrieval_count": len(retrieval_results) if retrieval_results else 0,
            "causal_chains_used": causal_chains[:5],
            "table_lookups": len(table_data),
            "metrics_available": list(merged_metrics.keys()),
        }
    )
    
    # 6e-f: Validate with retries
    for attempt in range(MAX_RETRIES + 1):
        try:
            validation = validate_response(response, retrieved_source_ids)
            if validation.is_valid:
                break
            logger.warning(f"Validation failed (attempt {attempt+1}): {validation.errors}")
            if attempt < MAX_RETRIES:
                # Retry generation with stricter prompt
                recommendations = generate_recommendations(
                    query=query + "\n\nPREVIOUS ATTEMPT FAILED VALIDATION. Errors: " + str(validation.errors) + "\nBe MORE specific with citations, numbers, and causal mechanisms.",
                    retrieved_chunks=retrieved_chunks,
                    causal_chains=causal_chains,
                    table_data=table_data,
                    user_metrics=merged_metrics,
                    similarity_scores=similarity_scores,
                )
                response.recommendations = recommendations
        except Exception as e:
            logger.error(f"Validation step failed: {e}")
            break

    # 6g: Failsafe fallback if all LLM generation attempts yielded no recommendations
    if not response.recommendations:
        logger.warning("LLM generation produced no recommendations. Activating deterministic science failsafe...")
        response.recommendations = generate_failsafe_recommendations(merged_metrics, query)
        if response.reasoning_trace is None:
            response.reasoning_trace = {}
        response.reasoning_trace["failsafe_activated"] = True

    # Link retrieved chunks with the recommendations that cited them (FR-1.4 auditability)
    link_trace_to_recommendations(session_id, response.recommendations)

    # Attach retrieval evidence and current slots to reasoning trace for UI auditability
    if response.reasoning_trace is None:
        response.reasoning_trace = {}
    traces = get_retrieval_trace(session_id)
    if traces and traces[-1].results:
        response.reasoning_trace["retrieval_evidence"] = [
            r.model_dump() for r in traces[-1].results
        ]
    response.reasoning_trace["slots"] = dict(session["metrics"])

    # Store conversation turn
    session["conversation_history"].append({
        "query": input_data.query_text,
        "response_summary": [r.action for r in response.recommendations] if response.recommendations else []
    })

    return response
