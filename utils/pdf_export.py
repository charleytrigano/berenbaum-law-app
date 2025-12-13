from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime

def export_dossier_pdf(df, dossier_parent: int, file_path: str):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 2 * cm

    def draw(text, bold=False):
        nonlocal y
        if bold:
            c.setFont("Helvetica-Bold", 11)
        else:
            c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y, text)
        y -= 0.6 * cm

    # -------------------------------------------------
    draw("BERENBAUM LAW", bold=True)
    draw(f"Dossier {dossier_parent}")
    draw(f"Export généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= cm

    subset = df[df["Dossier Parent"] == dossier_parent]

    for _, r in subset.iterrows():
        draw(f"Dossier : {r['Dossier N']}", bold=True)
        draw(f"Client : {r.get('Nom', '')}")
        draw(f"Visa : {r.get('Visa', '')}")
        draw(f"Honoraires : ${r.get('Montant honoraires (US $)', 0):,.2f}")
        draw(f"Acomptes : ${sum([
            r.get('Acompte 1',0),
            r.get('Acompte 2',0),
            r.get('Acompte 3',0),
            r.get('Acompte 4',0)
        ]):,.2f}")
        draw(f"Escrow : {'Oui' if r.get('Escrow') else 'Non'}")
        y -= 0.4 * cm

        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm

    # -------------------------------------------------
    y -= cm
    draw("TOTAUX CONSOLIDÉS", bold=True)

    total_h = subset["Montant honoraires (US $)"].sum()
    total_f = subset["Autres frais (US $)"].sum()
    total_enc = (
        subset["Acompte 1"].sum() +
        subset["Acompte 2"].sum() +
        subset["Acompte 3"].sum() +
        subset["Acompte 4"].sum()
    )

    draw(f"Total honoraires : ${total_h:,.2f}")
    draw(f"Total frais : ${total_f:,.2f}")
    draw(f"Total encaissé : ${total_enc:,.2f}")
    draw(f"Solde dû : ${(total_h + total_f - total_enc):,.2f}")

    c.save()