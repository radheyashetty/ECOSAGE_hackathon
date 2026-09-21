"""
Deterministic fail-safe recommendation engine for EcoSage.

Activates when cloud LLM APIs are unreachable, experiencing rate limits,
or offline. Uses the local causal graph and structured benchmark tables
to produce grounded, validated recommendations without requiring external network calls.
"""
from typing import Any

from ecosage.causal_graph import get_causal_chain, render_chain_text
from ecosage.logger import get_logger
from ecosage.models import ConfidenceLevel, Recommendation, Source, TimeHorizon
from ecosage.retrieval import lookup_structured_table

logger = get_logger("failsafe")


def generate_failsafe_recommendations(
    user_metrics: dict[str, Any],
    query: str = ""
) -> list[Recommendation]:
    """Generate evidence-grounded recommendations deterministically using local tables and causal graph."""
    logger.info("🛡️ Fail-safe deterministic engine activated.")
    recommendations: list[Recommendation] = []

    soc = user_metrics.get("soil_organic_carbon_pct")
    rainfall = str(user_metrics.get("rainfall", "")).lower()
    crop = str(user_metrics.get("crop", "")).lower()
    region = str(user_metrics.get("region", "semi-arid")).lower()
    land_use = str(user_metrics.get("land_use_type", "monoculture")).lower()

    # Look up benchmark tables
    soc_data = lookup_structured_table("soc_benchmarks", {"biome": region})
    rain_data = lookup_structured_table("rainfall_biodiversity", {"rainfall_category": rainfall})

    typical_soc = 2.0
    if soc_data:
        typical_soc = soc_data[0].get("soc_pct_typical", 2.0)

    has_low_rain = "low" in rainfall or "arid" in region or bool(rain_data and "low" in rain_data[0].get("rainfall_category", ""))

    # 1. Agroforestry & Legume Intercropping (Primary for degraded / monoculture / low SOC)
    if (soc is not None and soc < typical_soc) or "monoculture" in land_use or "wheat" in crop:
        chain_paths = get_causal_chain("intercropping", "species_richness", max_depth=5)
        chain_narrative = (
            render_chain_text(chain_paths[0])
            if chain_paths
            else "intercropping → root diversity → soil organic carbon → microbial diversity → species richness"
        )

        water_note = (
            "Given low rainfall constraints in semi-arid zones, drought-tolerant legume species "
            "(e.g., chickpea, pigeonpea) with complementary root depths must be selected to optimize water use efficiency."
            if has_low_rain
            else "Crop diversity enhances root architecture and water infiltration."
        )

        rec = Recommendation(
            action="Introduce Agroforestry with Legume Intercropping and Drought-Adapted Trees",
            mechanism=(
                f"Implementing agroforestry and intercropping establishes diverse root architecture. "
                f"The causal progression ({chain_narrative}) increases subterranean organic matter deposition, "
                f"elevating soil organic carbon and stimulating microbial biomass, which drives nutrient cycling "
                f"and provides varied floral resources to recover pollinator diversity and overall species richness. {water_note}"
            ),
            impacted_metrics=[
                "soil_organic_carbon_pct",
                "species_richness_index",
                "microbial_diversity",
                "soil_moisture_retention"
            ],
            quantified_estimate="+15-25% SOC over 2-3 years and +30-50% pollinator diversity",
            time_horizon=TimeHorizon.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            sources=[
                Source(name="FAO Soil Organic Carbon Report", id="FAO-SOC-2017"),
                Source(name="IPCC AR6 Land Use Chapter", id="IPCC-AR6-LU"),
                Source(name="Intercropping Systems in Semi-Arid Regions", id="INTERCROP-2021")
            ],
            ecological_tradeoffs=[
                "Initial seedling water competition during dry season; requires synchronized planting dates.",
                "Sapling protection against grazing livestock required during first 18 months."
            ],
            economic_feasibility="Low-to-Medium CapEx; seed costs offset by reduced synthetic fertilizer within 2 seasons."
        )
        recommendations.append(rec)

    # 2. Permanent Cover Cropping & Mulching (for erosion prevention & moisture buffer)
    if "low" in rainfall or "moderate" in rainfall or (soc is not None and soc < 1.0):
        rec2 = Recommendation(
            action="Establish Permanent Organic Residue Mulching and Drought-Tolerant Cover Crops",
            mechanism=(
                "Maintaining biological surface cover reduces soil surface temperature and minimizes evaporative moisture loss. "
                "The decomposition of cover crop residue injects stable carbon into the upper soil profile, "
                "raising soil organic carbon and expanding mycorrhizal fungal networks, which directly extends plant water access "
                "and enhances flora and fauna survival under drought stress conditions."
            ),
            impacted_metrics=[
                "soil_organic_carbon_pct",
                "soil_moisture_retention",
                "species_survival",
                "microbial_diversity"
            ],
            quantified_estimate="+8-15% SOC increase over 3-5 years and 40-60% erosion reduction",
            time_horizon=TimeHorizon.MEDIUM,
            confidence=ConfidenceLevel.MEDIUM,
            sources=[
                Source(name="Cover Cropping Effects on Soil Health and Biodiversity", id="COVER-CROP-2019"),
                Source(name="FAO Soil Organic Carbon Report", id="FAO-SOC-2017")
            ],
            ecological_tradeoffs=[
                "Cover crop termination timing must be managed prior to primary crop sowing to prevent cash-crop moisture deficit.",
                "Residue management requires minimal seed drill or manual planting adjustments."
            ],
            economic_feasibility="Very Low CapEx; estimated payback within 6-12 months through moisture conservation and weed suppression."
        )
        recommendations.append(rec2)

    # Universal fallback guarantee: ensure at least one recommendation is always returned
    if not recommendations:
        chain_paths = get_causal_chain("intercropping", "species_richness", max_depth=5)
        chain_narrative = (
            render_chain_text(chain_paths[0])
            if chain_paths
            else "intercropping → root diversity → soil organic carbon → microbial diversity → species richness"
        )
        recommendations.append(
            Recommendation(
                action="Implement Diversified Agroecological Agroforestry and Legume Intercropping",
                mechanism=(
                    f"Integrating perennial woody species with nitrogen-fixing cover crops promotes subterranean root niche differentiation. "
                    f"The causal progression ({chain_narrative}) continuously deposits organic matter, "
                    f"stimulating mycorrhizal fungi and subterranean invertebrate biomass to rebuild multi-trophic biodiversity."
                ),
                impacted_metrics=[
                    "soil_organic_carbon_pct",
                    "species_richness_index",
                    "microbial_diversity",
                    "soil_moisture_retention"
                ],
                quantified_estimate="+15-25% SOC over 2-3 years and +30-50% pollinator diversity",
                time_horizon=TimeHorizon.MEDIUM,
                confidence=ConfidenceLevel.MEDIUM,
                sources=[
                    Source(name="FAO Soil Organic Carbon Report", id="FAO-SOC-2017"),
                    Source(name="IPCC AR6 Land Use Chapter", id="IPCC-AR6-LU"),
                    Source(name="Intercropping Systems in Semi-Arid Regions", id="INTERCROP-2021")
                ],
                ecological_tradeoffs=[
                    "Initial seedling water competition during dry season; requires synchronized planting dates.",
                    "Sapling protection against grazing livestock required during first 18 months."
                ],
                economic_feasibility="Low-to-Medium CapEx; seed costs offset by reduced synthetic fertilizer within 2 seasons."
            )
        )

    logger.info(f"🛡️ Fail-safe engine produced {len(recommendations)} validated recommendations.")
    return recommendations
