"""
EcoSage Reusable UI Components (Sections 1 to 10)
==================================================
Strict design adherence:
- No bold/700 font weight anywhere
- Strictly 4 semantic colors (Green, Amber, Red, Blue)
- Flat hairline cards, no shadows, no gradients
- Consistent SVG icons
- Zero-indent HTML rendering preventing markdown codeblock bug
"""
from __future__ import annotations

import html
from typing import Any, Callable

import streamlit as st

from ecosage.conversation import get_filled_categories
from ui.theme import (
    COLOR_ACCENT,
    COLOR_AMBER_TEXT,
    COLOR_BLUE_TEXT,
    COLOR_GREEN_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    get_svg_icon,
)


def render_header():
    """Section 1: App Shell / Header with live status indicators and repo link."""
    leaf_icon = get_svg_icon("leaf", COLOR_ACCENT, 20)
    dot_icon = get_svg_icon("dot", COLOR_GREEN_TEXT, 10)
    ext_icon = get_svg_icon("external-link", COLOR_ACCENT, 12)

    raw_html = f'''<div class="ecosage-top-bar">
<div class="ecosage-top-left">
<div class="ecosage-wordmark">{leaf_icon}<span>EcoSage</span></div>
<div class="ecosage-tagline">AI environmental scientist, not a chatbot</div>
</div>
<div class="ecosage-top-right">
<div class="ecosage-status-pill">{dot_icon}<span>60 passages indexed</span></div>
<div class="ecosage-status-pill">{dot_icon}<span>Gemini connected</span></div>
<a href="https://github.com/radheyashetty/ECOSAGE_hackathon" target="_blank" class="ecosage-link-pill"><span>GitHub</span>{ext_icon}</a>
</div>
</div>'''
    st.markdown(raw_html, unsafe_allow_html=True)


def render_landing_cards(on_select_example: Callable[[str, dict | None], None]):
    """Section 2: Landing / Empty State with 3 explainer cards and 3 1-click test scenarios."""
    book_icon = get_svg_icon("book", COLOR_ACCENT, 16)
    network_icon = get_svg_icon("network", COLOR_ACCENT, 16)
    shield_icon = get_svg_icon("shield", COLOR_ACCENT, 16)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'''<div class="explainer-card">
<div class="explainer-title">{book_icon} Grounded in FAO / IPCC</div>
<p class="explainer-desc">Indexed ChromaDB vector store with 60 vetted passages from FAO SOC guidelines, IPCC AR6 WGII, and peer-reviewed agroecology literature.</p>
</div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="explainer-card">
<div class="explainer-title">{network_icon} Multi-Metric Causal Graph</div>
<p class="explainer-desc">26-edge directed knowledge graph traversing soil organic carbon, moisture retention, canopy moderation, and species richness.</p>
</div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="explainer-card">
<div class="explainer-title">{shield_icon} Validated, Not Generic</div>
<p class="explainer-desc">Deterministic 9-rule scientific validator rejects unquantified claims, verifies time horizons, and enforces citations.</p>
</div>''', unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.caption("One-Click Evaluation Scenarios — Test the pipeline instantly:")

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("🌾 Semi-Arid Monoculture (Sec 6)", use_container_width=True):
            query = (
                "I manage a 25-hectare parcel in a semi-arid zone with 350 mm annual rainfall. "
                "Currently growing monoculture wheat. Soil test shows 0.3% soil organic carbon. "
                "Biodiversity is declining and I have noticed fewer pollinators."
            )
            metrics = {
                "soil_organic_carbon_pct": 0.3,
                "rainfall_mm_annual": 350.0,
                "rainfall": "low",
                "region": "semi-arid",
                "land_use_type": "monoculture",
                "crop": "monoculture wheat",
            }
            on_select_example(query, metrics)
    with btn_col2:
        if st.button("🌴 Tropical Humid Restoration", use_container_width=True):
            query = (
                "Tropical hillside parcel with 1200 mm rainfall, acidic soil (pH 5.5), and 1.2% SOC. "
                "Currently degraded cassava monoculture facing high water erosion and pollinator loss."
            )
            metrics = {
                "soil_organic_carbon_pct": 1.2,
                "soil_ph": 5.5,
                "rainfall_mm_annual": 1200.0,
                "rainfall": "high",
                "region": "tropical",
                "land_use_type": "degraded",
                "crop": "cassava",
            }
            on_select_example(query, metrics)
    with btn_col3:
        if st.button("❓ Adversarial Vague Input (Test)", use_container_width=True):
            query = "My soil is degraded, what should I do?"
            on_select_example(query, None)


