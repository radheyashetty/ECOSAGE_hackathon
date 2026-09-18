"""
Post-generation output validation (PRD Section 5.3, FR-3.2).
This is critical for anti-hallucination.
"""
import re
from dataclasses import dataclass, field

from ecosage.models import EcoSageResponse, Recommendation

# Blocklist of generic/shallow phrases that should be rejected
GENERIC_BLOCKLIST = [
    "use sustainable practices",
    "go green",
    "be eco-friendly",
    "plant more trees",  # without specifics
    "reduce pollution",
    "save the environment",
    "practice sustainability",
    "be more environmentally conscious",
    "adopt green practices",
    "conserve natural resources",
]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

def validate_recommendation(rec: Recommendation, retrieved_source_ids: set[str]) -> ValidationResult:
    """Validate a single recommendation against quality criteria."""
    errors = []
    warnings = []
    
    # Check 1: Citation present - at least one source
    if not rec.sources or len(rec.sources) == 0:
        errors.append("Recommendation lacks sources. At least one source is required.")
        
    # Check 2: Quantification present - regex for numbers/percentages in quantified_estimate
    if not rec.quantified_estimate:
        errors.append("Quantified estimate is missing.")
    elif not re.search(r'\d', rec.quantified_estimate):
        errors.append(f"Quantified estimate '{rec.quantified_estimate}' does not contain any numbers.")
        
    # Check 3: Mechanism check - mechanism field contains substance (>20 words, mentions at least 2 metrics)
    if not rec.mechanism:
        errors.append("Mechanism is missing.")
    else:
        words = rec.mechanism.split()
        if len(words) < 15:
            errors.append("Mechanism is too short. It must be at least 15 words to establish a scientific causal mechanism.")
        elif len(words) <= 20:
            warnings.append("Mechanism is relatively brief. Consider describing additional causal steps.")
            
        # Check for metric mentions - use flexible matching
        # Strip common suffixes and convert underscores to spaces for matching
        mechanism_lower = rec.mechanism.lower()
        mentioned_count = 0
        for m in (rec.impacted_metrics or []):
            m_lower = m.lower()
            # Try exact match first
            if m_lower in mechanism_lower:
                mentioned_count += 1
                continue
            # Strip common suffixes and try again
            base_name = m_lower.replace("_pct", "").replace("_index", "").replace("_score", "").replace("_avg_c", "")
            # Convert underscores to spaces for natural language matching
            readable_name = base_name.replace("_", " ")
            if readable_name in mechanism_lower:
                mentioned_count += 1
                continue
            # Try individual words (at least 2 key words match)
            words = [w for w in base_name.split("_") if len(w) > 3]
            if sum(1 for w in words if w in mechanism_lower) >= min(2, len(words)):
                mentioned_count += 1
        
        if mentioned_count < 2:
            errors.append("Mechanism must explicitly mention at least 2 of the impacted metrics to establish causality.")
            
    # Check 4: Generic phrase blocklist - check action and mechanism against blocklist
    action_lower = (rec.action or "").lower()
    mech_lower = (rec.mechanism or "").lower()
    for phrase in GENERIC_BLOCKLIST:
        if phrase in action_lower:
            errors.append(f"Action contains generic blocklisted phrase: '{phrase}'")
        if phrase in mech_lower:
            errors.append(f"Mechanism contains generic blocklisted phrase: '{phrase}'")
            
    # Check 5: Cross-reference - cited source IDs must exist in retrieved context
    if rec.sources:
        for source in rec.sources:
            if getattr(source, 'id', None) not in retrieved_source_ids:
                errors.append(f"Source ID '{getattr(source, 'id', '')}' was cited but not found in retrieved context (hallucination risk).")
                
    # Check 6: Impacted metrics - at least 3 metrics listed
    if not rec.impacted_metrics or len(rec.impacted_metrics) < 3:
        errors.append("At least 3 impacted environmental metrics are required for complex causal chaining.")
        
    # Check 7: Time horizon is set
    if not rec.time_horizon:
        errors.append("Time horizon is missing.")
    elif rec.time_horizon not in ["short", "medium", "long"]:
        warnings.append(f"Time horizon '{rec.time_horizon}' is unconventional (should be short/medium/long).")
        
    # Check 8: Confidence level is set
    if not getattr(rec, 'confidence', None):
        warnings.append("Confidence level not set on recommendation.")
    elif getattr(rec, 'confidence', None) == "Low":
        # Check 9: Confidence calibration - Low confidence must not make unhedged assertive claims
        HEDGE_TERMS = [
            "preliminary", "provisional", "directional", "may", "suggests",
            "potential", "conditional", "further testing", "subject to",
            "investigate", "indicates", "explore", "consider"
        ]
        text_to_check = f"{rec.action} {rec.mechanism} {rec.quantified_estimate}".lower()
        has_hedge = any(term in text_to_check for term in HEDGE_TERMS)
        if not has_hedge:
            errors.append(
                "Low-confidence recommendation makes an assertive claim without required hedging or follow-up inquiry. "
                "Must include hedging language (e.g. 'preliminary', 'directional', 'may', 'suggests') or conditional guidance."
            )
        
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

def validate_response(response: EcoSageResponse, retrieved_source_ids: set[str]) -> ValidationResult:
    """Validate the full response and wire low-confidence follow-up questions."""
    errors = []
    warnings = []
    
    # If there are clarifying questions and no recommendations, that's valid
    has_questions = bool(getattr(response, "clarifying_questions", None))
    
    if not response.recommendations:
        if not has_questions:
            errors.append("Response contains neither recommendations nor clarifying questions.")
        else:
            warnings.append("Response contains clarifying questions but no recommendations.")
    else:
        # Validate each recommendation
        for i, rec in enumerate(response.recommendations):
            res = validate_recommendation(rec, retrieved_source_ids)
            for err in res.errors:
                errors.append(f"Rec {i+1}: {err}")
            for warn in res.warnings:
                warnings.append(f"Rec {i+1}: {warn}")

            # Wire low confidence to trigger a follow-up question/hedge
            if getattr(rec, 'confidence', None) == "Low":
                follow_up = f"Directional guidance note: '{rec.action}' carries low evidence confidence. Would you like to provide on-site soil analysis or local field observations to verify this intervention?"
                if follow_up not in response.clarifying_questions:
                    response.clarifying_questions.append(follow_up)
                
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

def compute_confidence(similarity_scores: list[float], source_count: int) -> str:
    """Rule-based confidence score per PRD Section 13b.
    
    High: avg similarity >= 0.80 AND >=2 independent sources agree
    Medium: avg similarity >= 0.65 AND >=1 source supports
    Low: avg similarity < 0.65 OR sources disagree/only 1 weak match
    """
    if not similarity_scores or source_count == 0:
        return "Low"
        
    avg_similarity = sum(similarity_scores) / len(similarity_scores)
    
    if avg_similarity >= 0.80 and source_count >= 2:
        return "High"
    elif avg_similarity >= 0.65 and source_count >= 1:
        return "Medium"
    else:
        return "Low"
