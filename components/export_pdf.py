from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import tempfile
import os

def generate_pdf(row):
    """ Génère un PDF propre et retourne le chemin du fichier """

    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Heading1"]
    title_style.textColor = "#003366"

    text_style = styles["BodyText"]
    text_style.fontSize = 11

    # TEMP FILE
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"Dossier_{row['Dossier N']}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=letter)

    # -------- TITLE --------
    story.append(Paragraph(f"Dossier {row['Dossier N']} – {row['Nom']}", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # -------- INFO GÉNÉRALES --------
    story.append(Paragraph("<b>Informations générales</b>", styles["Heading2"]))
    info = f"""
        <b>Nom :</b> {row['Nom']}<br/>
        <b>Catégorie :</b> {row.get('Categories', '')}<br/>
        <b>Sous-catégorie :</b> {row.get('Sous-categories', '')}<br/>
        <b>Visa :</b> {row.get('Visa', '')}<br/>
        <b>Date de création :</b> {row.get('Date', '')}<br/>
    """
    story.append(Paragraph(info, text_style))
    story.append(Spacer(1, 0.2 * inch))

    # -------- FACTURATION --------
    hon = float(row.get("Montant honoraires (US $)", 0))
    frais = float(row.get("Autres frais (US $)", 0))
    total = hon + frais

    acs = sum([
        float(row.get("Acompte 1", 0)),
        float(row.get("Acompte 2", 0)),
        float(row.get("Acompte 3", 0)),
        float(row.get("Acompte 4", 0)),
    ])

    solde = total - acs
    statut = "Payé" if solde <= 0 else "Partiel" if acs > 0 else "Impayé"

    story.append(Paragraph("<b>Facturation</b>", styles["Heading2"]))
    fact = f"""
        <b>Honoraires :</b> ${hon:,.2f}<br/>
        <b>Autres frais :</b> ${frais:,.2f}<br/>
        <b>Total :</b> ${total:,.2f}<br/>
        <b>Total payé :</b> ${acs:,.2f}<br/>
        <b>Solde restant :</b> ${solde:,.2f}<br/>
        <b>Statut :</b> {statut}<br/>
    """
    story.append(Paragraph(fact, text_style))
    story.append(Spacer(1, 0.3 * inch))

    # -------- TIMELINE --------
    story.append(Paragraph("<b>Timeline</b>", styles["Heading2"]))
    timeline = ""

    if row.get("Date"):
        timeline += f"📄 Création : {row.get('Date')}<br/>"

    if row.get("Escrow"):
        timeline += "💰 Escrow ouvert<br/>"

    if row.get("Dossier envoye"):
        timeline += f"📤 Envoyé : {row.get('Date envoi', '')}<br/>"

    story.append(Paragraph(timeline or "Aucun événement.", text_style))

    doc.build(story)

    return filename
