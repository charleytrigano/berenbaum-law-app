from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import pandas as pd
import tempfile
import os

# =====================================================================
#  PDF BUILDER WITHOUT KALEIDO (SAFE MODE)
# =====================================================================

def build_pdf_report(df: pd.DataFrame, charts=None, kpis=None):
    """
    Génère un PDF sans graphiques (compatibilité Streamlit Cloud).
    Ajoute :
    - Titre
    - KPIs
    - Tableau des données
    """

    styles = getSampleStyleSheet()
    story = []

    # ---------------------------------------------------------
    # TITRE
    # ---------------------------------------------------------
    story.append(Paragraph("<b>Berenbaum Law — Rapport Analytique</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------
    if kpis:
        story.append(Paragraph("<b>Indicateurs</b>", styles["Heading2"]))
        for key, value in kpis.items():
            story.append(Paragraph(f"{key} : <b>{value}</b>", styles["Normal"]))
        story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # TABLEAU DES DONNÉES
    # ---------------------------------------------------------
    if df is not None and not df.empty:
        story.append(Paragraph("<b>Données filtrées</b>", styles["Heading2"]))
        story.append(Spacer(1, 8))

        # Convertir dataframe en liste pour ReportLab
        data = [df.columns.tolist()] + df.astype(str).values.tolist()

        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
        )
        story.append(table)

    # ---------------------------------------------------------
    # BUILD FILE
    # ---------------------------------------------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    doc.build(story)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    os.remove(pdf_path)
    return pdf_bytes
