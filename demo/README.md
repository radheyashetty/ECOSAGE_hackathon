# ?? EcoSage System Demonstration Artifacts

This folder contains reproducible artifacts and scripts for evaluators and judges to review EcoSage in action without needing to run the full stack manually.

---

## ?? Walkthrough Animation
See [`walkthrough.gif`](walkthrough.gif) for an automated visual playback covering:
1. **Scenario A (PRD Section 6 Benchmark)**: Monoculture wheat in semi-arid conditions (0.3% SOC) receiving quantified agroforestry and intercropping recommendations with FAO/IPCC citations.
2. **Scenario B (Adversarial Vague Query)**: Slot-filling engine actively halting generation on incomplete input to request missing parameters.
3. **Scenario C (Novel Tropical Biome)**: Contour buffer and agroforestry recommendations with trade-offs and CapEx feasibility analysis.
4. **Publication-Grade Export**: 1-click Markdown advisory report generation.

---

## ?? Running the Scripted Terminal Walkthrough
To run the automated terminal demonstration directly:

```bash
python demo/run_demo.py
```

## ?? Re-generating the Walkthrough GIF
To re-generate the animated visual artifact:

```bash
python demo/generate_walkthrough_gif.py
```
