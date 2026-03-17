# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
PDF Report Generator for LGPD DPIA/RIPD reports.
Uses ReportLab to produce professional compliance documents.
"""

from datetime import datetime
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Color palette ────────────────────────────────────────────────────────────
BLUE_DARK   = colors.HexColor("#0f3460")
BLUE_MID    = colors.HexColor("#16213e")
BLUE_LIGHT  = colors.HexColor("#e8f4fd")
RED         = colors.HexColor("#e53935")
ORANGE      = colors.HexColor("#fb8c00")
GREEN       = colors.HexColor("#43a047")
GREY_LIGHT  = colors.HexColor("#f5f5f5")
GREY_TEXT   = colors.HexColor("#555555")

RISK_COLORS = {
    "high":     RED,
    "critical": RED,
    "medium":   ORANGE,
    "low":      GREEN,
    # PT-BR aliases
    "alto":     RED,
    "critico":  RED,
    "medio":    ORANGE,
    "médio":    ORANGE,
    "baixo":    GREEN,
}


# ─── Style helpers ────────────────────────────────────────────────────────────

def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontSize=22,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#cce0ff"),
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontSize=13,
            textColor=BLUE_DARK,
            spaceBefore=14,
            spaceAfter=6,
            borderPad=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREY_TEXT,
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontSize=10,
            textColor=GREY_TEXT,
            leading=13,
            leftIndent=14,
            spaceAfter=2,
            bulletIndent=4,
        ),
        "label": ParagraphStyle(
            "label",
            parent=base["Normal"],
            fontSize=9,
            textColor=GREY_TEXT,
        ),
        "value": ParagraphStyle(
            "value",
            parent=base["Normal"],
            fontSize=10,
            textColor=BLUE_DARK,
            fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#999999"),
            alignment=TA_CENTER,
        ),
    }


def _risk_badge(risk_level: str) -> Table:
    """Small colored badge showing the risk level."""
    color = RISK_COLORS.get(risk_level.lower(), GREY_TEXT)
    label = risk_level.upper()
    t = Table([[label]], colWidths=[3 * cm], rowHeights=[0.7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), color),
        ("TEXTCOLOR",   (0, 0), (-1, -1), colors.white),
        ("FONTNAME",    (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


# ─── Main generator ───────────────────────────────────────────────────────────

def generate_dpia_pdf(dpia_data: dict[str, Any]) -> bytes:
    """
    Generate a DPIA/RIPD PDF report from a DPIAResponse-shaped dict.

    Returns the PDF as bytes (suitable for FileResponse or download).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="RIPD — Relatório de Impacto à Proteção de Dados",
        author="LGPD Sentinel AI",
    )

    s = _styles()
    story = []

    # ── Cover banner ──────────────────────────────────────────────────────────
    banner_data = [[
        Paragraph("🛡️ LGPD Sentinel AI", s["title"]),
    ]]
    banner = Table(banner_data, colWidths=[doc.width])
    banner.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), BLUE_DARK),
        ("TOPPADDING",  (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(banner)

    sub_data = [[Paragraph(
        "Relatório de Impacto à Proteção de Dados — RIPD/DPIA",
        s["subtitle"],
    )]]
    sub_table = Table(sub_data, colWidths=[doc.width])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), BLUE_MID),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Metadata table ────────────────────────────────────────────────────────
    generated_at = dpia_data.get("generated_at", datetime.utcnow().isoformat())
    if hasattr(generated_at, "strftime"):
        generated_at = generated_at.strftime("%d/%m/%Y %H:%M UTC")

    meta_rows = [
        [Paragraph("Empresa",       s["label"]), Paragraph(dpia_data.get("company_name", "N/A"),    s["value"])],
        [Paragraph("Gerado em",     s["label"]), Paragraph(str(generated_at),                        s["value"])],
        [Paragraph("Modelo de IA",  s["label"]), Paragraph(dpia_data.get("model_used", "N/A"),       s["value"])],
        [Paragraph("Nível de risco",s["label"]), _risk_badge(dpia_data.get("risk_level", "N/A"))],
    ]
    meta_table = Table(meta_rows, colWidths=[4 * cm, doc.width - 4 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE_LIGHT),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [BLUE_LIGHT, colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Treatment description ─────────────────────────────────────────────────
    story.append(Paragraph("1. Descrição do Tratamento", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK, spaceAfter=6))
    story.append(Paragraph(
        dpia_data.get("treatment_description", "Não informado."), s["body"]
    ))

    # Legal basis
    story.append(Paragraph("Base Legal", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=4))
    story.append(Paragraph(dpia_data.get("legal_basis", "Não identificada."), s["body"]))

    # Applicable articles
    articles = dpia_data.get("applicable_articles", [])
    if articles:
        story.append(Paragraph("Artigos Aplicáveis", s["h2"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=4))
        for art in articles:
            story.append(Paragraph(f"• {art}", s["bullet"]))

    # ── Risks ─────────────────────────────────────────────────────────────────
    risks = dpia_data.get("risks", [])
    if risks:
        story.append(Paragraph("2. Riscos Identificados", s["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK, spaceAfter=6))

        risk_rows = [
            [
                Paragraph("<b>Risco</b>",        s["body"]),
                Paragraph("<b>Probabilidade</b>", s["body"]),
                Paragraph("<b>Impacto</b>",       s["body"]),
                Paragraph("<b>Nível</b>",          s["body"]),
            ]
        ]
        for r in risks:
            nivel = r.get("nivel_risco", r.get("risk_level", "N/A"))
            risk_rows.append([
                Paragraph(r.get("descricao", r.get("description", "N/A")), s["label"]),
                Paragraph(r.get("probabilidade", r.get("probability", "N/A")), s["label"]),
                Paragraph(r.get("impacto", r.get("impact", "N/A")), s["label"]),
                _risk_badge(nivel),
            ])
        risk_table = Table(
            risk_rows,
            colWidths=[7 * cm, 3 * cm, 3 * cm, 3 * cm],
        )
        risk_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), BLUE_DARK),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [GREY_LIGHT, colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Mitigation ────────────────────────────────────────────────────────────
    measures = dpia_data.get("mitigation_measures", [])
    if measures:
        story.append(Paragraph("3. Medidas de Mitigação", s["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK, spaceAfter=6))
        for m in measures:
            if isinstance(m, dict):
                text = m.get("medida", m.get("measure", str(m)))
            else:
                text = str(m)
            story.append(Paragraph(f"• {text}", s["bullet"]))

    # ── Recommendations ───────────────────────────────────────────────────────
    recs = dpia_data.get("recommendations", [])
    if recs:
        story.append(Paragraph("4. Recomendações de Conformidade", s["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK, spaceAfter=6))
        for rec in recs:
            story.append(Paragraph(f"• {rec}", s["bullet"]))

    # ── ANPD consultation ─────────────────────────────────────────────────────
    story.append(Paragraph("5. Consulta Prévia à ANPD", s["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE_DARK, spaceAfter=6))
    requires = dpia_data.get("requires_anpd_consultation", False)
    story.append(Paragraph(
        f"{'✅ Necessária' if requires else '❌ Não obrigatória'}",
        s["body"],
    ))
    reason = dpia_data.get("anpd_consultation_reason")
    if reason:
        story.append(Paragraph(f"Justificativa: {reason}", s["body"]))

    # ── Risk score summary ────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    score = dpia_data.get("overall_risk_score", 0)
    compliance = dpia_data.get("compliance_score", 0)
    summary_rows = [
        [Paragraph("Score de Risco Geral",    s["label"]), Paragraph(f"{score:.0%}", s["value"])],
        [Paragraph("Score de Conformidade",   s["label"]), Paragraph(f"{compliance:.0f}/100", s["value"])],
    ]
    summary_table = Table(summary_rows, colWidths=[6 * cm, doc.width - 6 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), BLUE_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Gerado por LGPD Sentinel AI • github.com/ldsjunior-ui/lgpd-sentinel-ai • Apache 2.0 • "
        "Este relatório é informativo. Consulte um advogado para conformidade legal completa.",
        s["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()