def render_slot_panel(slots: dict[str, Any]):
    """Section 3: Input Slot Panel showing the 5 category pills and filling progress."""
    filled_set = get_filled_categories(slots)
    filled_count = len(filled_set)
    total_categories = 5
    progress_val = min(1.0, filled_count / float(total_categories))

    check_icon = get_svg_icon("circle-check", COLOR_GREEN_TEXT, 14)
    circle_icon = get_svg_icon("circle", COLOR_TEXT_MUTED, 14)
    db_icon = get_svg_icon("database", COLOR_TEXT_PRIMARY, 14)

    categories = [
        ("soil", "Soil", ["soil_organic_carbon_pct", "soil_ph", "soil_moisture_pct"]),
        ("land_use", "Land use", ["land_use_type", "crop"]),
        ("climate", "Climate", ["rainfall", "rainfall_mm_annual", "region"]),
        ("biodiversity", "Biodiversity", ["species_richness_index", "habitat_diversity_score"]),
        ("human_impact", "Human impact", ["pollution_index", "deforestation_rate_pct"]),
    ]

    pills_html = []
    for cat_id, cat_title, fields in categories:
        is_filled = cat_id in filled_set
        if is_filled:
            val_strs = []
            if cat_id == "soil":
                if "soil_organic_carbon_pct" in slots:
                    val_strs.append(f"SOC: {slots['soil_organic_carbon_pct']}%")
                if "soil_ph" in slots:
                    val_strs.append(f"pH: {slots['soil_ph']}")
            elif cat_id == "land_use":
                if "land_use_type" in slots:
                    val_strs.append(str(slots["land_use_type"]))
                elif "crop" in slots:
                    val_strs.append(str(slots["crop"]))
            elif cat_id == "climate":
                if "rainfall_mm_annual" in slots:
                    val_strs.append(f"{int(slots['rainfall_mm_annual'])}mm")
                elif "rainfall" in slots:
                    val_strs.append(str(slots["rainfall"]))
                if "region" in slots:
                    val_strs.append(str(slots["region"]))
            elif cat_id == "biodiversity":
                if "species_richness_index" in slots:
                    val_strs.append(f"SR: {slots['species_richness_index']}")
                else:
                    val_strs.append("Observed")
            elif cat_id == "human_impact":
                if "deforestation_rate_pct" in slots:
                    val_strs.append(f"Deforest: {slots['deforestation_rate_pct']}%")
                else:
                    val_strs.append("Recorded")

            summary = ", ".join(val_strs) if val_strs else "Provided"
            pills_html.append(
                f'<div class="slot-pill-filled">{check_icon}<span>{cat_title} — <span class="slot-pill-val">{html.escape(summary)}</span></span></div>'
            )
        else:
            pills_html.append(
                f'<div class="slot-pill-empty">{circle_icon}<span>{cat_title} — <span class="slot-pill-val">not yet provided</span></span></div>'
            )

    panel_html = f'''<div class="slots-container">
<div class="slots-header">
<div class="slots-header-title">{db_icon}<span>Environmental Input Slots</span></div>
<div class="slots-progress-label">{filled_count} of {total_categories} categories filled</div>
</div>
<div class="slots-row">
{"".join(pills_html)}
</div>
</div>'''
    st.markdown(panel_html, unsafe_allow_html=True)
    st.progress(progress_val)


