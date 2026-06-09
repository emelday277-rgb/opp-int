from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime

BLUE = colors.HexColor("#185FA5")
LIGHT_BLUE = colors.HexColor("#E6F1FB")
GREEN = colors.HexColor("#3B6D11")
LIGHT_GREEN = colors.HexColor("#EAF3DE")
AMBER = colors.HexColor("#854F0B")
LIGHT_AMBER = colors.HexColor("#FAEEDA")
RED = colors.HexColor("#791F1F")
LIGHT_RED = colors.HexColor("#FCEBEB")
GRAY = colors.HexColor("#6b7280")
LIGHT_GRAY = colors.HexColor("#f9fafb")
DARK = colors.HexColor("#111827")
BORDER = colors.HexColor("#e5e7eb")


def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "Title": ParagraphStyle("Title", fontSize=24, textColor=BLUE, fontName="Helvetica-Bold", spaceAfter=4),
        "Subtitle": ParagraphStyle("Subtitle", fontSize=11, textColor=GRAY, fontName="Helvetica", spaceAfter=20),
        "SectionHeader": ParagraphStyle("SectionHeader", fontSize=9, textColor=GRAY, fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=6, textTransform="uppercase", letterSpacing=1),
        "Body": ParagraphStyle("Body", fontSize=10, textColor=DARK, fontName="Helvetica", leading=16, spaceAfter=6),
        "BulletItem": ParagraphStyle("BulletItem", fontSize=10, textColor=DARK, fontName="Helvetica", leading=15, leftIndent=12, spaceAfter=3),
        "Tag": ParagraphStyle("Tag", fontSize=9, fontName="Helvetica-Bold", leading=12),
        "EvidenceStep": ParagraphStyle("EvidenceStep", fontSize=8, textColor=GRAY, fontName="Helvetica-Bold", textTransform="uppercase", letterSpacing=0.5),
        "EvidenceQuery": ParagraphStyle("EvidenceQuery", fontSize=9, textColor=BLUE, fontName="Helvetica-Bold", spaceAfter=3),
        "EvidenceText": ParagraphStyle("EvidenceText", fontSize=9, textColor=GRAY, fontName="Helvetica-Oblique", leading=13),
    }
    return {**{k: styles[k] for k in styles.byName}, **custom}


def section_header(title: str, styles: dict):
    return [
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6),
        Paragraph(title.upper(), styles["SectionHeader"]),
    ]


def bullet_list(items: list, styles: dict, color=DARK):
    return [Paragraph(f"• {item}", styles["BulletItem"]) for item in items if item]


def risk_table(risks: list, bg_color, text_color):
    if not risks:
        return []
    rows = []
    for r in risks:
        desc = r.get("description", "")
        mit = r.get("mitigation", "")
        cell = f"{desc}"
        if mit:
            cell += f"\n→ Mitigation: {mit}"
        rows.append([cell])

    t = Table([[r[0]] for r in rows], colWidths=[16*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("TEXTCOLOR", (0, 0), (-1, -1), text_color),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [bg_color]),
        ("ROWPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
    ]))
    return [t, Spacer(1, 6)]


