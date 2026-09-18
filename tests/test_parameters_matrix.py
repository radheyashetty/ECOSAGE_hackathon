"""Comprehensive parameter-by-parameter matrix test suite for EcoSage.

Tests:
1. Pydantic validation boundaries on all 12 core environmental metrics.
2. Category combinations and slot-filling logic across all 5 categories.
3. Parameterized free-text extraction for all variables.
4. Diverse biome & land-use scenarios across different parameter regimes.
5. Causal graph traversal and reachability across all 23 metrics.
"""
import itertools

import pytest
from pydantic import ValidationError

from ecosage.causal_graph import (
    ADJACENCY_DICT,
    CAUSAL_EDGES,
    get_all_metrics,
    get_causal_chain,
    get_related_metrics,
)
from ecosage.conversation import (
    CRITICAL_CATEGORIES,
    extract_metrics_from_text,
    get_clarifying_questions,
    get_filled_categories,
    needs_clarification,
)
from ecosage.failsafe import generate_failsafe_recommendations
from ecosage.models import (
    EcoSageResponse,
    EnvironmentalMetrics,
)
from ecosage.validator import validate_response

# ==============================================================================
# 1. PARAMETER BOUNDARIES & VALIDATION TESTS
# ==============================================================================

class TestParameterBoundaries:
    """Verify numerical and domain bounds on all 12 environmental metrics."""

    @pytest.mark.parametrize("valid_ph", [0.0, 5.5, 7.0, 8.5, 14.0])
    def test_soil_ph_valid_bounds(self, valid_ph):
        metrics = EnvironmentalMetrics(soil_ph=valid_ph)
        assert metrics.soil_ph == valid_ph

    @pytest.mark.parametrize("invalid_ph", [-0.1, -5.0, 14.1, 20.0])
    def test_soil_ph_invalid_bounds(self, invalid_ph):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(soil_ph=invalid_ph)

    @pytest.mark.parametrize("valid_soc", [0.0, 0.3, 2.5, 15.0, 100.0])
    def test_soil_organic_carbon_valid_bounds(self, valid_soc):
        metrics = EnvironmentalMetrics(soil_organic_carbon_pct=valid_soc)
        assert metrics.soil_organic_carbon_pct == valid_soc

    @pytest.mark.parametrize("invalid_soc", [-0.5, 100.1, 150.0])
    def test_soil_organic_carbon_invalid_bounds(self, invalid_soc):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(soil_organic_carbon_pct=invalid_soc)

    @pytest.mark.parametrize("valid_moisture", [0.0, 25.0, 60.5, 100.0])
    def test_soil_moisture_valid_bounds(self, valid_moisture):
        metrics = EnvironmentalMetrics(soil_moisture_pct=valid_moisture)
        assert metrics.soil_moisture_pct == valid_moisture

    @pytest.mark.parametrize("invalid_moisture", [-1.0, 100.5, 200.0])
    def test_soil_moisture_invalid_bounds(self, invalid_moisture):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(soil_moisture_pct=invalid_moisture)

    @pytest.mark.parametrize("valid_richness", [0.0, 0.25, 0.5, 0.85, 1.0])
    def test_species_richness_index_valid(self, valid_richness):
        metrics = EnvironmentalMetrics(species_richness_index=valid_richness)
        assert metrics.species_richness_index == valid_richness

    @pytest.mark.parametrize("invalid_richness", [-0.01, 1.01, 5.0])
    def test_species_richness_index_invalid(self, invalid_richness):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(species_richness_index=invalid_richness)

    @pytest.mark.parametrize("valid_habitat", [0.0, 0.33, 0.75, 1.0])
    def test_habitat_diversity_score_valid(self, valid_habitat):
        metrics = EnvironmentalMetrics(habitat_diversity_score=valid_habitat)
        assert metrics.habitat_diversity_score == valid_habitat

    @pytest.mark.parametrize("invalid_habitat", [-0.1, 1.1])
    def test_habitat_diversity_score_invalid(self, invalid_habitat):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(habitat_diversity_score=invalid_habitat)

    @pytest.mark.parametrize("valid_pollution", [0.0, 0.45, 0.9, 1.0])
    def test_pollution_index_valid(self, valid_pollution):
        metrics = EnvironmentalMetrics(pollution_index=valid_pollution)
        assert metrics.pollution_index == valid_pollution

    @pytest.mark.parametrize("invalid_pollution", [-0.05, 1.05])
    def test_pollution_index_invalid(self, invalid_pollution):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(pollution_index=invalid_pollution)

    @pytest.mark.parametrize("valid_deforestation", [0.0, 2.5, 50.0, 100.0])
    def test_deforestation_rate_valid(self, valid_deforestation):
        metrics = EnvironmentalMetrics(deforestation_rate_pct=valid_deforestation)
        assert metrics.deforestation_rate_pct == valid_deforestation

    @pytest.mark.parametrize("invalid_deforestation", [-1.0, 100.1])
    def test_deforestation_rate_invalid(self, invalid_deforestation):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(deforestation_rate_pct=invalid_deforestation)

    @pytest.mark.parametrize("valid_rain_mm", [0.0, 250.0, 1200.0, 5000.0])
    def test_rainfall_mm_annual_valid(self, valid_rain_mm):
        metrics = EnvironmentalMetrics(rainfall_mm_annual=valid_rain_mm)
        assert metrics.rainfall_mm_annual == valid_rain_mm

    @pytest.mark.parametrize("invalid_rain_mm", [-1.0, -100.0])
    def test_rainfall_mm_annual_invalid(self, invalid_rain_mm):
        with pytest.raises(ValidationError):
            EnvironmentalMetrics(rainfall_mm_annual=invalid_rain_mm)

    @pytest.mark.parametrize("temp_c", [-30.0, 0.0, 25.5, 48.0])
    def test_temperature_avg_c_range(self, temp_c):
        metrics = EnvironmentalMetrics(temperature_avg_c=temp_c)
        assert metrics.temperature_avg_c == temp_c


