from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd


def export_escrow_pdf(df: pd.DataFrame, filename: str):
    """
    Génère un PDF fiable des escrows.
    Colonnes requises :
    - Dossier N
    - Nom
    - Montant Escrow
    """

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 40

    # En-tête
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Berenbaum Law — Escrow Report")

    y -= 22
    c.setFont("Helvetica", 10)
    c.drawString(
        40,
        y,
        f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )

    # Tableau
    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Dossier")
    c.drawString(140, y, "Client")
    c.drawRightString(520, y, "Montant (USD)")
    y -= 5
    c.line(40, y, 520, y)

    total = 0.0
    c.setFont("Helvetica", 10)

    for _, row in df.iterrows():
        if y < 60:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)

        montant = float(row.get("Montant Escrow", 0) or 0)
        total += montant

        y -= 18
        c.drawString(40, y, str(row.get("Dossier N", "")))
        c.drawString(140, y, str(row.get("Nom", "")))
        c.drawRightString(520, y, f"${montant:,.2f}")

    # Total
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(520, y, f"TOTAL ESCROW : ${total:,.2f}")

    c.save()