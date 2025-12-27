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
# CONFIG
# =========================================================
st.set_page_config(page_title="❓ Aide", page_icon="❓", layout="wide")
render_sidebar()

# =========================================================
# PARAMÈTRES (Logo + Nom cabinet)
# =========================================================
DEFAULT_CABINET_NAME = "Berenbaum Law"
LOGO_PATH = "assets/logo.png"

# Ces 2 valeurs sont éditables dans la page, mais gardées en session
if "cabinet_name" not in st.session_state:
    st.session_state["cabinet_name"] = DEFAULT_CABINET_NAME
if "help_logo_path" not in st.session_state:
    st.session_state["help_logo_path"] = LOGO_PATH


# =========================================================
# CONTENU PAR DÉFAUT (FR/EN)
# =========================================================
DEFAULT_HELP_FR = """# AIDE & MODE D’EMPLOI – Cabinet (Interne)

## 1. Objectif
Cette application permet de gérer les dossiers du cabinet :
- création / modification
- statuts & dates
- finances (honoraires, acomptes, solde)
- escrow (Acompte 1 uniquement)
- analyses et exports

## 2. Navigation
Utilisez la barre latérale (sidebar) pour accéder aux pages :
Dashboard, Liste, Nouveau, Modifier, Analyses, Escrow, Visa, Tarifs, Exports, Paramètres, Aide.

## 3. Dashboard
- Filtres : Année, Catégorie, Sous-catégorie, Visa, Statut
- KPI : nombre de dossiers, honoraires, frais, total facturé, total encaissé, solde dû, escrow total

Règle escrow :
> Le montant escrow correspond à Acompte 1 uniquement.

## 4. Nouveau dossier
- Dossier parent : ex 13068
- Sous-dossier (fils) : ex 13068-1, 13068-2
- Catégorie / sous-catégorie / visa obligatoires
- Acompte 1 + date + mode de règlement (Chèque / CB / Virement / Venmo)

## 5. Modifier un dossier
- Informations générales + commentaire
- Facturation : Montant honoraires (US $) + autres frais
- Acomptes 1→4 + dates + modes
- Statuts : envoyé / accepté / refusé / annulé / RFE + dates associées
- Escrow : transitions selon la procédure interne

## 6. Analyses
Filtres + KPI + comparaisons temporelles.

## 7. Exports
- Export JSON ↔ Excel multi-feuilles
- Export PDF si activé

## 8. FAQ
- Pourquoi un KPI ne bouge pas ? Vérifier les filtres.
- Pourquoi escrow ≠ total encaissé ? Escrow = Acompte 1 uniquement.
"""

DEFAULT_HELP_EN = """# HELP & USER GUIDE – Internal (Firm Use)

## 1. Purpose
This app helps manage the firm’s cases:
- create / edit cases
- statuses & dates
- financials (fees, deposits, balance)
- escrow (Deposit 1 only)
- analytics and exports

## 2. Navigation
Use the left sidebar to open pages:
Dashboard, List, New, Edit, Analytics, Escrow, Visa, Pricing, Exports, Settings, Help.

## 3. Dashboard
- Filters: Year, Category, Sub-category, Visa, Status
- KPIs: total cases, fees, other charges, billed total, collected total, balance due, escrow total

Escrow rule:
> Escrow amount equals Deposit 1 only.

## 4. New Case
- Parent case: e.g., 13068
- Child case: e.g., 13068-1, 13068-2
- Category / sub-category / visa required
- Deposit 1 + payment date + payment method (Check / Card / Wire / Venmo)

## 5. Edit Case
- General info + comments
- Billing: Fees (US $) + other charges
- Deposits 1→4 + dates + methods
- Statuses: sent / approved / denied / cancelled / RFE + related dates
- Escrow: transitions per internal procedure

## 6. Analytics
Filters + KPIs + time comparisons.

## 7. Exports
- JSON ↔ Excel multi-sheet export
- PDF export if enabled

## 8. FAQ
- KPI not updating? Check filters.
- Escrow ≠ collected? Escrow = Deposit 1 only.
"""


# =========================================================
# PDF BUILDER (Logo + Nom cabinet)
# =========================================================
def _register_font_if_available() -> str:
    """
    Optionnel : si tu ajoutes un fichier TTF dans assets/ (ex: assets/DejaVuSans.ttf),
    on l'utilise pour mieux supporter accents et symboles.
    """
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", "assets/DejaVuSans.ttf"))
        return "DejaVuSans"
    except Exception:
        return "Helvetica"


def _safe_image_reader(path: str):
    try:
        if path and os.path.exists(path):
            return ImageReader(path)
    except Exception:
        pass
    return None


