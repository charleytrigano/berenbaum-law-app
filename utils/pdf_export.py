from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def export_escrow_pdf(df, filename):
    """
    Génère un PDF simple et fiable des escrows fournis.
    df doit contenir : Dossier N, Nom, Montant Escrow
    """

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Berenbaum Law — Escrow Report")

    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y -= 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "Dossier")
    c.drawString(140, y, "Client")
    c.drawRightString(500, y, "Montant (USD)")

    y -= 15
    c.line(40, y, 500, y)

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
        c.drawString(140, y, row.get("Nom", ""))
        c.drawRightString(500, y, f"${montant:,.2f}")

    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(500, y, f"TOTAL ESCROW : ${total:,.2f}")

    c.save()