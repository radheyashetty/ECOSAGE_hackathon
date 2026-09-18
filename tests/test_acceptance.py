"""Acceptance test matching PRD Section 6.

This test requires:
- GOOGLE_API_KEY environment variable set
- ChromaDB knowledge base ingested

Run with: pytest tests/test_acceptance.py -v -m acceptance
"""
import pytest
from ecosage.models import EcoSageInput, EnvironmentalMetrics, EcoSageResponse
from ecosage.orchestrator import process_input

pytestmark = pytest.mark.acceptance


class TestSection6Acceptance:
    """PRD Section 6: the primary acceptance test scenario."""

    @pytest.fixture(scope="class")
    def section6_response(self) -> EcoSageResponse:
        input_data = EcoSageInput(
            session_id="acceptance-test-cached",
            metrics=EnvironmentalMetrics(
                soil_organic_carbon_pct=0.3,
                rainfall="low",
                crop="monoculture wheat",
                region="semi-arid",
                land_use_type="monoculture",
            ),
            query_text="Biodiversity is declining on my land. What agroforestry or intercropping practices should I use to restore soil organic carbon?",
        )
        return process_input(input_data)

    def test_produces_recommendations(self, section6_response):
        """System should produce recommendations, not clarifying questions."""
        assert len(section6_response.recommendations) > 0, "No recommendations generated"
        assert len(section6_response.clarifying_questions) == 0, "Should not ask clarifying questions when input is sufficient"

    def test_recommends_agroforestry_or_intercropping(self, section6_response):
        """Should recommend agroforestry and/or intercropping."""
        all_text = " ".join([
            f"{r.action} {r.mechanism}"
            for r in section6_response.recommendations
        ]).lower()
        assert "agroforestry" in all_text or "intercropping" in all_text, \
            f"Expected agroforestry/intercropping recommendation, got: {all_text}"

    def test_quantifies_soc_impact(self, section6_response):
        """Should quantify SOC increase."""
        all_estimates = " ".join([r.quantified_estimate for r in section6_response.recommendations])
        assert "%" in all_estimates or "percent" in all_estimates.lower() or "t/ha" in all_estimates.lower(), \
            f"No quantified estimate found: {all_estimates}"

    def test_cites_fao_or_ipcc(self, section6_response):
        """Should cite FAO or IPCC sources."""
        all_source_ids = []
        for rec in section6_response.recommendations:
            all_source_ids.extend([s.id for s in rec.sources])
        source_str = " ".join(all_source_ids).upper()
        assert "FAO" in source_str or "IPCC" in source_str, \
            f"Expected FAO/IPCC citation, got: {all_source_ids}"

    def test_links_at_least_3_metrics(self, section6_response):
        """Hard constraint: >=3 environmental variables per recommendation."""
        for rec in section6_response.recommendations:
            assert len(rec.impacted_metrics) >= 3, \
                f"Recommendation '{rec.action}' only links {len(rec.impacted_metrics)} metrics: {rec.impacted_metrics}"

    def test_flags_low_rainfall_constraint(self, section6_response):
        """Should mention low rainfall or water as a constraint."""
        all_text = " ".join([
            f"{r.action} {r.mechanism}"
            for r in section6_response.recommendations
        ]).lower()
        assert any(word in all_text for word in ["rainfall", "water", "drought", "moisture", "arid"]), \
            "Should flag low rainfall or water as a constraint"


class TestAdversarialInput:
    """Test that vague inputs trigger clarifying questions."""

    def test_vague_input_asks_questions(self):
        """Adversarially vague input should trigger clarifying questions."""
        vague_input = EcoSageInput(
            session_id="adversarial-test-001",
            query_text="Help my land",
        )
        response = process_input(vague_input)
        assert len(response.clarifying_questions) > 0, \
            "Vague input should trigger clarifying questions"
        assert len(response.recommendations) == 0, \
            "Should NOT generate recommendations from vague input"
