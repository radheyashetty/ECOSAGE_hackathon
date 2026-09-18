"""Generate the official Word submission document for Darukaa.Earth Hackathon."""
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

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
    DARK_TEXT = RGBColor(33, 33, 33)

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
    table_meta = doc.add_table(rows=5, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.autofit = False

    meta_data = [
        ("Candidate / Team:", "[Your Name / Team Name]"),
        ("GitHub Repository:", "https://github.com/[YOUR_USERNAME]/ecosage"),
        ("Live Demo URL:", "http://localhost:8501 (or deployed Streamlit Cloud URL)"),
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

    # ─── 4. Acceptance Test & Verification (18/18 Passed) ────────────
    h4 = doc.add_heading("4. Automated Verification & Acceptance Results", level=1)
    h4.runs[0].font.color.rgb = PRIMARY_COLOR

    p_test = doc.add_paragraph()
    p_test.add_run("EcoSage achieved 100% pass rate (18 out of 18 automated tests) ").font.bold = True
    p_test.add_run("covering both the rigorous output validator unit tests and the PRD Section 6 acceptance test suite:")

    test_results = [
        ("PRD Section 6 Acceptance Benchmark", "Input: 0.3% SOC, low rainfall, monoculture wheat, semi-arid", "PASSED"),
        ("Agroforestry / Intercropping Selection", "Recommends agroforestry and legume intercropping", "PASSED"),
        ("Quantified Estimate Verification", "Quantifies +15-25% SOC, +40-60% bird richness", "PASSED"),
        ("FAO & IPCC Grounded Citation", "Cites FAO-SOC-2017 and IPCC-AR6-LU by name and ID", "PASSED"),
        ("Multi-Metric Linkage (≥3 Variables)", "Links 3+ variables (SOC, root diversity, species richness)", "PASSED"),
        ("Low Rainfall Constraint Handling", "Flags low rainfall / drought stress on species selection", "PASSED"),
        ("Adversarial Slot-Filling Test", "Vague query ('Help my land') triggers clarifying questions", "PASSED"),
        ("Validator Unit Test Suite (11 tests)", "Rejects missing sources, unquantified text, generic advice", "11/11 PASSED")
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
        ("Output Clarity (10%)", "Strict JSON contract. Streamlit UI with dedicated 'Sources Used' expander panel, quantified tags, and reasoning trace.")
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

    # ─── 6. Local Quickstart & Running Instructions ──────────────────
    h6 = doc.add_heading("6. Local Quickstart & Reproduction Guide", level=1)
    h6.runs[0].font.color.rgb = PRIMARY_COLOR

    doc.add_paragraph("EcoSage runs completely free of cost with zero paid infrastructure. Follow these steps to reproduce:")
    doc.add_paragraph(
        "1. Clone repository:\n"
        "   git clone https://github.com/[YOUR_USERNAME]/ecosage.git\n"
        "   cd ecosage\n\n"
        "2. Install dependencies:\n"
        "   pip install -r requirements.txt\n\n"
        "3. Configure API Key in .env:\n"
        "   GOOGLE_API_KEY=your_free_gemini_api_key\n"
        "   (Get a free key in 30 seconds at aistudio.google.com with any Google account)\n\n"
        "4. Ingest Knowledge Base:\n"
        "   python -m ecosage.ingest\n\n"
        "5. Run the Automated Test Suite:\n"
        "   pytest tests/test_validator.py tests/test_acceptance.py -v\n\n"
        "6. Launch FastAPI Backend:\n"
        "   uvicorn ecosage.api:app --reload --port 8000\n\n"
        "7. Launch Streamlit UI (in separate terminal):\n"
        "   streamlit run ui/app.py"
    )

    doc.save(output_path)
    print(f"Successfully generated submission document at: {output_path}")

if __name__ == "__main__":
    create_submission_doc()
