"""
EcoSage Design System Theme & Styling (Section 0)
==================================================
Strict design rules:
- One neutral base (white/near-white #FAFAFA, dark gray text #111827)
- One accent color (#1B5E20 forest green)
- Strictly 4 semantic colors:
    * Green: #15803D (success / high confidence / long horizon)
    * Amber: #B45309 (medium confidence / short horizon / caution)
    * Red:   #B91C1C (low confidence / error)
    * Blue:  #1D4ED8 (informational / clarifying questions)
- Typography: sans-serif, strictly two weights (400 regular, 500 medium), NO bold/700
- Cards: white, 1px hairline border #E5E7EB, 12px radius, no shadows, no gradients
- Icons: unified clean SVG icon set
- Spacing rhythm: 8 / 12 / 16 / 24px
"""

COLOR_BG_APP = "#FAFAFA"
COLOR_BG_CARD = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#111827"
COLOR_TEXT_SECONDARY = "#374151"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"
COLOR_ACCENT = "#1B5E20"
COLOR_ACCENT_LIGHT = "#E8F5E9"

COLOR_GREEN_TEXT = "#15803D"
COLOR_GREEN_BG = "#F0FDF4"
COLOR_GREEN_BORDER = "#BBF7D0"

COLOR_AMBER_TEXT = "#B45309"
COLOR_AMBER_BG = "#FFFBEB"
COLOR_AMBER_BORDER = "#FDE68A"

COLOR_RED_TEXT = "#B91C1C"
COLOR_RED_BG = "#FEF2F2"
COLOR_RED_BORDER = "#FECACA"

COLOR_BLUE_TEXT = "#1D4ED8"
COLOR_BLUE_BG = "#EFF6FF"
COLOR_BLUE_BORDER = "#BFDBFE"


def get_svg_icon(name: str, color: str = "currentColor", size: int = 16) -> str:
    """Return inline SVG string for consistent icon set (stroke-width: 1.75)."""
    icons = {
        "check": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        "circle-check": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
        "circle": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75"><circle cx="12" cy="12" r="9"></circle></svg>',
        "dot": f'<svg width="{size}" height="{size}" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4" fill="{color}"/></svg>',
        "leaf": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6"></path></svg>',
        "book": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>',
        "network": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="16" y="16" width="6" height="6" rx="1"></rect><rect x="2" y="16" width="6" height="6" rx="1"></rect><rect x="9" y="2" width="6" height="6" rx="1"></rect><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"></path><path d="M12 12V8"></path></svg>',
        "shield": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><path d="m9 12 2 2 4-4"></path></svg>',
        "arrow-right": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>',
        "info": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>',
        "alert": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
        "database": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>',
        "external-link": f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>',
    }
    return icons.get(name, "")