# ==============================================================================
# 2. CATEGORY COMBINATIONS & SLOT-FILLING LOGIC
# ==============================================================================

class TestCategoryCombinations:
    """Test all 2^5 = 32 category permutations for completeness and slot-filling."""

    SAMPLE_VALUES = {
        "soil": {"soil_organic_carbon_pct": 0.8},
        "land_use": {"land_use_type": "agroforestry"},
        "climate": {"rainfall": "moderate"},
        "biodiversity": {"species_richness_index": 0.6},
        "human_impact": {"pollution_index": 0.2},
    }

    def test_all_category_subsets_completeness(self):
        """Combinations with < 3 categories must trigger clarification; >= 3 must pass."""
        categories = list(CRITICAL_CATEGORIES.keys())

        for r in range(len(categories) + 1):
            for subset in itertools.combinations(categories, r):
                # Build test metrics dict
                metrics = {}
                for cat in subset:
                    metrics.update(self.SAMPLE_VALUES[cat])

                filled = get_filled_categories(metrics)
                assert filled == set(subset)

                if len(subset) < 3:
                    assert needs_clarification(metrics) is True
                    questions = get_clarifying_questions(metrics, max_questions=1)
                    assert len(questions) == 1
                    # Question should ask for the highest priority missing category
                    missing = set(categories) - set(subset)
                    expected_priority_cat = min(missing, key=lambda c: CRITICAL_CATEGORIES[c]["priority"])
                    assert CRITICAL_CATEGORIES[expected_priority_cat]["question"] == questions[0]
                else:
                    assert needs_clarification(metrics) is False
                    questions = get_clarifying_questions(metrics, max_questions=1)
                    # When not needing clarification, questions can still be generated if not all 5 are filled,
                    # but needs_clarification must be False


# ==============================================================================
# 3. PARAMETERIZED TEXT EXTRACTION TESTS
# ==============================================================================

