from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


# =========================================================
# 📄 EXPORT ESCROW PDF
# =========================================================
def export_escrow_pdf(df, filename):
    """
    Génère un PDF des escrows.
    df doit contenir : Dossier N, Nom, Montant Escrow
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Berenbaum Law — Escrow Report")

    y -= 20
    c.setFont("Helvetica", 9)
    c.drawString(40, y, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Dossier")
    c.drawString(120, y, "Client")
    c.drawRightString(520, y, "Montant (USD)")

    y -= 10
    c.line(40, y, 520, y)

    total = 0
    c.setFont("Helvetica", 10)

    for _, row in df.iterrows():
        if y < 60:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)

        montant = float(row.get("Montant Escrow", 0))
        total += montant

        y -= 18
        c.drawString(40, y, str(row.get("Dossier N", "")))
        c.drawString(120, y, row.get("Nom", ""))
        c.drawRightString(520, y, f"${montant:,.2f}")

    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(520, y, f"TOTAL ESCROW : ${total:,.2f}")

    c.save()


# =========================================================
# 📄 EXPORT FICHE DOSSIER PDF
# =========================================================
def export_dossier_pdf(dossier: dict, filename: str):
    """
    Génère un PDF individuel pour un dossier client.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Berenbaum Law — Fiche Dossier")

    y -= 25
    c.setFont("Helvetica", 9)
    c.drawString(40, y, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Dossier N° {dossier.get('Dossier N', '')}")

    y -= 20
    c.setFont("Helvetica", 11)

    def line(label, value):
        nonlocal y
        y -= 18
        c.drawString(40, y, f"{label} :")
        c.drawString(180, y, str(value))

    line("Nom", dossier.get("Nom", ""))
    line("Date", dossier.get("Date", ""))
    line("Catégorie", dossier.get("Categories", ""))
    line("Sous-catégorie", dossier.get("Sous-categories", ""))
    line("Visa", dossier.get("Visa", ""))

    y -= 15
    c.line(40, y, 520, y)

    line("Honoraires", f"${dossier.get('Montant honoraires (US $)', 0):,.2f}")
    line("Autres frais", f"${dossier.get('Autres frais (US $)', 0):,.2f}")

    total = (
        float(dossier.get("Montant honoraires (US $)", 0))
        + float(dossier.get("Autres frais (US $)", 0))
    )
    line("Total facturé", f"${total:,.2f}")

    y -= 20
    c.line(40, y, 520, y)

    line("Acompte 1", dossier.get("Acompte 1", 0))
    line("Acompte 2", dossier.get("Acompte 2", 0))
    line("Acompte 3", dossier.get("Acompte 3", 0))
    line("Acompte 4", dossier.get("Acompte 4", 0))

    y -= 20
    line("Commentaire", dossier.get("Commentaire", ""))

    c.save()