THEME_CSS = f"""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..24,400,0,0&display=swap");

    /* Base Page Styling */
    .stApp {{
        background-color: {COLOR_BG_APP} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }}

    /* Hide raw icon ligatures in Streamlit expanders */
    summary > span > span:first-child,
    summary span[data-testid="stIconMaterial"] {{
        display: none !important;
        font-size: 0 !important;
        width: 0 !important;
        height: 0 !important;
        visibility: hidden !important;
    }}
    summary::before {{
        content: "▾ " !important;
        font-size: 13px !important;
        color: #4B5563 !important;
        display: inline-block !important;
    }}
    details[open] summary::before {{
        content: "▴ " !important;
    }}

    html, body, p, label, input, textarea {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        font-weight: 400;
        color: {COLOR_TEXT_SECONDARY};
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }}

    /* Strictly weights 400 and 500, no bold/700 anywhere */
    h1 {{
        font-size: 21px !important;
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 6px !important;
    }}
    h2 {{
        font-size: 19px !important;
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        letter-spacing: -0.01em !important;
        margin-top: 14px !important;
        margin-bottom: 6px !important;
    }}
    h3 {{
        font-size: 17px !important;
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        letter-spacing: -0.01em !important;
        margin-top: 10px !important;
        margin-bottom: 4px !important;
    }}
    h4, h5, h6 {{
        font-size: 15px !important;
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    b, strong, .stMarkdown strong {{
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* Top Bar Header */
    .ecosage-top-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 18px;
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        margin-bottom: 14px;
        box-sizing: border-box;
    }}
    .ecosage-top-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .ecosage-wordmark {{
        font-size: 19px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .ecosage-tagline {{
        font-size: 13px;
        color: {COLOR_TEXT_MUTED};
        border-left: 1px solid {COLOR_BORDER};
        padding-left: 12px;
    }}
    .ecosage-top-right {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .ecosage-status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: {COLOR_TEXT_SECONDARY};
        background: {COLOR_GREEN_BG};
        border: 1px solid {COLOR_GREEN_BORDER};
        border-radius: 9999px;
        padding: 3px 10px;
    }}
    .ecosage-link-pill {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 12px;
        color: {COLOR_ACCENT};
        text-decoration: none;
        padding: 3px 8px;
        border-radius: 6px;
    }}
    .ecosage-link-pill:hover {{
        background: {COLOR_ACCENT_LIGHT};
    }}

    /* Explainer Cards */
    .explainer-card {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        box-sizing: border-box;
    }}
    .explainer-title {{
        font-size: 14px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }}
    .explainer-desc {{
        font-size: 13px;
        color: {COLOR_TEXT_MUTED};
        line-height: 1.45;
        margin: 0;
    }}

    /* Input Slot Panel */
    .slots-container {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }}
    .slots-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }}
    .slots-header-title {{
        font-size: 13px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .slots-progress-label {{
        font-size: 12px;
        color: {COLOR_TEXT_MUTED};
    }}
    .slots-row {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 8px;
    }}
    .slot-pill-empty {{
        background: {COLOR_BG_APP};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        color: {COLOR_TEXT_MUTED};
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .slot-pill-filled {{
        background: {COLOR_GREEN_BG};
        border: 1px solid {COLOR_GREEN_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        color: {COLOR_GREEN_TEXT};
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .slot-pill-val {{
        font-size: 11px;
        color: {COLOR_TEXT_SECONDARY};
        margin-left: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* Field Report Card */
    .field-report-card {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }}
    .field-report-card-low-conf {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_AMBER_BORDER};
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }}
    .report-card-action {{
        font-size: 16px;
        font-weight: 500;
        color: {COLOR_TEXT_PRIMARY};
        margin-bottom: 10px;
        line-height: 1.35;
    }}
    .report-badges-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 12px;
    }}
    .why-this-matters {{
        background: {COLOR_BLUE_BG};
        border-left: 3px solid {COLOR_BLUE_TEXT};
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
        color: {COLOR_TEXT_SECONDARY};
        margin-bottom: 12px;
        line-height: 1.45;
    }}
    .mechanism-block {{
        font-size: 14px;
        line-height: 1.5;
        color: {COLOR_TEXT_SECONDARY};
        margin-bottom: 12px;
    }}
    .causal-flow-container {{
        background: {COLOR_BG_APP};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 12px;
    }}
    .causal-flow-title {{
        font-size: 11px;
        font-weight: 500;
        color: {COLOR_TEXT_MUTED};
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .causal-flow-chips {{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 6px;
    }}
    .causal-chip {{
        background: {COLOR_BG_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 9999px;
        padding: 3px 10px;
        font-size: 12px;
        color: {COLOR_TEXT_SECONDARY};
    }}
    .causal-chip-arrow {{
        color: {COLOR_TEXT_MUTED};
        font-size: 11px;
        display: flex;
        align-items: center;
    }}
    .tradeoffs-callout {{
        background: {COLOR_AMBER_BG};
        border: 1px solid {COLOR_AMBER_BORDER};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        color: {COLOR_AMBER_TEXT};
        margin-bottom: 12px;
    }}
    .tradeoffs-list {{
        margin: 4px 0 0 0;
        padding-left: 18px;
        color: {COLOR_TEXT_SECONDARY};
        font-size: 13px;
    }}
    .low-conf-banner {{
        background: {COLOR_AMBER_BG};
        border: 1px solid {COLOR_AMBER_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        color: {COLOR_AMBER_TEXT};
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 12px;
    }}

    .badge-semantic {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 500;
        border-radius: 9999px;
        padding: 2px 10px;
    }}
    .badge-green {{
        background: {COLOR_GREEN_BG};
        color: {COLOR_GREEN_TEXT};
        border: 1px solid {COLOR_GREEN_BORDER};
    }}
    .badge-amber {{
        background: {COLOR_AMBER_BG};
        color: {COLOR_AMBER_TEXT};
        border: 1px solid {COLOR_AMBER_BORDER};
    }}
    .badge-red {{
        background: {COLOR_RED_BG};
        color: {COLOR_RED_TEXT};
        border: 1px solid {COLOR_RED_BORDER};
    }}
    .badge-blue {{
        background: {COLOR_BLUE_BG};
        color: {COLOR_BLUE_TEXT};
        border: 1px solid {COLOR_BLUE_BORDER};
    }}
    .badge-neutral {{
        background: {COLOR_BG_APP};
        color: {COLOR_TEXT_SECONDARY};
        border: 1px solid {COLOR_BORDER};
    }}

    .clarify-card {{
        background: {COLOR_BLUE_BG};
        border: 1px solid {COLOR_BLUE_BORDER};
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }}
    .clarify-title {{
        font-size: 14px;
        font-weight: 500;
        color: {COLOR_BLUE_TEXT};
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }}
    .clarify-prompt {{
        font-size: 13px;
        color: {COLOR_TEXT_SECONDARY};
        margin-bottom: 10px;
        line-height: 1.4;
    }}

    /* Clean Streamlit Overrides */
    div[data-testid="stExpander"] {{
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 10px !important;
        background: {COLOR_BG_CARD} !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
        box-shadow: none !important;
    }}
    div[data-testid="stExpander"] summary {{
        font-size: 13px !important;
        font-weight: 500 !important;
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    .stButton > button {{
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        border: 1px solid {COLOR_BORDER} !important;
        background: {COLOR_BG_CARD} !important;
        color: {COLOR_TEXT_PRIMARY} !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }}
    .stButton > button:hover {{
        border-color: {COLOR_ACCENT} !important;
        color: {COLOR_ACCENT} !important;
        background: {COLOR_ACCENT_LIGHT} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {COLOR_BG_CARD} !important;
        border-right: 1px solid {COLOR_BORDER} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {COLOR_TEXT_PRIMARY} !important;
    }}

    .ecosage-footer {{
        margin-top: 32px;
        padding-top: 14px;
        border-top: 1px solid {COLOR_BORDER};
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: {COLOR_TEXT_MUTED};
    }}
</style>
"""
