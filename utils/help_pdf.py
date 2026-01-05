from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from datetime import date
import io

def build_help_pdf_bytes(language="FR"):
    """
    Génère le PDF Aide Cabinet Interne (FR ou EN)
    Retourne bytes prêts à télécharger
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCenter",
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="Section",
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=10,
        spaceAfter=6
    ))

    story = []

    # =====================================================
    # TITRE
    # =====================================================
    title = "CABINET INTERNE — MANUEL UTILISATEUR"
    if language == "EN":
        title = "INTERNAL CABINET — USER MANUAL"

    story.append(Paragraph(title, styles["TitleCenter"]))
    story.append(Paragraph(
        f"Application de gestion des dossiers<br/>Date : {date.today().strftime('%d/%m/%Y')}",
        styles["Body"]
    ))
    story.append(Spacer(1, 20))

    # =====================================================
    # CONTENU
    # =====================================================
    sections_fr = [
        ("1. Objectif",
         "Cette application permet de gérer l’ensemble des dossiers clients du cabinet "
         "avec suivi administratif, financier, escrows, dossiers parents/fils, analyses et exports."),

        ("2. Navigation",
         "Toutes les pages sont accessibles via le menu latéral. "
         "Aucune connaissance technique n’est requise."),

        ("3. Dashboard",
         "Vue globale avec filtres dynamiques et KPI recalculés en temps réel."),

        ("4. Dossiers parents et fils",
         "Un dossier parent peut contenir plusieurs sous-dossiers. "
         "Les sous-dossiers peuvent avoir des visas différents."),

        ("5. Escrow — Règles officielles",
         "Tant que le dossier n’est ni accepté, ni refusé, ni annulé : "
         "TOUS les acomptes sont en escrow. "
         "Lorsque le dossier est finalisé, l’escrow passe à réclamer puis réclamé."),

        ("6. Modifier un dossier",
         "Gestion complète : facturation, acomptes, statuts, escrow, commentaires."),

        ("7. Analyses",
         "KPI avancés, comparaisons multi-années, dossiers soldés et non soldés."),

        ("8. Exports",
         "Exports Excel multi-feuilles et PDF (fiche dossier et fiche groupe)."),

        ("9. Bonnes pratiques",
         "Ne jamais modifier le JSON manuellement. "
         "Toujours vérifier les dates de paiement."),

        ("10. Support interne",
         "En cas de doute, se référer à ce manuel ou contacter l’administrateur interne.")
    ]

    sections_en = [
        ("1. Purpose",
         "This application manages all client cases including administrative, financial, "
         "escrow tracking, parent/child cases, analytics and exports."),

        ("2. Navigation",
         "All features are accessible from the sidebar. No technical knowledge required."),

        ("3. Dashboard",
         "Global view with dynamic filters and real-time KPIs."),

        ("4. Parent and child cases",
         "A parent case can contain multiple child cases with different visas."),

        ("5. Escrow — Official rules",
         "Until a case is accepted, refused or cancelled: ALL payments are held in escrow."),

        ("6. Edit case",
         "Full daily management: billing, payments, statuses, escrow, comments."),

        ("7. Analytics",
         "Advanced KPIs, multi-year comparisons, paid and unpaid cases."),

        ("8. Exports",
         "Excel multi-sheet exports and PDF reports."),

        ("9. Best practices",
         "Never manually edit the JSON. Always verify payment dates."),

        ("10. Internal support",
         "Refer to this manual or contact the internal administrator.")
    ]

    content = sections_fr if language == "FR" else sections_en

    for title, body in content:
        story.append(Paragraph(title, styles["Section"]))
        story.append(Paragraph(body, styles["Body"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()