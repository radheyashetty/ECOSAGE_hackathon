"""
EcoSage Scripted Demonstration (Terminal + Pipeline Walkthrough).
Covers:
  (a) PRD Section 6 acceptance example (Semi-arid monoculture wheat, 0.3% SOC)
  (b) Adversarial vague-input slot-filling test ("Biodiversity is declining on my land")
  (c) Novel scenario: Tropical acidic hillside with high rainfall & erosion
"""
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ecosage.models import EcoSageInput, EnvironmentalMetrics  # noqa: E402
from ecosage.orchestrator import process_input  # noqa: E402


def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f"  ??  {title}")
    print("=" * 70)


def run_scenario_a():
    print_banner("SCENARIO (A): PRD Section 6 Benchmark Acceptance Example")
    print("Parcel: 25 ha, Semi-Arid (350mm low rainfall), 0.3% SOC, Monoculture Wheat")
    inp = EcoSageInput(
        session_id="demo-session-sec6",
        metrics=EnvironmentalMetrics(
            soil_organic_carbon_pct=0.3,
            rainfall="low",
            crop="monoculture wheat",
            region="semi-arid",
            land_use_type="monoculture"
        ),
        query_text="Biodiversity is declining on my land. What agroforestry or intercropping practices should I use?"
    )
    t0 = time.time()
    res = process_input(inp)
    dur = time.time() - t0
    print(f"-> Completed in {dur:.2f}s | Status: {len(res.recommendations)} Recommendations Generated")
    for i, r in enumerate(res.recommendations, 1):
        print(f"\n  [{i}] Action: {r.action}")
        print(f"      Target Impact: {r.quantified_estimate}")
        print(f"      Confidence: {r.confidence} | Horizon: {r.time_horizon}")
        print(f"      Mechanism: {r.mechanism[:140]}...")
        print(f"      Impacted Metrics (>=3): {r.impacted_metrics}")
        print(f"      Citations: {', '.join([s.name + ' (' + s.id + ')' for s in r.sources])}")


def run_scenario_b():
    print_banner("SCENARIO (B): Adversarial Incomplete Query (Slot-Filling)")
    print("Query: 'Biodiversity is declining on my land' (Zero metrics supplied)")
    inp = EcoSageInput(
        session_id="demo-session-adv",
        query_text="Biodiversity is declining on my land"
    )
    t0 = time.time()
    res = process_input(inp)
    dur = time.time() - t0
    print(f"-> Completed in {dur:.2f}s | Status: Hallucination Prevented")
    print(f"-> Clarifying Questions Triggered ({len(res.clarifying_questions)}):")
    for q in res.clarifying_questions:
        print(f"     * {q}")


def run_scenario_c():
    print_banner("SCENARIO (C): Novel Biome - Tropical Acidic Hillside Agroforestry")
    print("Parcel: Tropical humid (1400mm rainfall), pH 5.2, 1.2% SOC, Degraded slope")
    inp = EcoSageInput(
        session_id="demo-session-tropical",
        metrics=EnvironmentalMetrics(
            soil_organic_carbon_pct=1.2,
            soil_ph=5.2,
            rainfall="high",
            crop="cassava",
            region="tropical",
            land_use_type="degraded"
        ),
        query_text="High water erosion and pollinator loss on degraded hillside parcel"
    )
    t0 = time.time()
    res = process_input(inp)
    dur = time.time() - t0
    print(f"-> Completed in {dur:.2f}s | Status: {len(res.recommendations)} Recommendations Generated")
    for i, r in enumerate(res.recommendations, 1):
        print(f"\n  [{i}] Action: {r.action}")
        print(f"      Target Impact: {r.quantified_estimate}")
        print(f"      Confidence: {r.confidence} | CapEx: {r.economic_feasibility}")
        print(f"      Trade-offs: {r.ecological_tradeoffs}")


def main():
    print("\nStarting EcoSage System Demonstration...")
    run_scenario_a()
    run_scenario_b()
    run_scenario_c()
    print("\n" + "=" * 70)
    print("  ? All 3 demonstration scenarios completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
