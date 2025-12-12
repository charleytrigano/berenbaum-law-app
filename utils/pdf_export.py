# utils/pdf_export.py
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from utils.timeline_builder import build_timeline
import os


def export_dossier_pdf(dossier: dict, output_path: str):
    styles = getSampleStyleSheet()
    story = []

    # Logo
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm))

    story.append(Spacer(1, 12))

    # Titre
    story.append(Paragraph(
        f"<b>Dossier {dossier.get('Dossier N')}</b> — {dossier.get('Nom')}",
        styles["Title"]
    ))

    story.append(Spacer(1, 12))

    # Infos générales
    info = [
        ["Catégorie", dossier.get("Categories", "")],
        ["Sous-catégorie", dossier.get("Sous-categories", "")],
        ["Visa", dossier.get("Visa", "")],
        ["Date création", dossier.get("Date", "")],
    ]

    table = Table(info, colWidths=[6*cm, 10*cm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Finances
    total_facture = float(dossier.get("Montant honoraires (US $)", 0)) + float(dossier.get("Autres frais (US $)", 0))
    total_encaisse = sum(float(dossier.get(f"Acompte {i}", 0) or 0) for i in range(1, 5))
    solde = total_facture - total_encaisse

    finance = [
        ["Montant honoraires", f"${dossier.get('Montant honoraires (US $)', 0):,.2f}"],
        ["Autres frais", f"${dossier.get('Autres frais (US $)', 0):,.2f}"],
        ["Total facturé", f"${total_facture:,.2f}"],
        ["Total encaissé", f"${total_encaisse:,.2f}"],
        ["Solde dû", f"${solde:,.2f}"],
    ]

    table = Table(finance, colWidths=[6*cm, 10*cm])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ]))
    story.append(table)
    story.append(Spacer(1, 16))

    # Timeline
    story.append(Paragraph("<b>Timeline du dossier</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    timeline = build_timeline(dossier)

    for ev in timeline:
        line = f"{ev['date'].date()} — {ev['label']}"
        if ev.get("amount"):
            line += f" — ${ev['amount']:,.2f}"
        story.append(Paragraph(line, styles["Normal"]))

    # PDF
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    doc.build(story)
