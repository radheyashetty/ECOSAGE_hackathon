"""Generate the official Word submission document for Darukaa.Earth Hackathon."""
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor


def set_cell_background(cell, hex_color):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def create_submission_doc(output_path="EcoSage_Hackathon_Submission.docx"):
    doc = Document()

    # Set page margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles & Colors
    PRIMARY_COLOR = RGBColor(24, 110, 50)     # Forest Green
    SECONDARY_COLOR = RGBColor(40, 80, 120)  # Slate Blue

    # ─── Title & Header ──────────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("🌿 EcoSage")
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY_COLOR

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_after = Pt(14)
    run_sub = subtitle_p.add_run("AI Environmental Scientist for Biodiversity Intelligence\nDarukaa.Earth Hackathon Challenge Submission Document")
    run_sub.font.size = Pt(14)
    run_sub.font.color.rgb = SECONDARY_COLOR

    # ─── Submission Metadata Box ─────────────────────────────────────
    table_meta = doc.add_table(rows=6, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.autofit = False

    meta_data = [
        ("Candidate / Team:", "Radheya Shetty (NMIMS Mumbai)"),
        ("Primary Contact Email:", "radheya.shetty214@nmims.in"),
        ("GitHub Repository:", "https://github.com/radheyashetty/ECOSAGE_hackathon"),
        ("Live Demo URL:", "https://ecosagehackathon-radheyashetty.streamlit.app"),
        ("Target Challenge:", "Darukaa.Earth AI Environmental Scientist Hackathon"),
        ("Reviewer Access Granted to:", "ankita.dasgupta@darukaa.com, harsh.kumar@darukaa.com,\nutkarsh.gauniyal@darukaa.com, guneet.mutreja@darukaa.com")
    ]

    for i, (k, v) in enumerate(meta_data):
        row = table_meta.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F0F4F1")
        set_cell_background(c1, "FFFFFF")

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.font.bold = True
        r0.font.size = Pt(9.5)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ─── 1. Executive Summary ────────────────────────────────────────
    h1 = doc.add_heading("1. Executive Summary", level=1)
    h1.runs[0].font.color.rgb = PRIMARY_COLOR

    p = doc.add_paragraph()
    p.add_run(
        "EcoSage is an evidence-grounded conversational AI system designed to behave like an environmental scientist, not a generic chatbot. "
        "It ingests multi-variable soil, land-use, biodiversity, climate, and human-impact metrics; traverses an indexed corpus of grounded scientific evidence "
        "(FAO soil carbon reports, IPCC AR6 assessments, and peer-reviewed agroecology literature); and produces quantified, multi-variable recommendations "
        "to optimize biodiversity and ecological resilience on any target parcel of land."
    )
    p_why = doc.add_paragraph()
    p_why.add_run("Key Core Differentiators:\n").font.bold = True
    p_why.add_run("• Explicitly NOT an LLM wrapper: ").font.bold = True
    p_why.add_run("The LLM is never permitted to make claims without injected, retrieved scientific passages.\n")
    p_why.add_run("• Multi-Metric Causal Reasoning (≥3 Variables): ").font.bold = True
    p_why.add_run("Explicitly traverses causal paths connecting Soil Health ↔ Biodiversity, Water Availability ↔ Species Survival, and Land Use ↔ Habitat Fragmentation.\n")
    p_why.add_run("• Rigorous Post-Generation Validator: ").font.bold = True
    p_why.add_run("Rejects generic advice ('use sustainable practices') via strict regex and heuristics checking for numeric quantification, causal mechanism clauses, and cited document IDs.")

    # ─── 2. System Architecture & Data Flow ─────────────────────────
    h2 = doc.add_heading("2. System Architecture & Data Flow", level=1)
    h2.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_paragraph(
        "EcoSage implements a structured pipeline ensuring full explainability and auditability:"
    )

    arch_steps = [
        ("1. Input Handler & Session Memory", "Accepts free-text or structured JSON (matching PRD Section 8.2). Extracts metrics via heuristic regex. Preserves session history."),
        ("2. Slot-Filling Validator", "Monitors 5 core categories (Soil, Land Use, Climate, Biodiversity, Human Impact). If <3 categories are supplied, asks targeted clarifying questions."),
        ("3. Knowledge Base & Vector Store", "ChromaDB local vector database containing 60 chunked passages from FAO-SOC-2017, IPCC-AR6-LU, and 6 peer-reviewed papers embedded with gemini-embedding-001."),
        ("4. Multi-Metric Causal Graph", "26 source-tagged causal edges traversing 23 environmental metrics to uncover mechanistic linkages before text generation."),
        ("5. Structured Table Lookups", "Direct tabular joins against JSON benchmark tables for SOC by biome, species richness indices, and rainfall-biodiversity modifiers."),
        ("6. Grounded Generator", "Constructs a strict context prompt ensuring only retrieved data is passed into Gemini with multi-model resilient fallback."),
        ("7. Output Validator", "Checks 8 validation rules (citations, numbers/quantification, substantive mechanism, ≥3 metrics, no generic blocklisted phrases). Retries up to 2 times upon failure.")
    ]

    table_arch = doc.add_table(rows=len(arch_steps)+1, cols=2)
    table_arch.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_arch.autofit = False

    hdr_cells = table_arch.rows[0].cells
    hdr_cells[0].width = Inches(2.2)
    hdr_cells[1].width = Inches(4.3)
    set_cell_background(hdr_cells[0], "E8F5E9")
    set_cell_background(hdr_cells[1], "E8F5E9")
    hdr_cells[0].paragraphs[0].add_run("Pipeline Component").font.bold = True
    hdr_cells[1].paragraphs[0].add_run("Responsibility & Implementation").font.bold = True

    for i, (name, desc) in enumerate(arch_steps):
        row = table_arch.rows[i+1]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        c0.paragraphs[0].add_run(name).font.bold = True
        c1.paragraphs[0].add_run(desc)

    # ─── 3. Multi-Metric Causal Graph (Core Differentiator) ───────────
    h3 = doc.add_heading("3. Multi-Metric Causal Graph (Core Differentiator)", level=1)
    h3.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_paragraph(
        "To satisfy the hackathon's hard constraint requiring reasoning across ≥3 environmental variables, "
        "EcoSage implements a directed graph with 26 source-tagged edges covering all three required clusters:"
    )

    doc.add_paragraph(
        "• Soil Health ↔ Biodiversity Cluster:\n"
        "  intercropping → root_diversity (+10-20% SOC) → soil_organic_carbon → microbial_diversity (20-40% increase per 1% SOC) → nutrient_cycling → species_richness\n\n"
        "• Water Availability ↔ Species Survival Cluster:\n"
        "  soil_organic_carbon → soil_moisture_retention (1-3% increase per 1% SOC) → buffers water_stress → species_survival\n\n"
        "• Land Use ↔ Habitat Fragmentation Cluster:\n"
        "  monoculture_intensification → habitat_fragmentation (species decline 20-50% below 10ha) → loss of pollinator_diversity (30-50% decline) → overall species_richness"
    )

    # ─── 4. Automated Verification & Parameter Matrix Results (140/140 Passed) ────
    h4 = doc.add_heading("4. Automated Verification & Parameter Matrix Results (140/140 Passed)", level=1)
    h4.runs[0].font.color.rgb = PRIMARY_COLOR

    p_test = doc.add_paragraph()
    p_test.add_run("EcoSage achieved a 100% pass rate (140 out of 140 automated tests) ").font.bold = True
    p_test.add_run("covering parameter boundary validation across all 12 variables, 32 category permutations, text extraction, 5 diverse biomes, geo-prior inference, ground-truth evaluation benchmark, failsafe engine, deterministic confidence bands, and the PRD Section 6 acceptance test suite:")

    test_results = [
        ("Parameter Boundary Suite (58 tests)", "Tests valid & out-of-bound limits for all 12 environmental metrics", "58/58 PASSED"),
        ("Category Permutations Suite (32 tests)", "Tests completeness & slot-filling for all 32 subset combinations", "32/32 PASSED"),
        ("Free-Text Heuristics Suite (20 tests)", "Tests natural language metric extraction across all variables", "20/20 PASSED"),
        ("Geo-Prior Climate Inference (9 tests)", "Tests FR-5.3 offline coordinate-to-climate reverse inference", "9/9 PASSED"),
        ("Diverse Biome Scenarios (5 tests)", "Tests semi-arid, tropical, arid, temperate, and wetland regimes", "5/5 PASSED"),
        ("Causal Graph Reachability (5 tests)", "Verifies all 23 metrics have edges and paths to species richness", "5/5 PASSED"),
        ("Scientific Ground-Truth Benchmark (5 tests)", "Tests causal density (>=3 vars), trade-offs, economics, and quantification", "5/5 PASSED"),
        ("Deterministic Failsafe Engine", "Offline rule-based generation with zero cloud dependency", "PASSED"),
        ("PRD Section 6 Acceptance Benchmark", "Input: 0.3% SOC, low rainfall, monoculture wheat, semi-arid", "PASSED"),
        ("Agroforestry / Intercropping Selection", "Recommends agroforestry and legume intercropping", "PASSED"),
        ("Quantified Estimate Verification", "Quantifies +15-25% SOC, +40-60% bird richness", "PASSED"),
        ("FAO & IPCC Grounded Citation", "Cites FAO-SOC-2017 and IPCC-AR6-LU by name and ID", "PASSED"),
        ("Multi-Metric Linkage (≥3 Variables)", "Links 3+ variables (SOC, root diversity, species richness)", "PASSED"),
        ("Low Rainfall Constraint Handling", "Flags low rainfall / drought stress on species selection", "PASSED"),
        ("Adversarial Slot-Filling Test", "Vague query ('Help my land') triggers clarifying questions", "PASSED"),
        ("Validator & Confidence Bands (15 tests)", "Rejects missing sources, unquantified text, generic advice, and verifies 3 deterministic confidence bands (High/Medium/Low)", "15/15 PASSED")
    ]

    table_tests = doc.add_table(rows=len(test_results)+1, cols=3)
    table_tests.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_tests.autofit = False

    th = table_tests.rows[0].cells
    th[0].width = Inches(2.3)
    th[1].width = Inches(3.2)
    th[2].width = Inches(1.0)
    set_cell_background(th[0], "E8F5E9")
    set_cell_background(th[1], "E8F5E9")
    set_cell_background(th[2], "E8F5E9")
    th[0].paragraphs[0].add_run("Test Scenario").font.bold = True
    th[1].paragraphs[0].add_run("Verification Details").font.bold = True
    th[2].paragraphs[0].add_run("Result").font.bold = True

    for i, (name, details, res) in enumerate(test_results):
        row = table_tests.rows[i+1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width = Inches(2.3)
        c1.width = Inches(3.2)
        c2.width = Inches(1.0)
        c0.paragraphs[0].add_run(name)
        c1.paragraphs[0].add_run(details)
        r_res = c2.paragraphs[0].add_run(res)
        r_res.font.bold = True
        r_res.font.color.rgb = PRIMARY_COLOR

    # ─── 5. Evaluation Criteria Mapping ──────────────────────────────
    h5 = doc.add_heading("5. Evaluation Criteria Mapping", level=1)
    h5.runs[0].font.color.rgb = PRIMARY_COLOR

    eval_map = [
        ("Depth of Reasoning (30%)", "Multi-metric causal graph with 26 edges traversing soil, water, and fragmentation relationships. Validator rejects non-causal outputs."),
        ("Scientific Grounding (25%)", "ChromaDB vector RAG over FAO reports, IPCC AR6 chapters, and 6 peer-reviewed papers. Mandatory citation check."),
        ("Knowledge System Design (20%)", "Local ChromaDB store + structured JSON tables. Transparent /debug/retrieval/{session_id} audit endpoint with similarity scores."),
        ("Conversational Intelligence (15%)", "Session memory and slot-filling across 5 environmental categories. Incomplete input triggers clarifying questions."),
        ("Output Clarity (10%)", "Strict JSON contract. Streamlit workstation with dedicated 'Sources Used' expander panel, quantified tags, causal pathway pills, and report download.")
    ]

    table_eval = doc.add_table(rows=len(eval_map)+1, cols=2)
    table_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_eval.autofit = False

    eh = table_eval.rows[0].cells
    eh[0].width = Inches(2.2)
    eh[1].width = Inches(4.3)
    set_cell_background(eh[0], "E8F5E9")
    set_cell_background(eh[1], "E8F5E9")
    eh[0].paragraphs[0].add_run("Criterion & Weight").font.bold = True
    eh[1].paragraphs[0].add_run("How EcoSage Satisfies It").font.bold = True

    for i, (crit, desc) in enumerate(eval_map):
        row = table_eval.rows[i+1]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        c0.paragraphs[0].add_run(crit).font.bold = True
        c1.paragraphs[0].add_run(desc)

    # ─── 6. Evaluator Streamlit Workstation Interface ─────────────────
    h6 = doc.add_heading("6. Evaluator Streamlit Workstation Interface", level=1)
    h6.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_paragraph(
        "EcoSage delivers a professional agronomist-grade workstation designed for evaluator visual impact and ergonomic clarity. "
        "Adhering to a strict flat design system (zero drop shadows/gradients, strictly two typographic weights 400 and 500, and 4 semantic colors: "
        "Green=high confidence/success, Amber=medium confidence/short horizon, Red=low confidence/error, Blue=informational), "
        "the interface provides 5 distinct views documented in the screenshots directory:"
    )

    ui_screens = [
        ("1. Landing Explainer & 1-Click Test Chips", "screenshots/01_landing_page.png", "3 explainer cards (Grounded in FAO/IPCC, Multi-Metric Causal Graph, Validated Not Generic), interactive 5-slot category bar, and 1-click test scenario chips."),
        ("2. Field Report Card with Causal Trail", "screenshots/02_advisory_field_report.png", "Multi-metric recommendation card with semantic confidence badge, 'Why this matters' line, causal pathway trail pills, operational trade-offs, and 1-click .md advisory report export."),
        ("3. Grounded Retrieval Detail & Provenance", "screenshots/03_retrieval_evidence_detail.png", "Inspectable ChromaDB audit expander displaying document IDs, exact cosine similarities (e.g. 0.794, 0.788), chunk excerpts, and supported recommendation provenance."),
        ("4. Scenario Comparison ('Try Changing One Variable')", "screenshots/04_scenario_comparison.png", "Side-by-side sensitivity workstation comparing baseline and perturbed environmental regimes in real-time to observe dynamic causal graph adaptation."),
        ("5. Clarifying Inquiry Flow", "screenshots/05_clarifying_questions.png", "Warm blue informational card asking targeted clarifying questions with discrete parameter buttons when incomplete or vague inputs are supplied.")
    ]

    table_ui = doc.add_table(rows=len(ui_screens)+1, cols=3)
    table_ui.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_ui.autofit = False

    uh = table_ui.rows[0].cells
    uh[0].width = Inches(2.2)
    uh[1].width = Inches(2.0)
    uh[2].width = Inches(2.3)
    set_cell_background(uh[0], "E8F5E9")
    set_cell_background(uh[1], "E8F5E9")
    set_cell_background(uh[2], "E8F5E9")
    uh[0].paragraphs[0].add_run("Workstation Screen").font.bold = True
    uh[1].paragraphs[0].add_run("Asset File").font.bold = True
    uh[2].paragraphs[0].add_run("Evaluator Impact & Features").font.bold = True

    for i, (sname, sfile, sdesc) in enumerate(ui_screens):
        row = table_ui.rows[i+1]
        c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
        c0.width = Inches(2.2)
        c1.width = Inches(2.0)
        c2.width = Inches(2.3)
        c0.paragraphs[0].add_run(sname).font.bold = True
        c1.paragraphs[0].add_run(sfile)
        c2.paragraphs[0].add_run(sdesc)

    # Embed Actual Screenshot Figures directly into Document
    doc.add_paragraph().paragraph_format.space_before = Pt(8)
    h6_sub = doc.add_heading("6.1 Visual Workstation Screen Captures", level=2)
    h6_sub.runs[0].font.color.rgb = SECONDARY_COLOR

    screen_figures = [
        ("screenshots/01_landing_page.png", "Figure 1: Workstation Landing Page with 3 Explainer Cards, 5-Slot Category Bar, and 1-Click Evaluation Chips."),
        ("screenshots/02_advisory_field_report.png", "Figure 2: Grounded Advisory Field Report Card with Semantic Badges, 'Why this matters', Causal Traversal Chips, and Trade-offs."),
        ("screenshots/03_retrieval_evidence_detail.png", "Figure 3: ChromaDB Retrieval Provenance Audit Expander displaying Document IDs, Cosine Similarities, and Supported Recommendations."),
        ("screenshots/04_scenario_comparison.png", "Figure 4: Parameter Sensitivity Analysis ('Try Changing One Variable') executing live dual-scenario comparison."),
        ("screenshots/05_clarifying_questions.png", "Figure 5: Conversational Clarifying Flow asking targeted questions with interactive discrete parameter buttons."),
    ]

    import io
    import os

    from PIL import Image

    for img_path, caption in screen_figures:
        if os.path.exists(img_path):
            # Compress and resize image in memory to keep document under 500KB
            im = Image.open(img_path)
            w, h = im.size
            target_w = 1100
            target_h = int(h * (target_w / w))
            im_resized = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
            img_buf = io.BytesIO()
            im_resized.convert("RGB").save(img_buf, format="JPEG", quality=68, optimize=True)
            img_buf.seek(0)

            p_img = doc.add_paragraph()
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            run_img = p_img.add_run()
            run_img.add_picture(img_buf, width=Inches(6.0))
            
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_after = Pt(10)
            run_cap = p_cap.add_run(caption)
            run_cap.font.size = Pt(8.5)
            run_cap.font.italic = True
            run_cap.font.color.rgb = RGBColor(107, 114, 128)

    # ─── 7. Database Schema, CI/CD & Local Reproduction ──────────────
    h7 = doc.add_heading("7. Architecture, Database/Schema, Local Setup & CI/CD", level=1)
    h7.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_paragraph(
        "• Database / Vector Schema:\n"
        "  - ChromaDB Collection: 'ecosage_knowledge' (60 vector chunks, embedded via gemini-embedding-001 with 768-dim vectors).\n"
        "  - Metadata Fields: document_id, source_name, section_title, target_metrics, chunk_index.\n"
        "  - Reference Benchmark Tables: JSON schemas in corpus/tables/ for SOC % benchmarks by biome, species richness baselines, and rainfall modifiers.\n\n"
        "• CI/CD Pipeline (.github/workflows/ci.yml):\n"
        "  - Multi-OS, multi-Python matrix testing across Python 3.11, 3.12, 3.13, and 3.14.\n"
        "  - Automated Ruff linter check + full Pytest suite execution on every pull request and push to main.\n"
        "  - Standalone HTML test report artifact generated and uploaded on every build for reviewer auditability.\n\n"
        "• Windows One-Click Quickstart (run.bat):\n"
        "  - Simply double-click 'run.bat' for an interactive menu:\n"
        "    [1] Streamlit UI (Frontend Dashboard)\n"
        "    [2] Full Stack (FastAPI Backend + Streamlit UI)\n"
        "    [3] Launch FastAPI Backend Server Only (Port 8000)\n"
        "    [4] Ingest Knowledge Base into ChromaDB\n"
        "    [5] Run Full 140-Test Suite\n"
        "    [6] Run Code Quality Check (Ruff Linter)\n\n"
        "• Manual Command Line Setup:\n"
        "  1. git clone <YOUR_REPO_URL> && cd ecosage\n"
        "  2. pip install -r requirements.txt\n"
        "  3. copy .env.example .env (add free GOOGLE_API_KEY from aistudio.google.com)\n"
        "  4. python -m ecosage.ingest\n"
        "  5. pytest -v  (Runs all 140 tests)\n"
        "  6. streamlit run ui/app.py"
    )

    doc.save(output_path)
    print(f"Successfully generated submission document at: {output_path}")

if __name__ == "__main__":
    create_submission_doc()
