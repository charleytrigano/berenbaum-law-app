import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape

def generate_pdf_from_dataframe(df, title="Export PDF"):
    """
    Génère un PDF minimal contenant uniquement le tableau filtré.
    Retourne un buffer BytesIO prêt à être téléchargé.
    """

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))

    width, height = landscape(A4)

    # Titre
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, title)

    # Position de départ du tableau
    y = height - 80
    p.setFont("Helvetica", 9)

    # Dessin des titres de colonnes
    col_x = 30
    for col in df.columns:
        p.drawString(col_x, y, str(col))
        col_x += 120  # espacement horizontal

    y -= 20

    # Dessin des lignes
    for _, row in df.iterrows():
        col_x = 30
        for item in row:
            txt = str(item)
            p.drawString(col_x, y, txt[:20])  # limite 20 caractères / colonne
            col_x += 120
        y -= 15

        # Saut de page si trop bas
        if y < 40:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica", 9)

    p.save()
    buffer.seek(0)
    return buffer
