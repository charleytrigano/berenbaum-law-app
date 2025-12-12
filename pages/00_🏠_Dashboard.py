from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import date


def export_dossier_pdf(parent_id, dossiers, output_path):
    """
    parent_id : '12937'
    dossiers  : liste de dicts (12937, 12937-1, ...)
    """

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, f"Dossier {parent_id} — Récapitulatif")
    y -= 1.2 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Date d’export : {date.today().isoformat()}")
    y -= 1.5 * cm

    # -------------------------------------------------
    # TABLE HEADER
    # -------------------------------------------------
    c.setFont("Helvetica-Bold", 9)
    headers = [
        "Dossier",
        "Honoraires",
        "Frais",
        "Facturé",
        "Encaissé",
        "Solde",
        "Escrow",
    ]
    x_positions = [2, 4.5, 6.5, 8.5, 10.5, 12.5, 14.5]

    for h, x in zip(headers, x_positions):
        c.drawString(x * cm, y, h)

    y -= 0.6 * cm
    c.line(2 * cm, y, 19 * cm, y)
    y -= 0.4 * cm

    # -------------------------------------------------
    # CONTENT
    # -------------------------------------------------
    total_h = total_f = total_fact = total_enc = total_solde = total_escrow = 0

    c.setFont("Helvetica", 9)

    for d in dossiers:
        honoraires = float(d.get("Montant honoraires (US $)", 0))
        frais = float(d.get("Autres frais (US $)", 0))
        fact = honoraires + frais

        encaiss = sum(float(d.get(f"Acompte {i}", 0)) for i in range(1, 5))
        solde = fact - encaiss

        escrow = float(d.get("Acompte 1", 0)) if d.get("Escrow") else 0

        values = [
            d.get("Dossier N"),
            f"{honoraires:,.2f}",
            f"{frais:,.2f}",
            f"{fact:,.2f}",
            f"{encaiss:,.2f}",
            f"{solde:,.2f}",
            f"{escrow:,.2f}",
        ]

        for v, x in zip(values, x_positions):
            c.drawString(x * cm, y, str(v))

        total_h += honoraires
        total_f += frais
        total_fact += fact
        total_enc += encaiss
        total_solde += solde
        total_escrow += escrow

        y -= 0.45 * cm

        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 9)

    # -------------------------------------------------
    # TOTALS
    # -------------------------------------------------
    y -= 0.6 * cm
    c.line(2 * cm, y, 19 * cm, y)
    y -= 0.5 * cm

    c.setFont("Helvetica-Bold", 9)
    totals = [
        "TOTAL",
        f"{total_h:,.2f}",
        f"{total_f:,.2f}",
        f"{total_fact:,.2f}",
        f"{total_enc:,.2f}",
        f"{total_solde:,.2f}",
        f"{total_escrow:,.2f}",
    ]

    for t, x in zip(totals, x_positions):
        c.drawString(x * cm, y, t)

    c.showPage()
    c.save()
