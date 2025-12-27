# pages/10_❓_Aide.py
import os
from io import BytesIO
from datetime import datetime

import streamlit as st
from utils.sidebar import render_sidebar

# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(page_title="❓ Aide", page_icon="❓", layout="wide")
render_sidebar()

# =========================================================
# PARAM CABINET
# =========================================================
DEFAULT_CABINET_NAME = "Berenbaum Law"
DEFAULT_LOGO_PATH = "assets/logo.png"

if "cabinet_name" not in st.session_state:
    st.session_state["cabinet_name"] = DEFAULT_CABINET_NAME

if "cabinet_logo_path" not in st.session_state:
    st.session_state["cabinet_logo_path"] = DEFAULT_LOGO_PATH

# =========================================================
# CONTENUS PAR DÉFAUT (tu peux remplacer par ton aide complète)
# =========================================================
DEFAULT_HELP_FR = """# Aide – Berenbaum Law App (Cabinet interne)

> Cette page permet de consulter, éditer et exporter l’Aide au format PDF.

## Sommaire
1. Présentation
2. Accès / Navigation
3. Dashboard
4. Liste des dossiers
5. Nouveau dossier (Parent / Fils)
6. Modifier dossier
7. Escrow
8. Analyses
9. Tarifs
10. Exports (Excel/JSON/PDF)
11. Paramètres & dépannage
12. FAQ

## 1) Présentation
Décrire ici le fonctionnement général.

## 2) Accès / Navigation
- Sidebar: liens vers chaque page
- Filtres: année, catégorie, sous-catégorie, visa, statuts

## 3) Dashboard
- KPI: nombre dossiers, honoraires, frais, total facturé, encaissé, solde, escrow total
- Tableau dossiers (parents & fils)

## 4) Liste des dossiers
- Filtrage multi-année
- Export CSV

## 5) Nouveau dossier
- Parent: 13068
- Fils: 13068-1, 13068-2
- Catégorie / sous-catégorie / visa obligatoires
- Acompte 1: montant + date paiement + mode de règlement

## 6) Modifier dossier
- Modification complète des infos
- Acomptes 1→4 + dates + modes
- Statuts + dates associées
- Commentaire

## 7) Escrow
- 3 états: Escrow actif → Escrow à réclamer → Escrow réclamé
- Montant escrow = Acompte 1 uniquement

## 8) Analyses
- KPI + comparaisons temporelles
- Filtres: statuts + dossiers soldés / non soldés / <0

## 9) Tarifs
- Tarifs par visa avec historique

## 10) Exports
- Export JSON ↔ Excel multi-feuilles
- Export PDF par état (si activé)

## 11) Paramètres & dépannage
- Diagnostic Dropbox
- Import Excel → JSON
- Nettoyage avancé

## 12) FAQ
- KPI incohérents: vérifier filtres
- Escrow: correspond à Acompte 1
"""

DEFAULT_HELP_EN = """# Help – Berenbaum Law App (Internal)

## Table of contents
1. Overview
2. Navigation
3. Dashboard
4. Case list
5. New case (Parent / Child)
6. Edit case
7. Escrow
8. Analytics
9. Pricing
10. Exports
11. Settings & troubleshooting
12. FAQ

## 1) Overview
Describe how the app works.

## 2) Navigation
Use the sidebar to access pages.

## 3) Dashboard
KPIs, filters, and the parent/child list.

## 7) Escrow
3 states: Active → To claim → Claimed
Escrow amount = Deposit 1 only
"""

if "help_fr" not in st.session_state:
    st.session_state["help_fr"] = DEFAULT_HELP_FR

if "help_en" not in st.session_state:
    st.session_state["help_en"] = DEFAULT_HELP_EN

# =========================================================
# PDF HELPERS
# =========================================================
def register_font() -> str:
    """
    Optionnel: si assets/DejaVuSans.ttf existe, meilleure compatibilité accents.
    """
    try:
        ttf_path = "assets/DejaVuSans.ttf"
        if os.path.exists(ttf_path):
            pdfmetrics.registerFont(TTFont("DejaVuSans", ttf_path))
            return "DejaVuSans"
    except Exception:
        pass
    return "Helvetica"


def safe_image(path: str):
    try:
        if path and os.path.exists(path):
            return ImageReader(path)
    except Exception:
        pass
    return None


