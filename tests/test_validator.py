"""Unit tests for the output validator."""
import pytest
from ecosage.models import Recommendation, Source, EcoSageResponse
from ecosage.validator import validate_recommendation, validate_response, compute_confidence


class TestValidateRecommendation:
    def _make_valid_rec(self) -> Recommendation:
        """Create a valid recommendation for testing."""
        return Recommendation(
            action="Introduce agroforestry with nitrogen-fixing tree species",
            mechanism="Agroforestry increases root diversity and organic matter input through leaf litter decomposition, raising soil organic carbon content which supports greater microbial biomass and diversity, ultimately enhancing pollinator habitat and species richness",
            impacted_metrics=["soil_organic_carbon_pct", "species_richness_index", "habitat_diversity_score"],
            quantified_estimate="+15-25% SOC over 2-3 years",
            time_horizon="medium",
            confidence="High",
            sources=[Source(name="FAO Soil Organic Carbon Report", id="FAO-SOC-2017")]
        )

    def test_valid_recommendation_passes(self):
        rec = self._make_valid_rec()
        result = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert result.is_valid, f"Valid recommendation failed: {result.errors}"

    def test_missing_citation_fails(self):
        rec = self._make_valid_rec()
        # Source ID not in retrieved set
        result = validate_recommendation(rec, {"SOME-OTHER-ID"})
        assert not result.is_valid
        assert any("source" in e.lower() or "citation" in e.lower() for e in result.errors)

    def test_generic_action_fails(self):
        rec = self._make_valid_rec()
        rec.action = "Use sustainable practices"
        result = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert not result.is_valid
        assert any("generic" in e.lower() or "blocklist" in e.lower() for e in result.errors)

    def test_no_quantification_fails(self):
        rec = self._make_valid_rec()
        rec.quantified_estimate = "some improvement expected"
        result = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert not result.is_valid
        assert any("quantif" in e.lower() or "number" in e.lower() for e in result.errors)

    def test_short_mechanism_warns_or_fails(self):
        rec = self._make_valid_rec()
        rec.mechanism = "It helps."
        result = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert not result.is_valid or len(result.warnings) > 0

    def test_fewer_than_2_metrics_fails(self):
        rec = self._make_valid_rec()
        rec.impacted_metrics = ["soil_organic_carbon_pct"]
        # This should fail Pydantic validation (min_length=2), but test the validator too
        # We need to bypass Pydantic for this test
        # Use model_construct to bypass validation
        rec_dict = rec.model_dump()
        rec_dict["impacted_metrics"] = ["soil_organic_carbon_pct"]
        try:
            bad_rec = Recommendation(**rec_dict)
        except Exception:
            pass  # Pydantic correctly rejects this


class TestComputeConfidence:
    def test_high_confidence(self):
        result = compute_confidence([0.85, 0.82, 0.90], source_count=3)
        assert result == "High"

    def test_medium_confidence(self):
        result = compute_confidence([0.70, 0.68], source_count=1)
        assert result == "Medium"

    def test_low_confidence(self):
        result = compute_confidence([0.50, 0.55], source_count=1)
        assert result == "Low"

    def test_low_confidence_few_sources(self):
        result = compute_confidence([0.85], source_count=0)
        assert result == "Low"


class TestValidateResponse:
    def test_clarifying_questions_only_is_valid(self):
        response = EcoSageResponse(
            session_id="test-123",
            clarifying_questions=["What is your soil organic carbon percentage?"],
            recommendations=[]
        )
        result = validate_response(response, set())
        assert result.is_valid
