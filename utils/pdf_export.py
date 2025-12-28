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
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
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

def _draw_kv(c, x, y, label, value, max_w, offset=3.2*cm):
    """Dessine une ligne clé/valeur (label : value)."""
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"{label} :")
    c.setFont("Helvetica", 10)
    c.drawString(x + offset, y, value or "")
    return y - 0.5 * cm

# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------
def export_dossier_pdf(dossier: dict, output: BytesIO | None = None):
    buf = output if output else BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4
    left, right = 2*cm, 2*cm
    top, bottom = 1.5*cm, 2.0*cm
    max_w = W - left - right

    # ------------------ Header -------------------
    logo = _safe_logo_reader("assets/logo.png")
    y = H - top
    if logo:
        c.drawImage(logo, left, y - 2*cm, width=2*cm, height=2*cm, mask="auto")
        x_title = left + 2.5*cm
    else:
        x_title = left

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_title, y - 0.6*cm, "Fiche dossier – Cabinet interne")
    c.setFont("Helvetica", 9)
    c.drawRightString(W - right, y - 0.7*cm, datetime.now().strftime("%Y-%m-%d %H:%M"))
    c.line(left, y - 2.3*cm, W - right, y - 2.3*cm)
    y -= 3.0*cm

    # ------------------ Données principales -------------------
    dossier_n = _to_str(dossier.get("Dossier N"))
    nom = _to_str(dossier.get("Nom"))
    visa = _to_str(dossier.get("Visa"))
    cat = _to_str(dossier.get("Categories"))
    sous = _to_str(dossier.get("Sous-categories"))
    date_dossier = _to_str(dossier.get("Date"))

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, f"Dossier {dossier_n} — {nom}")
    y -= 0.8*cm
    c.setFont("Helvetica", 10)
    y = _draw_kv(c, left, y, "Date", date_dossier, max_w)
    y = _draw_kv(c, left, y, "Catégorie", cat, max_w)
    y = _draw_kv(c, left, y, "Sous-catégorie", sous, max_w)
    y = _draw_kv(c, left, y, "Visa", visa, max_w)
    c.line(left, y, W - right, y)
    y -= 0.8*cm

    # ------------------ Finances -------------------
    honoraires = dossier.get("Montant honoraires (US $)", 0)
    autres = dossier.get("Autres frais (US $)", 0)
    a1 = dossier.get("Acompte 1", 0)
    a2 = dossier.get("Acompte 2", 0)
    a3 = dossier.get("Acompte 3", 0)
    a4 = dossier.get("Acompte 4", 0)

    total_facture = float(honoraires or 0) + float(autres or 0)
    total_encaisse = float(a1 or 0) + float(a2 or 0) + float(a3 or 0) + float(a4 or 0)
    solde = total_facture - total_encaisse

    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Finances")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    y = _draw_kv(c, left, y, "Honoraires", _to_money(honoraires), max_w)
    y = _draw_kv(c, left, y, "Autres frais", _to_money(autres), max_w)
    y = _draw_kv(c, left, y, "Total facturé", _to_money(total_facture), max_w)
    y = _draw_kv(c, left, y, "Total encaissé", _to_money(total_encaisse), max_w)
    y = _draw_kv(c, left, y, "Solde dû", _to_money(solde), max_w)
    c.line(left, y, W - right, y)
    y -= 0.8*cm

    # ------------------ Paiements -------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Paiements (Acomptes)")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    for i in range(1, 5):
        ai = dossier.get(f"Acompte {i}", 0)
        di = dossier.get(f"Date Acompte {i}", dossier.get(f"Date Paiement {i}", ""))
        mi = dossier.get(f"Mode Acompte {i}", dossier.get("mode de paiement", ""))
        val = f"{_to_money(ai)}  |  Date: {_to_str(di)}  |  Mode: {_to_str(mi)}"
        y = _draw_kv(c, left, y, f"Acompte {i}", val, max_w)
    c.line(left, y, W - right, y)
    y -= 0.8*cm

    # ------------------ Statuts & Escrow -------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Statuts & Escrow")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)

    def b(k):
        v = dossier.get(k, False)
        return "Oui" if str(v).lower() in ["true", "1", "yes", "oui"] else "Non"

    offset_right = 5.5 * cm  # plus décalé à droite pour meilleure lisibilité

    y = _draw_kv(c, left, y, "Dossier envoyé", b("Dossier envoye"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Dossier accepté", b("Dossier accepte"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Dossier refusé", b("Dossier refuse"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Dossier annulé", b("Dossier Annule"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "RFE", b("RFE"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Escrow actif", b("Escrow"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Escrow à réclamer", b("Escrow_a_reclamer"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Escrow réclamé", b("Escrow_reclame"), max_w, offset=offset_right)
    y = _draw_kv(c, left, y, "Montant escrow (Acompte 1)", _to_money(a1), max_w, offset=offset_right)
    c.line(left, y, W - right, y)
    y -= 0.8*cm

    # ------------------ Commentaire -------------------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left, y, "Commentaire")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    comment = _to_str(dossier.get("Commentaire", ""))
    for line in comment.split("\n"):
        c.drawString(left + 1*cm, y, line)
        y -= 0.45*cm

    c.save()
    if output is None:
        return buf.getvalue()
    return None