def generate_pdf_report(results: dict, evidence_trail: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    styles = build_styles()
    story = []

    opp = results.get("opportunity_summary", {})
    org = results.get("organization_summary", {})
    fit = results.get("fit_evaluation", {})
    risks = results.get("risk_assessment", {})
    rec = results.get("recommendation", {})
    plan = results.get("action_plan", {})

    decision = rec.get("decision", "PURSUE").upper()
    score = fit.get("fit_score", 0)
    generated = datetime.now().strftime("%B %d, %Y at %H:%M")

    # --- Cover ---
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("OppInt", styles["Title"]))
    story.append(Paragraph("Opportunity Intelligence Report", styles["Subtitle"]))
    story.append(Paragraph(f"Generated: {generated}", styles["Subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=20))

    # --- Scorecard summary box ---
    if "DO NOT" in decision:
        verdict_color = LIGHT_RED
        verdict_text_color = RED
    elif "CAUTION" in decision:
        verdict_color = LIGHT_AMBER
        verdict_text_color = AMBER
    else:
        verdict_color = LIGHT_GREEN
        verdict_text_color = GREEN

    scorecard_data = [
        [
            Paragraph(f"<font size='28' color='#185FA5'><b>{score}</b></font><font size='14' color='#9ca3af'>/10</font>", styles["Body"]),
            Paragraph(f"<font size='13' color='#185FA5'><b>Fit Score</b></font>", styles["Body"]),
            Paragraph(f"<font size='13'><b>{decision.title()}</b></font>", styles["Body"]),
            Paragraph(f"<font size='11'>{rec.get('confidence_level','')}</font><br/><font size='9' color='#6b7280'>Confidence</font>", styles["Body"]),
        ]
    ]
    scorecard = Table(scorecard_data, colWidths=[3*cm, 4*cm, 5.5*cm, 4*cm])
    scorecard.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("TEXTCOLOR", (2, 0), (2, 0), verdict_text_color),
        ("BACKGROUND", (2, 0), (2, 0), verdict_color),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(scorecard)
    story.append(Spacer(1, 20))

    # --- Strategic Summary ---
    story += section_header("Strategic Summary", styles)
    story.append(Paragraph(rec.get("strategic_summary", ""), styles["Body"]))
    story.append(Spacer(1, 12))

    # --- Opportunity Summary ---
    story += section_header("Opportunity Summary", styles)
    story.append(Paragraph("<b>Purpose</b>", styles["Body"]))
    story.append(Paragraph(opp.get("purpose", ""), styles["Body"]))
    if opp.get("requirements"):
        story.append(Paragraph("<b>Requirements</b>", styles["Body"]))
        story += bullet_list(opp.get("requirements", []), styles)
    if opp.get("deadlines"):
        story.append(Paragraph("<b>Deadlines</b>", styles["Body"]))
        story += bullet_list(opp.get("deadlines", []), styles)
    if opp.get("evaluation_criteria"):
        story.append(Paragraph("<b>Evaluation criteria</b>", styles["Body"]))
        story += bullet_list(opp.get("evaluation_criteria", []), styles)
    story.append(Spacer(1, 12))

    # --- Fit Evaluation ---
    story += section_header("Fit Evaluation", styles)
    if fit.get("strong_matches"):
        story.append(Paragraph("<b>Strong matches</b>", styles["Body"]))
        story += bullet_list([m["area"] for m in fit.get("strong_matches", [])], styles)
    if fit.get("partial_matches"):
        story.append(Paragraph("<b>Partial matches</b>", styles["Body"]))
        story += bullet_list([m["area"] for m in fit.get("partial_matches", [])], styles)
    if fit.get("gaps"):
        story.append(Paragraph("<b>Gaps identified</b>", styles["Body"]))
        story += bullet_list([m["area"] for m in fit.get("gaps", [])], styles)
    if fit.get("evidence_summary"):
        story.append(Paragraph("<b>Evidence summary</b>", styles["Body"]))
        story.append(Paragraph(fit.get("evidence_summary", ""), styles["Body"]))
    story.append(Spacer(1, 12))

    # --- Risk Assessment ---
    story += section_header("Risk Assessment", styles)
    story.append(Paragraph("<b>High risks</b>", styles["Body"]))
    story += risk_table(risks.get("high_risks", []), LIGHT_RED, RED)
    story.append(Paragraph("<b>Medium risks</b>", styles["Body"]))
    story += risk_table(risks.get("medium_risks", []), LIGHT_AMBER, AMBER)
    story.append(Paragraph("<b>Low risks</b>", styles["Body"]))
    story += risk_table(risks.get("low_risks", []), LIGHT_GREEN, GREEN)
    story.append(Spacer(1, 12))

    # --- Recommendation ---
    story += section_header("Recommendation", styles)
    story.append(Paragraph("<b>Reasons to pursue</b>", styles["Body"]))
    story += bullet_list(rec.get("reasons_to_pursue", []), styles)
    story.append(Paragraph("<b>Reasons for caution</b>", styles["Body"]))
    story += bullet_list(rec.get("reasons_for_caution", []), styles)
    if rec.get("key_conditions"):
        story.append(Paragraph("<b>Key conditions</b>", styles["Body"]))
        story += bullet_list(rec.get("key_conditions", []), styles)
    story.append(Spacer(1, 12))

    # --- Action Plan ---
    story += section_header("Action Plan", styles)
    story.append(Paragraph("<b>Immediate actions (next 48 hours)</b>", styles["Body"]))
    story += bullet_list(plan.get("immediate_actions", []), styles)
    story.append(Paragraph("<b>Short-term actions (this week)</b>", styles["Body"]))
    story += bullet_list(plan.get("short_term_actions", []), styles)
    story.append(Paragraph("<b>Documents to prepare</b>", styles["Body"]))
    story += bullet_list(plan.get("documents_to_prepare", []), styles)
    story.append(Paragraph("<b>Preparation checklist</b>", styles["Body"]))
    story += bullet_list(plan.get("preparation_checklist", []), styles)
    story.append(Paragraph("<b>Submission checklist</b>", styles["Body"]))
    story += bullet_list(plan.get("submission_checklist", []), styles)
    story.append(Spacer(1, 12))

    # --- Evidence Trail ---
    story += section_header("Evidence Trail", styles)
    for entry in evidence_trail:
        story.append(Paragraph(entry.get("step", "").replace("_", " ").upper(), styles["EvidenceStep"]))
        story.append(Paragraph(f'Query: "{entry.get("query_used", "")}"', styles["EvidenceQuery"]))
        excerpt = entry.get("evidence_retrieved", "")[:300]
        story.append(Paragraph(f"{excerpt}...", styles["EvidenceText"]))
        story.append(Spacer(1, 8))

    # --- Footer ---
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Generated by OppInt — Opportunity Intelligence Agent · Powered by Microsoft Foundry IQ",
        ParagraphStyle("Footer", fontSize=8, textColor=GRAY, fontName="Helvetica", alignment=TA_CENTER)
    ))

    doc.build(story)
    return buffer.getvalue()