def render_field_report_card(
    rec: dict[str, Any],
    rec_index: int,
    user_slots: dict[str, Any] | None = None,
    all_evidence: list[dict] | None = None,
    turn_index: int = 0
):
    """Sections 5 & 6: Recommendation Field Report Card with 'Why this matters' and expandable evidence."""
    confidence = rec.get("confidence", "Medium")
    is_low_conf = confidence.lower() == "low"
    time_horizon = rec.get("time_horizon", "medium").lower()

    if "short" in time_horizon:
        horizon_class = "badge-amber"
        horizon_label = "⏱️ < 1 yr (Short)"
    elif "long" in time_horizon:
        horizon_class = "badge-green"
        horizon_label = "⏱️ > 3 yr (Long)"
    else:
        horizon_class = "badge-green"
        horizon_label = "⏱️ 1-3 yr (Medium)"

    if is_low_conf:
        conf_class = "badge-red"
        conf_label = "● Low Confidence"
    elif confidence.lower() == "high":
        conf_class = "badge-green"
        conf_label = "● High Confidence"
    else:
        conf_class = "badge-amber"
        conf_label = "● Medium Confidence"

    quant_estimate = rec.get("quantified_estimate", "Quantitative uplift projected")
    capex_estimate = rec.get("economic_feasibility", "Moderate CapEx")

    why_matters = "Directly addresses reported ecosystem constraints with targeted scientific intervention."
    if user_slots:
        soc_val = user_slots.get("soil_organic_carbon_pct")
        rain_val = user_slots.get("rainfall_mm_annual") or user_slots.get("rainfall")
        crop_val = user_slots.get("crop")
        if soc_val is not None and soc_val < 1.0 and rain_val:
            why_matters = f"Directly reverses your reported {soc_val}% SOC depletion while mitigating {rain_val} moisture stress."
        elif soc_val is not None and soc_val < 1.0:
            why_matters = f"Targets your depleted {soc_val}% soil organic carbon through biological soil carbon sequestration."
        elif crop_val:
            why_matters = f"Breaks monoculture vulnerability in your {crop_val} system while bolstering natural pest predators."

    impacted_metrics = rec.get("impacted_metrics", [])
    causal_chips_html = []
    if impacted_metrics:
        nodes = ["Intervention"] + [m.replace("_", " ").title() for m in impacted_metrics]
        arrow_icon = get_svg_icon("arrow-right", COLOR_TEXT_MUTED, 12)
        for i, node in enumerate(nodes):
            causal_chips_html.append(f'<span class="causal-chip">{html.escape(node)}</span>')
            if i < len(nodes) - 1:
                causal_chips_html.append(f'<span class="causal-chip-arrow">{arrow_icon}</span>')

    card_class = "field-report-card-low-conf" if is_low_conf else "field-report-card"

    low_conf_banner_html = ""
    if is_low_conf:
        alert_icon = get_svg_icon("alert", COLOR_AMBER_TEXT, 14)
        low_conf_banner_html = f'<div class="low-conf-banner">{alert_icon}<span>Limited source agreement — treat as directional (Low confidence). Further on-site testing recommended.</span></div>'

    tradeoffs = rec.get("ecological_tradeoffs", [])
    tradeoffs_html = ""
    if tradeoffs:
        alert_icon = get_svg_icon("alert", COLOR_AMBER_TEXT, 14)
        list_items = "".join([f"<li>{html.escape(t)}</li>" for t in tradeoffs])
        tradeoffs_html = f'''<div class="tradeoffs-callout">
<div style="display:flex; align-items:center; gap:6px; font-weight:500;">{alert_icon}<span>Ecological Trade-offs & Management Precautions:</span></div>
<ul class="tradeoffs-list">{list_items}</ul>
</div>'''

    card_content = f'''<div class="{card_class}">
{low_conf_banner_html}
<div class="report-card-action">{rec_index + 1}. {html.escape(rec.get('action', 'Recommended Intervention'))}</div>
<div class="report-badges-row">
<span class="badge-semantic {horizon_class}">{horizon_label}</span>
<span class="badge-semantic {conf_class}">{conf_label}</span>
<span class="badge-semantic badge-green">📊 {html.escape(quant_estimate)}</span>
<span class="badge-semantic badge-neutral">💰 {html.escape(capex_estimate[:45])}</span>
</div>
<div class="why-this-matters"><strong>Why this matters:</strong> {html.escape(why_matters)}</div>
<div class="mechanism-block">{html.escape(rec.get('mechanism', ''))}</div>
<div class="causal-flow-container">
<div class="causal-flow-title">Traversed Causal Pathway:</div>
<div class="causal-flow-chips">{"".join(causal_chips_html)}</div>
</div>
{tradeoffs_html}
</div>'''
    st.markdown(card_content, unsafe_allow_html=True)

    sources = rec.get("sources", [])
    with st.expander(f"🔍 View Retrieval Detail ({len(sources)} citations / Grounded Evidence)", expanded=False):
        if not sources and not all_evidence:
            st.caption("No external retrieval documents were matched for this specific card.")
        else:
            matched_evidence = []
            rec_action = rec.get("action", "")
            if all_evidence:
                for ev in all_evidence:
                    sup = ev.get("supported_recommendation", "")
                    if sup and (rec_action in sup or sup in rec_action or "General" in sup):
                        matched_evidence.append(ev)
                if not matched_evidence:
                    matched_evidence = all_evidence[:3]

            if matched_evidence:
                st.markdown("<div style='font-size:13px; font-weight:500; margin-bottom:8px; color:#111827;'>Retrieved Knowledge Chunks (ChromaDB + Cosine Similarity):</div>", unsafe_allow_html=True)
                for ev in matched_evidence:
                    sim = ev.get("similarity_score", 0.0)
                    sim_pct = f"{sim:.3f}"
                    sim_badge_class = "badge-green" if sim >= 0.80 else ("badge-amber" if sim >= 0.65 else "badge-red")
                    st.markdown(f'''<div style="background:#FAFAFA; border:1px solid #E5E7EB; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
<div style="font-size:13px; font-weight:500; color:#111827;">📄 {html.escape(ev.get('source_name', 'Source Document'))} <span style="font-size:11px; color:#6B7280;">({html.escape(ev.get('source_id', 'doc'))})</span></div>
<span class="badge-semantic {sim_badge_class}">Cosine Sim: {sim_pct}</span>
</div>
<div style="font-size:12px; color:#4B5563; font-style:italic; line-height:1.4; margin-bottom:4px;">"{html.escape(ev.get('chunk_text', '')[:220])}..."</div>
<div style="font-size:11px; color:#1D4ED8;"><strong>Supports:</strong> {html.escape(ev.get('supported_recommendation') or rec_action)}</div>
</div>''', unsafe_allow_html=True)
            else:
                for s in sources:
                    st.markdown(f"- **{s.get('name', 'Unknown')}** (Document ID: `{s.get('id', 'N/A')}`)")