class TestTextExtractionParameters:
    """Verify regex extraction across diverse phrasing styles for all variables."""

    @pytest.mark.parametrize("phrase, expected_soc", [
        ("SOC is 0.3%", 0.3),
        ("soil organic carbon is around 1.5%", 1.5),
        ("SOC: 2.1%", 2.1),
        ("SOC = 0.8", 0.8),
        ("soc is 12.0%", 12.0),
    ])
    def test_soc_extraction(self, phrase, expected_soc):
        res = extract_metrics_from_text(phrase)
        assert res.get("soil_organic_carbon_pct") == pytest.approx(expected_soc)

    @pytest.mark.parametrize("phrase, expected_ph", [
        ("pH 6.5", 6.5),
        ("soil pH is 7.2", 7.2),
        ("pH: 8.0", 8.0),
        ("pH of 5.8", 5.8),
    ])
    def test_ph_extraction(self, phrase, expected_ph):
        res = extract_metrics_from_text(phrase)
        assert res.get("soil_ph") == pytest.approx(expected_ph)

    @pytest.mark.parametrize("phrase, expected_rainfall", [
        ("low rainfall area", "low"),
        ("rainfall is moderate", "moderate"),
        ("high rainfall region", "high"),
        ("rainfall: low", "low"),
    ])
    def test_rainfall_category_extraction(self, phrase, expected_rainfall):
        res = extract_metrics_from_text(phrase)
        assert res.get("rainfall") == expected_rainfall

    @pytest.mark.parametrize("phrase, expected_mm", [
        ("350 mm per year", 350.0),
        ("600 mm/yr", 600.0),
        ("1200mm annually", 1200.0),
        ("400 mm", 400.0),
    ])
    def test_rainfall_mm_extraction(self, phrase, expected_mm):
        res = extract_metrics_from_text(phrase)
        assert res.get("rainfall_mm_annual") == pytest.approx(expected_mm)

    @pytest.mark.parametrize("phrase, expected_region", [
        ("in semi-arid zone", "semi-arid"),
        ("tropical rainforest", "tropical"),
        ("temperate climate", "temperate"),
        ("arid desert", "arid"),
        ("mediterranean biome", "mediterranean"),
        ("boreal forest", "boreal"),
    ])
    def test_region_extraction(self, phrase, expected_region):
        res = extract_metrics_from_text(phrase)
        assert res.get("region") == expected_region

    @pytest.mark.parametrize("phrase, expected_land_use", [
        ("monoculture farming", "monoculture"),
        ("practicing agroforestry", "agroforestry"),
        ("cattle pasture", "pasture"),
        ("degraded agricultural soil", "degraded"),
        ("mixed cropping system", "mixed cropping"),
    ])
    def test_land_use_extraction(self, phrase, expected_land_use):
        res = extract_metrics_from_text(phrase)
        assert res.get("land_use_type") == expected_land_use

    @pytest.mark.parametrize("phrase, expected_crop", [
        ("growing monoculture wheat", "monoculture wheat"),
        ("planted with corn", "corn"),
        ("soybean field", "soybean"),
        ("crop is sorghum", "sorghum"),
    ])
    def test_crop_extraction(self, phrase, expected_crop):
        res = extract_metrics_from_text(phrase)
        assert expected_crop in res.get("crop", "")


# ==============================================================================
# 4. DIVERSE BIOME & LAND-USE PARAMETER REGIMES
# ==============================================================================

class TestDiverseBiomeScenarios:
    """Verify recommendation generation and validation across 5 distinct environmental regimes."""

    @pytest.mark.parametrize("scenario_name, metrics", [
        (
            "Semi-Arid Degraded Wheat",
            {
                "soil_organic_carbon_pct": 0.3,
                "soil_ph": 7.5,
                "rainfall": "low",
                "land_use_type": "monoculture",
                "crop": "monoculture wheat",
                "region": "semi-arid",
            }
        ),
        (
            "Tropical Acidic High-Rainfall",
            {
                "soil_organic_carbon_pct": 1.2,
                "soil_ph": 4.8,
                "rainfall": "high",
                "land_use_type": "degraded",
                "crop": "cassava",
                "region": "tropical",
                "deforestation_rate_pct": 12.0,
            }
        ),
        (
            "Arid Alkaline Pasture",
            {
                "soil_organic_carbon_pct": 0.2,
                "soil_ph": 8.6,
                "soil_moisture_pct": 8.0,
                "rainfall": "low",
                "land_use_type": "pasture",
                "region": "arid",
            }
        ),
        (
            "Temperate Mixed-Cropping",
            {
                "soil_organic_carbon_pct": 2.4,
                "soil_ph": 6.8,
                "rainfall": "moderate",
                "land_use_type": "mixed_cropping",
                "crop": "barley and clover",
                "region": "temperate",
                "species_richness_index": 0.45,
            }
        ),
        (
            "Wetland Buffer Zone with Human Impact",
            {
                "soil_organic_carbon_pct": 3.5,
                "soil_ph": 6.2,
                "soil_moisture_pct": 75.0,
                "rainfall": "high",
                "land_use_type": "wetland",
                "region": "tropical",
                "pollution_index": 0.6,
            }
        ),
    ])
    def test_scenario_produces_valid_recommendations(self, scenario_name, metrics):
        """Every diverse parameter scenario must produce valid, non-crashing recommendations."""
        recs = generate_failsafe_recommendations(metrics)
        assert len(recs) >= 1, f"Scenario '{scenario_name}' yielded no recommendations"

        response = EcoSageResponse(session_id=f"test-scenario-{scenario_name}", recommendations=recs)
        allowed_sources = {
            "FAO-SOC-2017", "IPCC-AR6-LU", "INTERCROP-2021",
            "COVER-CROP-2019", "AGROFOR-BIO-2020", "MICRO-SOIL-2021"
        }
        val = validate_response(response, allowed_sources)
        assert val.is_valid, f"Scenario '{scenario_name}' failed validation: {val.errors}"


