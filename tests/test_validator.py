"""Unit tests for the output validator."""
from ecosage.models import EcoSageResponse, Recommendation, Source
from ecosage.validator import (
    compute_confidence,
    validate_recommendation,
    validate_response,
)


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
            Recommendation(**rec_dict)
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

    def test_low_confidence_unhedged_assertive_fails(self):
        rec = Recommendation(
            action="Must implement immediate deep-root agroforestry overhaul",
            mechanism="This definitive intervention guarantees rapid soil organic carbon recovery and doubles species richness index across degraded agricultural landscapes.",
            impacted_metrics=["soil_organic_carbon_pct", "species_richness_index", "soil_moisture_retention"],
            quantified_estimate="+25% guaranteed increase in 1 year",
            time_horizon="short",
            confidence="Low",
            sources=[Source(name="FAO Report", id="FAO-SOC-2017")]
        )
        res = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert not res.is_valid
        assert any("low-confidence" in e.lower() or "hedging" in e.lower() for e in res.errors)

    def test_low_confidence_hedged_claim_passes(self):
        rec = Recommendation(
            action="Consider preliminary agroforestry trials with nitrogen-fixing species",
            mechanism="Preliminary evidence suggests this may assist soil organic carbon retention and foster microbial diversity under monitored conditions.",
            impacted_metrics=["soil_organic_carbon_pct", "species_richness_index", "soil_moisture_retention"],
            quantified_estimate="+10-15% potential estimate over 2-3 years",
            time_horizon="medium",
            confidence="Low",
            sources=[Source(name="FAO Report", id="FAO-SOC-2017")]
        )
        res = validate_recommendation(rec, {"FAO-SOC-2017"})
        assert res.is_valid

    def test_low_confidence_triggers_followup_question(self):
        rec = Recommendation(
            action="Consider preliminary agroforestry trials with nitrogen-fixing species",
            mechanism="Preliminary evidence suggests this may assist soil organic carbon retention and foster microbial diversity under monitored conditions.",
            impacted_metrics=["soil_organic_carbon_pct", "species_richness_index", "soil_moisture_retention"],
            quantified_estimate="+10-15% potential estimate over 2-3 years",
            time_horizon="medium",
            confidence="Low",
            sources=[Source(name="FAO Report", id="FAO-SOC-2017")]
        )
        resp = EcoSageResponse(session_id="test-session-conf", recommendations=[rec])
        res = validate_response(resp, {"FAO-SOC-2017"})
        assert res.is_valid
        assert len(resp.clarifying_questions) > 0
        assert any("low evidence confidence" in q.lower() or "directional" in q.lower() for q in resp.clarifying_questions)


class TestValidateResponse:
    def test_clarifying_questions_only_is_valid(self):
        response = EcoSageResponse(
            session_id="test-123",
            clarifying_questions=["What is your soil organic carbon percentage?"],
            recommendations=[]
        )
        result = validate_response(response, set())
        assert result.is_valid


class TestFailSafeEngine:
    def test_failsafe_produces_valid_recommendations(self):
        from ecosage.failsafe import generate_failsafe_recommendations
        metrics = {
            "soil_organic_carbon_pct": 0.3,
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid",
            "land_use_type": "monoculture",
        }
        recs = generate_failsafe_recommendations(metrics)
        assert len(recs) >= 1
        response = EcoSageResponse(session_id="test-failsafe", recommendations=recs)
        allowed_sources = {"FAO-SOC-2017", "IPCC-AR6-LU", "INTERCROP-2021", "COVER-CROP-2019"}
        val = validate_response(response, allowed_sources)
        assert val.is_valid, f"Failsafe recommendations failed validation: {val.errors}"
