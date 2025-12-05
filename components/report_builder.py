from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import tempfile
import plotly.io as pio

def build_pdf_report(df, charts, kpis):
    """
    Génère un PDF complet avec :
    - Page de garde
    - KPI
    - Graphiques (PNG depuis Plotly)
    - Tableau final
    """

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal = styles["BodyText"]

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp.name, pagesize=A4, rightMargin=20, leftMargin=20)

    story = []

    # -----------------------------
    # PAGE DE GARDE
    # -----------------------------
    story.append(Paragraph("Berenbaum Law – Analyse complète", title_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Rapport généré automatiquement à partir des données de votre base Dropbox.", normal))
    story.append(Spacer(1, 40))

    # -----------------------------
    # KPI
    # -----------------------------
    story.append(Paragraph("<b>Indicateurs principaux :</b>", normal))
    story.append(Spacer(1, 12))

    kpi_table = [
        ["Dossiers", kpis["dossiers"]],
        ["Honoraires", kpis["honoraires"]],
        ["Autres frais", kpis["autres_frais"]],
        ["Facturé", kpis["facture"]],
        ["Encaissé", kpis["encaisse"]],
        ["Solde", kpis["solde"]],
    ]

    t = Table(kpi_table, colWidths=[5 * cm, 8 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ]))

    story.append(t)
    story.append(Spacer(1, 24))

    # -----------------------------
    # GRAPHIQUES
    # -----------------------------
    story.append(Paragraph("<b>Graphiques :</b>", normal))
    story.append(Spacer(1, 12))

    for fig in charts:
        img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.write_image(img_temp.name, width=600, height=350, scale=2)

        story.append(Image(img_temp.name, width=16*cm, height=9*cm))
        story.append(Spacer(1, 20))

    # -----------------------------
    # TABLEAU FINAL
    # -----------------------------
    story.append(Paragraph("<b>Données filtrées :</b>", normal))
    story.append(Spacer(1, 12))

    if len(df) > 0:
        table_data = [list(df.columns)] + df.values.tolist()
        table = Table(table_data, repeatRows=1)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))

        story.append(table)
    else:
        story.append(Paragraph("Aucune donnée après filtre.", normal))

    doc.build(story)

    return temp.name