def wrap_text(c, text: str, font: str, size: int, max_width: float):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build_pdf(
    content: str,
    lang_label: str,
    cabinet_name: str,
    logo_path: str,
    title: str,
    include_branding: bool,
    images: list,
) -> bytes:
    font = register_font()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    left = 2.0 * cm
    right = 2.0 * cm
    top = 1.6 * cm
    bottom = 2.0 * cm
    max_w = W - left - right

    body_size = 10
    lh = 14

    logo = safe_image(logo_path) if include_branding else None

    def header():
        y_top = H - top

        if include_branding:
            # logo
            if logo is not None:
                lw = 2.0 * cm
                lh_img = 2.0 * cm
                c.drawImage(logo, left, y_top - lh_img, width=lw, height=lh_img, mask="auto")
                x_txt = left + lw + 0.6 * cm
            else:
                x_txt = left

            # cabinet
            c.setFont(font, 14)
            c.drawString(x_txt, y_top - 0.6 * cm, (cabinet_name or "")[:80])

            # title
            c.setFont(font, 12)
            c.drawString(x_txt, y_top - 1.25 * cm, title[:95])

            # separator
            c.setLineWidth(0.5)
            c.line(left, y_top - 2.2 * cm, W - right, y_top - 2.2 * cm)
            return y_top - 2.7 * cm

        # sans branding
        c.setFont(font, 14)
        c.drawString(left, y_top - 0.8 * cm, title[:95])
        c.setLineWidth(0.5)
        c.line(left, y_top - 1.4 * cm, W - right, y_top - 1.4 * cm)
        return y_top - 2.0 * cm

    def footer(page_num: int):
        c.setFont(font, 8)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        right_txt = f"{lang_label} – {stamp} – p.{page_num}"
        c.drawString(left, bottom - 12, "Document interne cabinet" if include_branding else "Document")
        c.drawRightString(W - right, bottom - 12, right_txt)

    page = 1
    y = header()
    c.setFont(font, body_size)

    lines = content.replace("\r\n", "\n").split("\n")

    def new_page():
        nonlocal y, page
        footer(page)
        c.showPage()
        page += 1
        y = header()
        c.setFont(font, body_size)

    # Render text (simple markdown-like)
    for raw in lines:
        s = raw.rstrip()

        if s.strip() == "":
            y -= lh
            if y < bottom:
                new_page()
            continue

        # headings
        if s.startswith("# "):
            c.setFont(font, 14)
            y -= 6
            for l in wrap_text(c, s[2:].strip(), font, 14, max_w):
                if y < bottom:
                    new_page()
                    c.setFont(font, 14)
                c.drawString(left, y, l)
                y -= lh
            c.setFont(font, body_size)
            continue

        if s.startswith("## "):
            c.setFont(font, 12)
            y -= 4
            for l in wrap_text(c, s[3:].strip(), font, 12, max_w):
                if y < bottom:
                    new_page()
                    c.setFont(font, 12)
                c.drawString(left, y, l)
                y -= lh
            c.setFont(font, body_size)
            continue

        if s.startswith("### "):
            c.setFont(font, 11)
            y -= 2
            for l in wrap_text(c, s[4:].strip(), font, 11, max_w):
                if y < bottom:
                    new_page()
                    c.setFont(font, 11)
                c.drawString(left, y, l)
                y -= lh
            c.setFont(font, body_size)
            continue

        text = "• " + s[2:].strip() if s.startswith("- ") else s

        for l in wrap_text(c, text, font, body_size, max_w):
            if y < bottom:
                new_page()
            c.drawString(left, y, l)
            y -= lh

    # Insert images section (optional)
    if images:
        if y < bottom + 6 * cm:
            new_page()

        c.setFont(font, 12)
        c.drawString(left, y, "Annexes – Captures d’écran")
        y -= (lh + 6)

        for img_bytes, name in images:
            try:
                img = ImageReader(BytesIO(img_bytes))
                # fit width
                img_max_w = max_w
                img_max_h = 12 * cm
                # draw with fixed box; reportlab preserves aspect if we compute sizes crudely:
                # We'll render in a box img_max_w x img_max_h.
                if y < bottom + img_max_h:
                    new_page()
                    c.setFont(font, 10)

                c.setFont(font, 9)
                c.drawString(left, y, f"{name}")
                y -= 12

                c.drawImage(img, left, y - img_max_h, width=img_max_w, height=img_max_h, preserveAspectRatio=True, anchor="sw")
                y -= (img_max_h + 18)

            except Exception:
                # ignore bad images
                continue

    footer(page)
    c.save()
    return buf.getvalue()


