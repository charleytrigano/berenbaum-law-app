# utils/pdf_export_groupe.py
# Export PDF d’un groupe dossier (parent + fils)
# Robuste : parent = dict, children = list[dict]

import os
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _to_float(v):
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def _bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ["true", "1", "yes", "oui", "y", "vrai"]


def export_groupe_pdf(parent: dict, children: list, output):
    """
    Génère un PDF "Fiche groupe dossier (parent + fils)".

    Paramètres:
      - parent: dict (peut être {})
      - children: list[dict]
      - output:
          * str => chemin fichier
          * BytesIO => buffer
    """
    if parent is None:
        parent = {}
    if children is None:
        children = []
    if not isinstance(children, list):
        # sécurité : si on reçoit autre chose, on force en liste
        children = list(children)

    # --- Output target ---
    buffer = None
    if isinstance(output, (BytesIO,)):
        buffer = output
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1.3 * cm,
            rightMargin=1.3 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
        )
    else:
        # chemin fichier
        doc = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            leftMargin=1.3 * cm,
            rightMargin=1.3 * cm,
            topMargin=1.2 * cm,
            bottomMargin=1.2 * cm,
        )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=16,
        leading=18,
        spaceAfter=10,
    )
    h_style = ParagraphStyle(
        "HCustom",
        parent=styles["Heading2"],
        fontSize=12,
        leading=14,
        spaceBefore=8,
        spaceAfter=6,
    )
    normal = styles["BodyText"]

    elements = []

    # --- Logo (si présent) ---
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        try:
            elements.append(RLImage(logo_path, width=3.0 * cm, height=3.0 * cm))
            elements.append(Spacer(1, 6))
        except Exception:
            pass

    # --- Titre ---
    parent_id = str(parent.get("Dossier N", "") or parent.get("Dossier Parent", "") or "").strip()
    title = f"Fiche groupe dossier (Parent + Fils) — {parent_id}" if parent_id else "Fiche groupe dossier (Parent + Fils)"
    elements.append(Paragraph(title, title_style))

    # --- Date génération ---
    elements.append(
        Paragraph(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal)
    )
    elements.append(Spacer(1, 10))

    # --- Parent bloc ---
    elements.append(Paragraph("Parent", h_style))

    parent_rows = [
        ["Dossier N", str(parent.get("Dossier N", "") or "")],
        ["Nom", str(parent.get("Nom", "") or "")],
        ["Date", str(parent.get("Date", "") or "")],
        ["Catégorie", str(parent.get("Categories", "") or "")],
        ["Sous-catégorie", str(parent.get("Sous-categories", "") or "")],
        ["Visa", str(parent.get("Visa", "") or "")],
        ["Commentaire", str(parent.get("Commentaire", "") or "")],
    ]

    # si parent vide (cas où parent n’existe pas comme ligne)
    if all((str(v[1]).strip() == "" for v in parent_rows)):
        parent_rows = [["Info", "Parent non présent comme ligne dédiée dans la base (groupe affiché via les fils)."]]

    t_parent = Table(parent_rows, colWidths=[4.2 * cm, 12.8 * cm])
    t_parent.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(t_parent)
    elements.append(Spacer(1, 12))

    # --- Enfants tableau ---
    elements.append(Paragraph("Sous-dossiers (fils)", h_style))

    if not children:
        elements.append(Paragraph("Aucun sous-dossier (fils) détecté.", normal))
        elements.append(Spacer(1, 10))
    else:
        headers = [
            "Dossier N", "Nom", "Date", "Catégorie", "Sous-cat", "Visa",
            "Honoraires", "Frais",
            "A1", "A2", "A3", "A4",
            "Escrow état",
            "Statut"
        ]
        data = [headers]

        for c in children:
            dn = str(c.get("Dossier N", "") or "")
            nom = str(c.get("Nom", "") or "")
            date = str(c.get("Date", "") or "")
            cat = str(c.get("Categories", "") or "")
            sous = str(c.get("Sous-categories", "") or "")
            visa = str(c.get("Visa", "") or "")

            hon = _to_float(c.get("Montant honoraires (US $)", 0))
            fr = _to_float(c.get("Autres frais (US $)", 0))
            a1 = _to_float(c.get("Acompte 1", 0))
            a2 = _to_float(c.get("Acompte 2", 0))
            a3 = _to_float(c.get("Acompte 3", 0))
            a4 = _to_float(c.get("Acompte 4", 0))

            escrow_state = "—"
            if _bool(c.get("Escrow", False)):
                escrow_state = "Actif"
            elif _bool(c.get("Escrow_a_reclamer", False)):
                escrow_state = "À réclamer"
            elif _bool(c.get("Escrow_reclame", False)):
                escrow_state = "Réclamé"

            statut = []
            if _bool(c.get("Dossier envoye", False)) or _bool(c.get("Dossier_envoye", False)):
                statut.append("Envoyé")
            if _bool(c.get("Dossier accepte", False)):
                statut.append("Accepté")
            if _bool(c.get("Dossier refuse", False)):
                statut.append("Refusé")
            if _bool(c.get("Dossier Annule", False)):
                statut.append("Annulé")
            if _bool(c.get("RFE", False)):
                statut.append("RFE")
            statut_txt = ", ".join(statut) if statut else "—"

            data.append([
                dn, nom, date, cat, sous, visa,
                f"{hon:,.2f}", f"{fr:,.2f}",
                f"{a1:,.2f}", f"{a2:,.2f}", f"{a3:,.2f}", f"{a4:,.2f}",
                escrow_state,
                statut_txt
            ])

        t = Table(data, repeatRows=1, colWidths=[
            2.2*cm, 2.8*cm, 1.8*cm, 2.2*cm, 2.2*cm, 2.2*cm,
            1.8*cm, 1.4*cm,
            1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm,
            1.8*cm,
            2.3*cm
        ])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1C1C1C")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 8),

                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#DDDDDD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        elements.append(t)
        elements.append(Spacer(1, 12))

    # --- KPI certifiés ---
    elements.append(Paragraph("Totaux certifiés (groupe)", h_style))

    hon_sum = 0.0
    frais_sum = 0.0
    enc_sum = 0.0
    escrow_sum = 0.0

    for c in children:
        hon_sum += _to_float(c.get("Montant honoraires (US $)", 0))
        frais_sum += _to_float(c.get("Autres frais (US $)", 0))
        enc_sum += (
            _to_float(c.get("Acompte 1", 0))
            + _to_float(c.get("Acompte 2", 0))
            + _to_float(c.get("Acompte 3", 0))
            + _to_float(c.get("Acompte 4", 0))
        )
        if _bool(c.get("Escrow", False)) or _bool(c.get("Escrow_a_reclamer", False)) or _bool(c.get("Escrow_reclame", False)):
            escrow_sum += _to_float(c.get("Acompte 1", 0))

    total_facture = hon_sum + frais_sum
    solde = total_facture - enc_sum

    kpi_rows = [
        ["Nombre de sous-dossiers", str(len(children))],
        ["Honoraires", f"${hon_sum:,.2f}"],
        ["Autres frais", f"${frais_sum:,.2f}"],
        ["Total facturé", f"${total_facture:,.2f}"],
        ["Total encaissé", f"${enc_sum:,.2f}"],
        ["Solde", f"${solde:,.2f}"],
        ["Escrow total (Acompte 1)", f"${escrow_sum:,.2f}"],
    ]
    t_kpi = Table(kpi_rows, colWidths=[7.0 * cm, 10.0 * cm])
    t_kpi.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F2F2")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(t_kpi)

    # --- Build ---
    doc.build(elements)

    # si buffer => rien à retourner ici, la page lit buf.getvalue()
    return