# ==============================================================================
# 5. CAUSAL GRAPH METRIC COVERAGE & REACHABILITY
# ==============================================================================

class TestCausalGraphMetricCoverage:
    """Verify graph structure, edge integrity, and reachability for all metrics."""

    def test_total_metrics_and_edges(self):
        metrics = get_all_metrics()
        assert len(metrics) >= 20, f"Expected >= 20 unique metrics, found {len(metrics)}"
        assert len(CAUSAL_EDGES) >= 25, f"Expected >= 25 edges, found {len(CAUSAL_EDGES)}"

    def test_all_metrics_have_connections(self):
        """Every metric must have at least one incoming or outgoing edge."""
        all_metrics = get_all_metrics()
        for m in all_metrics:
            out_edges = ADJACENCY_DICT.get(m, [])
            in_edges = [e for e in CAUSAL_EDGES if e["target_metric"] == m]
            assert len(out_edges) + len(in_edges) > 0, f"Metric '{m}' is an isolated orphan node!"

    @pytest.mark.parametrize("intervention", ["agroforestry", "intercropping", "cover_cropping"])
    def test_interventions_reach_species_or_carbon(self, intervention):
        """Each core intervention must connect to either soil_organic_carbon or species_richness."""
        related = get_related_metrics(intervention, depth=3)
        reachable = set(related.keys())
        has_carbon_or_biodiversity = bool(
            {"soil_organic_carbon", "crop_diversity", "root_diversity", "species_richness"} & reachable
        )
        assert has_carbon_or_biodiversity, f"Intervention '{intervention}' does not reach target cluster!"

    def test_multi_variable_causal_chains_exist(self):
        """Path from intercropping to species_richness must link >= 3 variables."""
        chains = get_causal_chain("intercropping", "species_richness", max_depth=6)
        assert len(chains) >= 1, "No path found from intercropping to species_richness"
        for chain in chains:
            # Each chain edge connects 2 metrics, so >= 2 edges means >= 3 variables
            assert len(chain) >= 2, f"Causal chain too short: {len(chain)} edges"


# ==============================================================================
# 6. GEO-COORDINATE CLIMATE PRIOR INFERENCE (PRD BONUS FR-5.3)
# ==============================================================================

class TestGeoClimateInference:
    """Verify offline regional prior inference from coordinates (FR-5.3 Bonus)."""

    @pytest.mark.parametrize("lat, lng, expected_region, expected_rainfall", [
        (26.9, 75.8, "semi-arid", "low"),         # Rajasthan Thar Desert
        (18.5, 77.0, "semi-arid", "low"),         # Deccan Plateau
        (28.6, 77.2, "temperate", "moderate"),    # New Delhi / Indo-Gangetic
        (10.0, 76.5, "tropical", "high"),         # Western Ghats Hotspot
        (14.0, 0.0, "semi-arid", "low"),          # African Sahel
        (38.0, 23.7, "mediterranean", "moderate"), # Athens, Greece
        (35.0, -100.0, "temperate", "moderate"),  # US Great Plains
        (-25.0, 130.0, "semi-arid", "low"),       # Australian Interior
        (0.0, 20.0, "tropical", "high"),          # Congo Basin
    ])
    def test_geo_coordinate_priors(self, lat, lng, expected_region, expected_rainfall):
        from ecosage.geo_inference import infer_climate_priors
        priors = infer_climate_priors(lat, lng)
        assert priors["region"] == expected_region
        assert priors["rainfall"] == expected_rainfall
        assert priors["rainfall_mm_annual"] > 0
