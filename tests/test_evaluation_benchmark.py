"""
Evaluation Benchmark Suite for EcoSage (Darukaa.Earth Hackathon).

Tests ground-truth scientific alignment, causal graph density,
quantification precision, ecological trade-off coverage, and economic phasing.
"""
import pytest

from ecosage.failsafe import generate_failsafe_recommendations
from ecosage.models import EcoSageInput, EnvironmentalMetrics
from ecosage.orchestrator import process_input


class TestScientificGroundTruthBenchmark:
    """Evaluates recommendations against expert agronomist gold standards."""

    @pytest.fixture
    def section6_input(self):
        return EcoSageInput(
            session_id="benchmark-eval-sec6",
            metrics=EnvironmentalMetrics(
                soil_organic_carbon_pct=0.3,
                rainfall="low",
                crop="monoculture wheat",
                region="semi-arid",
                land_use_type="monoculture"
            ),
            query_text="Biodiversity is declining on my land. Recommend evidence-backed practices."
        )

    def test_benchmark_causal_density_and_metrics(self, section6_input):
        """Verify >=3 environmental metrics per recommendation."""
        res = process_input(section6_input)
        assert len(res.recommendations) > 0, "No recommendations produced"

        for rec in res.recommendations:
            assert len(rec.impacted_metrics) >= 3, (
                f"Recommendation '{rec.action}' only impacted {len(rec.impacted_metrics)} metrics (<3)"
            )
            assert len(rec.mechanism.split()) >= 20, "Mechanism explanation lacks scientific depth"

    def test_benchmark_tradeoff_coverage(self, section6_input):
        """Verify ecological trade-offs and risks are actively analyzed."""
        res = process_input(section6_input)
        for rec in res.recommendations:
            assert len(rec.ecological_tradeoffs) > 0, (
                f"Recommendation '{rec.action}' missing ecological trade-off analysis"
            )

    def test_benchmark_economic_feasibility_phasing(self, section6_input):
        """Verify economic feasibility and CapEx phasing are assessed."""
        res = process_input(section6_input)
        for rec in res.recommendations:
            assert rec.economic_feasibility, (
                f"Recommendation '{rec.action}' missing economic feasibility statement"
            )
            assert any(word in rec.economic_feasibility.lower() for word in ["capex", "roi", "cost", "investment", "return", "phased"]), (
                f"Feasibility lacks financial terminology: {rec.economic_feasibility}"
            )

    def test_benchmark_quantification_precision(self, section6_input):
        """Verify numeric impact estimates are present."""
        res = process_input(section6_input)
        for rec in res.recommendations:
            assert any(c.isdigit() for c in rec.quantified_estimate), (
                f"Recommendation '{rec.action}' lacks numeric quantification: {rec.quantified_estimate}"
            )

    def test_failsafe_engine_satisfies_all_benchmark_criteria(self):
        """Verify offline deterministic engine passes 100% of benchmark criteria."""
        user_metrics = {
            "soil_organic_carbon_pct": 0.3,
            "rainfall": "low",
            "crop": "monoculture wheat",
            "region": "semi-arid",
            "land_use_type": "monoculture"
        }
        recs = generate_failsafe_recommendations(user_metrics)
        assert len(recs) >= 2

        for rec in recs:
            # 1. Multi-metric >= 3
            assert len(rec.impacted_metrics) >= 3
            # 2. Citations
            assert len(rec.sources) >= 2
            # 3. Numeric quantification
            assert any(c.isdigit() for c in rec.quantified_estimate)
            # 4. Ecological trade-offs
            assert len(rec.ecological_tradeoffs) >= 1
            # 5. Economic feasibility
            assert "capex" in rec.economic_feasibility.lower() or "cost" in rec.economic_feasibility.lower()