def render_clarifying_questions(
    questions: list[str],
    on_select_chip: Callable[[str, dict], None]
):
    """Section 4 & 9: Warm informational clarifying inquiry card with interactive chip selectors."""
    info_icon = get_svg_icon("info", COLOR_BLUE_TEXT, 18)

    st.markdown(f'''<div class="clarify-card">
<div class="clarify-title">{info_icon}<span>Additional Ecological Context Required</span></div>
<div class="clarify-prompt">To provide evidence-grounded scientific advice rather than generic rules of thumb, EcoSage requires additional field parameters:</div>
</div>''', unsafe_allow_html=True)

    for q in questions:
        st.markdown(f"- **{q}**")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    st.caption("Select a quick parameter chip or type your answer below:")

    q_text = " ".join(questions).lower()

    if "rainfall" in q_text:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Low Rainfall (< 400 mm/yr)", key="chip_rain_low"):
                on_select_chip("Rainfall is low (< 400 mm/yr)", {"rainfall": "low", "rainfall_mm_annual": 350.0})
        with col2:
            if st.button("Moderate Rainfall (400-800 mm)", key="chip_rain_mod"):
                on_select_chip("Rainfall is moderate (400-800 mm/yr)", {"rainfall": "moderate", "rainfall_mm_annual": 600.0})
        with col3:
            if st.button("High Rainfall (> 800 mm)", key="chip_rain_high"):
                on_select_chip("Rainfall is high (> 800 mm/yr)", {"rainfall": "high", "rainfall_mm_annual": 1100.0})

    elif "soil" in q_text or "carbon" in q_text or "ph" in q_text:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Low SOC (0.3%) & Neutral pH (7.0)", key="chip_soil_low"):
                on_select_chip("Soil test shows 0.3% SOC and pH 7.0", {"soil_organic_carbon_pct": 0.3, "soil_ph": 7.0})
        with col2:
            if st.button("Moderate SOC (1.2%) & Acidic pH (5.5)", key="chip_soil_mod"):
                on_select_chip("Soil test shows 1.2% SOC and pH 5.5", {"soil_organic_carbon_pct": 1.2, "soil_ph": 5.5})
        with col3:
            if st.button("Healthy SOC (2.5%) & Neutral pH (6.8)", key="chip_soil_high"):
                on_select_chip("Soil test shows 2.5% SOC and pH 6.8", {"soil_organic_carbon_pct": 2.5, "soil_ph": 6.8})

    elif "land" in q_text or "crop" in q_text:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Monoculture Wheat", key="chip_land_mono"):
                on_select_chip("Land use is monoculture wheat", {"land_use_type": "monoculture", "crop": "monoculture wheat"})
        with col2:
            if st.button("Degraded Pasture", key="chip_land_past"):
                on_select_chip("Land use is degraded pasture", {"land_use_type": "degraded", "crop": "pasture"})
        with col3:
            if st.button("Mixed Crop / Orchard", key="chip_land_mix"):
                on_select_chip("Land use is mixed cropping and orchard", {"land_use_type": "mixed_cropping", "crop": "orchard"})


