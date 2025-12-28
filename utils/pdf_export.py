# utils/pdf_export.py
from __future__ import annotations

from io import BytesIO
from datetime import date, datetime

import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

import os


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _to_str(v) -> str:
    """Convertit n'importe quelle valeur en string safe PDF."""
    if v is None:
        return ""
    # Pandas / numpy
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass

    # datetime / date / pandas Timestamp
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    try:
        if isinstance(v, pd.Timestamp):
            return v.strftime("%Y-%m-%d")
    except Exception:
        pass

    return str(v)


def _to_money(v) -> str:
    try:
        x = float(v or 0)
    except Exception:
        x = 0.0
    return f"${x:,.2f}"


def _safe_logo_reader(path: str):
    try:
        if path and os.path.exists(path):
            return ImageReader(path)
    except Exception:
        pass
    return None


def _draw_kv(c: canvas.Canvas, x: float, y: float, label: str, value: str, max_w: float):
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"{label} :")
    c.setFont("Helvetica", 10)

    # simple wrap (largeur approximative)
    txt = value or ""
    if c.stringWidth(txt, "Helvetica", 10) <= max_w:
        c.drawString(x + 3.2 * cm, y, txt)
        return y - 0.55 * cm

    # wrap basique par mots
    words = txt.split(" ")
    line = ""
    lines = []
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 10) <= (max_w - 3.2 * cm):
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)

    yy = y
    for i, l in enumerate(lines):
        if i == 0:
            c.drawString(x + 3.2 * cm, yy, l)
        else:
            yy -= 0.55 * cm
            c.drawString(x + 3.2 * cm, yy, l)
    return yy - 0.55 * cm