def build_help_pdf_bytes(
    cabinet_name: str,
    title: str,
    content: str,
    footer: str = "",
    logo_path: str = "assets/logo.png",
) -> bytes:
    """
    Génère un PDF A4 :
    - En-tête avec logo + nom cabinet + titre
    - Corps texte paginé
    - Footer optionnel
    """
    font_name = _register_font_if_available()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    width, height = A4
    left = 2.0 * cm
    right = 2.0 * cm
    top = 1.6 * cm
    bottom = 2.0 * cm
    max_width = width - left - right

    # Styles
    header_name_size = 14
    header_title_size = 12
    body_size = 10
    line_height = 14  # points

    logo = _safe_image_reader(logo_path)

    def draw_header():
        y_top = height - top

        # Logo
        if logo is not None:
            # dimension logo
            logo_w = 2.0 * cm
            logo_h = 2.0 * cm
            c.drawImage(logo, left, y_top - logo_h, width=logo_w, height=logo_h, mask="auto")
            x_text = left + logo_w + 0.6 * cm
        else:
            x_text = left

        # Nom cabinet
        c.setFont(font_name, header_name_size)
        c.drawString(x_text, y_top - 0.6 * cm, (cabinet_name or "").strip()[:70])

        # Titre document
        c.setFont(font_name, header_title_size)
        c.drawString(x_text, y_top - 1.25 * cm, title[:90])

        # Trait séparation
        c.setLineWidth(0.5)
        c.line(left, y_top - 2.2 * cm, width - right, y_top - 2.2 * cm)

        return y_top - 2.7 * cm  # position de départ du corps

    def wrap_line(text: str):
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if c.stringWidth(test, font_name, body_size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

    y = draw_header()
    c.setFont(font_name, body_size)

    raw_lines = content.replace("\r\n", "\n").split("\n")

    def new_page():
        c.showPage()
        return draw_header()

    for raw in raw_lines:
        line = raw.strip()

        if line == "":
            y -= line_height
            if y < bottom:
                y = new_page()
                c.setFont(font_name, body_size)
            continue

        # Markdown "léger"
        if line.startswith("### "):
            c.setFont(font_name, 12)
            text = line[4:].strip()
            y -= 2
            for wl in wrap_line(text):
                if y < bottom:
                    y = new_page()
                    c.setFont(font_name, 12)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        if line.startswith("## "):
            c.setFont(font_name, 13)
            text = line[3:].strip()
            y -= 4
            for wl in wrap_line(text):
                if y < bottom:
                    y = new_page()
                    c.setFont(font_name, 13)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        if line.startswith("# "):
            c.setFont(font_name, 14)
            text = line[2:].strip()
            y -= 6
            for wl in wrap_line(text):
                if y < bottom:
                    y = new_page()
                    c.setFont(font_name, 14)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        text = "• " + line[2:].strip() if line.startswith("- ") else line

        for wl in wrap_line(text):
            if y < bottom:
                y = new_page()
                c.setFont(font_name, body_size)
            c.drawString(left, y, wl)
            y -= line_height

    # Footer (sur la dernière page)
    if footer:
        c.setFont(font_name, 8)
        c.drawString(left, bottom - 10, footer[:160])

    c.save()
    return buf.getvalue()


# =========================================================
# UI – Header page (Logo + Nom cabinet)
# =========================================================
cabinet_name = st.session_state["cabinet_name"]
logo_path = st.session_state["help_logo_path"]

header_left, header_right = st.columns([1, 4])
with header_left:
    if logo_path and os.path.exists(logo_path):
        st.image(logo_path, width=95)
with header_right:
    st.markdown(f"## {cabinet_name}")
    st.caption("Espace Aide – consultation, édition et export PDF")

st.markdown("---")

with st.expander("⚙️ Paramètres de l’aide (logo / nom cabinet)", expanded=False):
    st.session_state["cabinet_name"] = st.text_input("Nom du cabinet", value=st.session_state["cabinet_name"])
    st.session_state["help_logo_path"] = st.text_input("Chemin du logo", value=st.session_state["help_logo_path"])
    if st.session_state["help_logo_path"] and not os.path.exists(st.session_state["help_logo_path"]):
        st.warning("Logo introuvable à ce chemin. Le PDF sera généré sans logo.")


# =========================================================
# UI – Edition + Export PDF
# =========================================================
st.markdown("### 📘 Consulter / éditer l’aide")

colA, colB, colC = st.columns([2, 2, 2])
lang = colA.selectbox("Langue", ["Français", "English"], index=0)
mode = colB.selectbox("Mode", ["Édition", "Lecture"], index=0)
pdf_branding = colC.selectbox("Type PDF", ["Cabinet interne", "Sans en-tête"], index=0)

if "help_fr" not in st.session_state:
    st.session_state["help_fr"] = DEFAULT_HELP_FR
if "help_en" not in st.session_state:
    st.session_state["help_en"] = DEFAULT_HELP_EN

content_key = "help_fr" if lang == "Français" else "help_en"

if mode == "Édition":
    st.info("Modifiez le texte ci-dessous puis exportez en PDF.")
    edited = st.text_area(
        "Contenu de l’aide (modifiable)",
        value=st.session_state[content_key],
        height=520,
    )
    st.session_state[content_key] = edited
else:
    st.markdown(st.session_state[content_key])

st.markdown("---")
st.markdown("### 📄 Export PDF")

default_title = "Aide – Berenbaum Law App" if lang == "Français" else "Help – Berenbaum Law App"
export_title = st.text_input("Titre du document", value=default_title)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
if pdf_branding == "Cabinet interne":
    footer = f"Document interne cabinet – généré le {now_str}"
else:
    footer = f"Généré le {now_str}"

if st.button("📄 Générer le PDF", type="primary"):
    pdf_bytes = build_help_pdf_bytes(
        cabinet_name=st.session_state["cabinet_name"] if pdf_branding == "Cabinet interne" else "",
        title=export_title,
        content=st.session_state[content_key],
        footer=footer,
        logo_path=st.session_state["help_logo_path"] if pdf_branding == "Cabinet interne" else "",
    )

    filename = f"aide_{'FR' if lang=='Français' else 'EN'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    st.download_button(
        label="⬇️ Télécharger le PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )

st.caption(
    "Astuce : pour une meilleure gestion des accents dans le PDF, "
    "vous pouvez ajouter une police TTF dans assets/ (ex: assets/DejaVuSans.ttf)."
)
