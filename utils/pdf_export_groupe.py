from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import io


def export_groupe_pdf(parent_id, parent_row, children_rows):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, f"Groupe de dossiers {parent_id}")
    y -= 1 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Exporté le {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 1.5 * cm

    # -------------------------------------------------
    # DOSSIER PARENT
    # -------------------------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "DOSSIER PARENT")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    for k in ["Nom", "Categories", "Sous-categories", "Visa", "Commentaire"]:
        c.drawString(2 * cm, y, f"{k} : {parent_row.get(k, '')}")
        y -= 0.5 * cm

    y -= 0.5 * cm

    # -------------------------------------------------
    # SOUS-DOSSIERS
    # -------------------------------------------------
    for row in children_rows:
        if y < 4 * cm:
            c.showPage()
            y = height - 2 * cm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, f"Dossier {row['Dossier N']}")
        y -= 0.6 * cm

        c.setFont("Helvetica", 9)

        fields = [
            "Nom", "Categories", "Sous-categories", "Visa",
            "Montant honoraires (US $)", "Autres frais (US $)",
            "Acompte 1", "Acompte 2", "Acompte 3", "Acompte 4"
        ]

        for f in fields:
            c.drawString(2 * cm, y, f"{f} : {row.get(f, '')}")
            y -= 0.45 * cm

        y -= 0.5 * cm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer