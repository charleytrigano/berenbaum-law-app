from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

def export_dossier_pdf(dossier):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # ---------------------------------------------------------
    # Styles 
    # ---------------------------------------------------------
    title_color = colors.HexColor("#1F2937")  # Gris bleu VisionOS
    section_color = colors.HexColor("#4B5563")
    text_color = colors.HexColor("#111827")

    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, 750, f"Dossier {int(dossier['Dossier N'])} — {dossier['Nom']}")

    # ---------------------------------------------------------
    # BADGES (Statut + Escrow)
    # ---------------------------------------------------------
    y = 720
    def badge(text, color):
        c.setFillColor(colors.HexColor(color))
        c.roundRect(40, y, 120, 22, 6, fill=True, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y + 6, text)
        return y - 30

    # Statut
    if dossier.get("Dossier envoye"):
        y = badge("Envoyé", "#2563EB")
    elif dossier.get("Dossier accepte"):
        y = badge("Accepté", "#059669")
    elif dossier.get("Dossier refuse"):
        y = badge("Refusé", "#DC2626")
    else:
        y = badge("En cours", "#6B7280")

    # Escrow
    if dossier.get("Escrow"):
        y = badge("Escrow en cours", "#FACC15")
    elif dossier.get("Escrow_a_reclamer"):
        y = badge("Escrow à réclamer", "#EA580C")
    elif dossier.get("Escrow_reclame"):
        y = badge("Escrow réclamé", "#22C55E")
    else:
        y = badge("Pas d'Escrow", "#9CA3AF")

    # ---------------------------------------------------------
    # SECTION : Informations générales
    # ---------------------------------------------------------
    c.setFillColor(section_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Informations générales")
    y -= 25

    c.setFillColor(text_color)
    c.setFont("Helvetica", 11)
    infos = [
        ("Catégorie", dossier.get("Categories","")),
        ("Sous-catégorie", dossier.get("Sous-categories","")),
        ("Visa", dossier.get("Visa","")),
        ("Date de création", dossier.get("Date","")),
    ]

    for label, value in infos:
        c.drawString(40, y, f"{label} : {value}")
        y -= 18

    # ---------------------------------------------------------
    # SECTION : Facturation
    # ---------------------------------------------------------
    y -= 10
    c.setFillColor(section_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Facturation")
    y -= 25

    honoraires = float(dossier.get("Montant honoraires (US $)", 0))
    frais = float(dossier.get("Autres frais (US $)", 0))
    total = honoraires + frais

    c.setFont("Helvetica", 11)
    c.setFillColor(text_color)
    c.drawString(40, y, f"Honoraires : ${honoraires:,.2f}")
    y -= 18
    c.drawString(40, y, f"Autres frais : ${frais:,.2f}")
    y -= 18
    c.drawString(40, y, f"Total : ${total:,.2f}")
    y -= 30

    # ---------------------------------------------------------
    # SECTION : Acomptes
    # ---------------------------------------------------------
    acomptes = [
        ("Acompte 1", dossier.get("Acompte 1", 0)),
        ("Acompte 2", dossier.get("Acompte 2", 0)),
        ("Acompte 3", dossier.get("Acompte 3", 0)),
        ("Acompte 4", dossier.get("Acompte 4", 0)),
    ]

    c.setFillColor(section_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Acomptes")
    y -= 25

    total_acomptes = 0
    c.setFont("Helvetica", 11)
    c.setFillColor(text_color)

    for label, val in acomptes:
        if float(val) > 0:
            c.drawString(40, y, f"{label} : ${float(val):,.2f}")
            y -= 18
            total_acomptes += float(val)

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, y, f"Total acomptes : ${total_acomptes:,.2f}")
    y -= 18

    solde = total - total_acomptes
    c.drawString(40, y, f"Solde restant : ${solde:,.2f}")
    y -= 30

    # ---------------------------------------------------------
    # SECTION : Timeline
    # ---------------------------------------------------------
    c.setFillColor(section_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Timeline")
    y -= 25

    timeline_fields = [
        ("Date envoi", dossier.get("Date envoi","")),
        ("Date acceptation", dossier.get("Date acceptation","")),
        ("Date refus", dossier.get("Date refus","")),
        ("Date annulation", dossier.get("Date annulation","")),
        ("Date RFE", dossier.get("Date reclamation","")),
    ]

    c.setFont("Helvetica", 11)
    c.setFillColor(text_color)

    for label, val in timeline_fields:
        if val not in ["", None, "None"]:
            c.drawString(40, y, f"{label} : {val}")
            y -= 18

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