# =========================================================
# UI
# =========================================================
st.markdown("## ❓ Aide – Consultation / Édition / Export PDF")

# Header with logo + name (in page)
top_l, top_r = st.columns([1, 5])
with top_l:
    lp = st.session_state["cabinet_logo_path"]
    if lp and os.path.exists(lp):
        st.image(lp, width=120)
with top_r:
    st.markdown(f"### {st.session_state['cabinet_name']}")
    st.caption("Page Aide : édition du contenu + export PDF (FR / EN) + captures d’écran optionnelles")

st.markdown("---")

with st.expander("⚙️ Paramètres (logo / nom cabinet / options PDF)", expanded=False):
    st.session_state["cabinet_name"] = st.text_input("Nom du cabinet", value=st.session_state["cabinet_name"])
    st.session_state["cabinet_logo_path"] = st.text_input("Chemin du logo", value=st.session_state["cabinet_logo_path"])
    if st.session_state["cabinet_logo_path"] and not os.path.exists(st.session_state["cabinet_logo_path"]):
        st.warning("Logo introuvable : le PDF sera généré sans logo (ou en mode sans en-tête).")

col1, col2, col3 = st.columns(3)
lang = col1.selectbox("Langue", ["Français", "English"], index=0)
mode = col2.selectbox("Mode", ["Édition", "Lecture"], index=0)
pdf_mode = col3.selectbox("PDF", ["Cabinet interne (logo + nom)", "Neutre (sans en-tête)"], index=0)

content_key = "help_fr" if lang == "Français" else "help_en"

st.markdown("### ✍️ Contenu de l’aide")
if mode == "Édition":
    st.session_state[content_key] = st.text_area(
        "Texte (Markdown simple) – modifiable",
        value=st.session_state[content_key],
        height=560
    )
else:
    st.markdown(st.session_state[content_key])

st.markdown("---")

# Import markdown (optional)
with st.expander("📥 Importer un fichier (Markdown / TXT) pour remplacer le contenu", expanded=False):
    uploaded = st.file_uploader("Choisir un fichier .md ou .txt", type=["md", "txt"])
    if uploaded is not None:
        try:
            txt = uploaded.read().decode("utf-8", errors="replace")
            st.session_state[content_key] = txt
            st.success("Contenu importé et appliqué (tu peux ensuite exporter en PDF).")
        except Exception as e:
            st.error(f"Erreur import : {e}")

# Screenshot uploads for PDF annex
with st.expander("🖼️ Annexes PDF – ajouter des captures d’écran (optionnel)", expanded=False):
    shots = st.file_uploader(
        "Uploader des images (PNG/JPG) à inclure dans le PDF",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )

st.markdown("### 📄 Export PDF")
default_title = "Aide – Berenbaum Law App" if lang == "Français" else "Help – Berenbaum Law App"
title = st.text_input("Titre du PDF", value=default_title)

include_branding = (pdf_mode == "Cabinet interne (logo + nom)")
lang_label = "FR" if lang == "Français" else "EN"

images_payload = []
if shots:
    for f in shots:
        images_payload.append((f.getvalue(), f.name))

btn_col1, btn_col2 = st.columns([1, 3])
with btn_col1:
    generate = st.button("📄 Générer le PDF", type="primary")
with btn_col2:
    st.caption("Le PDF est généré localement côté app. Aucun module externe requis.")

if generate:
    pdf_bytes = build_pdf(
        content=st.session_state[content_key],
        lang_label=lang_label,
        cabinet_name=st.session_state["cabinet_name"],
        logo_path=st.session_state["cabinet_logo_path"],
        title=title,
        include_branding=include_branding,
        images=images_payload,
    )

    fname = f"aide_{lang_label}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    st.download_button(
        "⬇️ Télécharger le PDF",
        data=pdf_bytes,
        file_name=fname,
        mime="application/pdf",
    )

st.caption(
    "Pour un rendu PDF avec accents parfaits, tu peux ajouter un fichier de police "
    "assets/DejaVuSans.ttf. Sinon, Helvetica est utilisée."
)