def render_footer():
    """Section 10: Persistent footer with GitHub repo link and 7-stage architectural pipeline expander."""
    st.markdown('''<div class="ecosage-footer">
<div>EcoSage 🌿 | Darukaa.Earth AI Biodiversity Intelligence Challenge</div>
<div>Zero-Cost Free-Tier Guarantee (₹0.00)</div>
</div>''', unsafe_allow_html=True)

    with st.expander("ℹ️ How EcoSage Works — 7-Stage Architectural Pipeline (PRD Specification)", expanded=False):
        st.markdown("""
1. **Input Handler**: Heuristic regex parser + structured JSON schema validator extracting 5 critical ecological categories.
2. **Slot Validator & Clarifier**: Completeness checker; triggers targeted clarifying questions if fewer than 3 categories are filled.
3. **Vector Store Retrieval**: ChromaDB with Google `text-embedding-004` (60 indexed passages from FAO, IPCC AR6, 6 agroecology papers).
4. **Causal Knowledge Graph**: NetworkX directed multi-metric graph (26 source-tagged edges, 23 metrics) discovering non-obvious pathways.
5. **Structured Table Lookups**: Quantitative benchmark queries against FAO SOC benchmarks, species richness, and rainfall thresholds.
6. **Grounded Generator**: Multi-metric reasoning prompt with few-shot evidence synthesis and conservative temperature (0.1).
7. **Deterministic Output Validator**: 9-rule post-generation gatekeeper enforcing numerical estimates, citations, and confidence hedging.
""")