# ---------------------------------------------------------
# Export PDF dossier (compat: retourne bytes OU écrit dans output)
# ---------------------------------------------------------
def export_dossier_pdf(dossier: dict, output: BytesIO | None = None) -> bytes | None:
    """
    Compatibilité maximale:
    - Si output est fourni (BytesIO), écrit dedans et retourne None.
    - Sinon retourne les bytes du PDF.
    """
    if not isinstance(dossier, dict):
        dossier = {}

    buf = output if output is not None else BytesIO()

    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    left = 2.0 * cm
    right = 2.0 * cm
    top = 1.6 * cm
    bottom = 2.0 * cm
    max_w = W - left - right

    # -----------------------------------------------------
    # Header (logo optionnel)
    # -----------------------------------------------------
    logo = _safe_logo_reader("assets/logo.png")
    y = H - top

    if logo is not None:
        c.drawImage(logo, left, y - 2.0 * cm, width=2.0 * cm, height=2.0 * cm, mask="auto")
        x_title = left + 2.5 * cm
    else:
        x_title = left

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_title, y - 0.6 * cm, "Fiche dossier (Interne)")

    c.setFont("Helvetica", 9)
    c.drawRightString(W - right, y - 0.7 * cm, datetime.now().strftime("%Y-%m-%d %H:%M"))

    c.setLineWidth(0.6)
    c.line(left, y - 2.3 * cm, W - right, y - 2.3 * cm)

    y = y - 3.0 * cm

    # -----------------------------------------------------
    # Données principales
    # -----------------------------------------------------
    dossier_n = _to_str(dossier.get("Dossier N", ""))
    nom = _to_str(dossier.get("Nom", ""))
    visa = _to_str(dossier.get("Visa", ""))
    cat = _to_str(dossier.get("Categories", ""))
    sous = _to_str(dossier.get("Sous-categories", ""))
    date_dossier = _to_str(dossier.get("Date", ""))

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, f"Dossier : {dossier_n} — {nom}")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    y = _draw_kv(c, left, y, "Date", date_dossier, max_w)
    y = _draw_kv(c, left, y, "Catégorie", cat, max_w)
    y = _draw_kv(c, left, y, "Sous-catégorie", sous, max_w)
    y = _draw_kv(c, left, y, "Visa", visa, max_w)

    y -= 0.3 * cm
    c.setLineWidth(0.3)
    c.line(left, y, W - right, y)
    y -= 0.7 * cm

    # -----------------------------------------------------
    # Finances
    # -----------------------------------------------------
    honoraires = dossier.get("Montant honoraires (US $)", 0)
    autres = dossier.get("Autres frais (US $)", 0)
    a1 = dossier.get("Acompte 1", 0)
    a2 = dossier.get("Acompte 2", 0)
    a3 = dossier.get("Acompte 3", 0)
    a4 = dossier.get("Acompte 4", 0)

    try:
        total_facture = float(honoraires or 0) + float(autres or 0)
    except Exception:
        total_facture = 0.0

    try:
        total_encaisse = float(a1 or 0) + float(a2 or 0) + float(a3 or 0) + float(a4 or 0)
    except Exception:
        total_encaisse = 0.0

    solde = total_facture - total_encaisse

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Finances")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    y = _draw_kv(c, left, y, "Honoraires", _to_money(honoraires), max_w)
    y = _draw_kv(c, left, y, "Autres frais", _to_money(autres), max_w)
    y = _draw_kv(c, left, y, "Total facturé", _to_money(total_facture), max_w)
    y = _draw_kv(c, left, y, "Total encaissé", _to_money(total_encaisse), max_w)
    y = _draw_kv(c, left, y, "Solde dû", _to_money(solde), max_w)

    y -= 0.3 * cm
    c.setLineWidth(0.3)
    c.line(left, y, W - right, y)
    y -= 0.7 * cm

    # -----------------------------------------------------
    # Acomptes + dates + modes (si présents)
    # -----------------------------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Paiements (Acomptes)")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    for i in range(1, 5):
        ai = dossier.get(f"Acompte {i}", 0)
        di = dossier.get(f"Date Acompte {i}", dossier.get(f"Date Paiement {i}", ""))
        mi = dossier.get(f"Mode Acompte {i}", dossier.get("mode de paiement", ""))

        label = f"Acompte {i}"
        val = f"{_to_money(ai)}  |  Date: {_to_str(di)}  |  Mode: {_to_str(mi)}"
        y = _draw_kv(c, left, y, label, val, max_w)

        if y < bottom + 3 * cm:
            c.showPage()
            y = H - top - 1.0 * cm

    y -= 0.3 * cm
    c.setLineWidth(0.3)
    c.line(left, y, W - right, y)
    y -= 0.7 * cm

    # -----------------------------------------------------
    # Statuts + Escrow
    # -----------------------------------------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Statuts & Escrow")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)

    def b(key):
        v = dossier.get(key, False)
        return "Oui" if str(v).strip().lower() in ["true", "1", "yes", "oui"] or v is True else "Non"

    y = _draw_kv(c, left, y, "Dossier envoyé", b("Dossier envoye"), max_w)
    y = _draw_kv(c, left, y, "Dossier accepté", b("Dossier accepte"), max_w)
    y = _draw_kv(c, left, y, "Dossier refusé", b("Dossier refuse"), max_w)
    y = _draw_kv(c, left, y, "Dossier annulé", b("Dossier Annule"), max_w)
    y = _draw_kv(c, left, y, "RFE", b("RFE"), max_w)

    y = _draw_kv(c, left, y, "Escrow actif", b("Escrow"), max_w)
    y = _draw_kv(c, left, y, "Escrow à réclamer", b("Escrow_a_reclamer"), max_w)
    y = _draw_kv(c, left, y, "Escrow réclamé", b("Escrow_reclame"), max_w)
    y = _draw_kv(c, left, y, "Montant escrow (règle)", _to_money(dossier.get("Acompte 1", 0)), max_w)

    # -----------------------------------------------------
    # Commentaire
    # -----------------------------------------------------
    y -= 0.3 * cm
    c.setLineWidth(0.3)
    c.line(left, y, W - right, y)
    y -= 0.7 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Commentaire")
    y -= 0.7 * cm

    c.setFont("Helvetica", 10)
    comment = _to_str(dossier.get("Commentaire", ""))
    for line in comment.split("\n"):
        if y < bottom + 1.5 * cm:
            c.showPage()
            y = H - top - 1.0 * cm
            c.setFont("Helvetica", 10)
        # wrap simple
        for l in line.split("\n"):
            y = _draw_kv(c, left, y, "", l, max_w)

    c.save()

    if output is None:
        return buf.getvalue()
    return None