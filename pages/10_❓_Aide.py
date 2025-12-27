# pages/10_❓_Aide.py
import streamlit as st
from io import BytesIO
from datetime import datetime

from utils.sidebar import render_sidebar

# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="❓ Aide", page_icon="❓", layout="wide")
render_sidebar()
st.title("❓ Aide – Mode d’emploi (interne cabinet)")


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
Dashboard, Liste, Nouveau, Modifier, Analyses, Escrow, Visa, Tarifs, Exports, Paramètres.

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
Dashboard, List, New, Edit, Analytics, Escrow, Visa, Pricing, Exports, Settings.

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
# PDF BUILDER (dans ce fichier pour éviter les imports manquants)
# =========================================================
def _register_font_if_available():
    """
    Optionnel : si tu ajoutes un fichier TTF dans assets/ (ex: assets/DejaVuSans.ttf),
    on l'utilise pour mieux supporter accents et symboles.
    """
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", "assets/DejaVuSans.ttf"))
        return "DejaVuSans"
    except Exception:
        return "Helvetica"


def build_help_pdf_bytes(title: str, content: str, footer: str = "") -> bytes:
    """
    Génère un PDF A4 simple, propre, imprimable.
    - Supporte sauts de ligne
    - Coupe les lignes trop longues
    """
    font_name = _register_font_if_available()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)

    width, height = A4
    left = 2.0 * cm
    right = 2.0 * cm
    top = 2.0 * cm
    bottom = 2.0 * cm

    max_width = width - left - right

    # Styles simples
    title_size = 16
    body_size = 10
    line_height = 14  # points

    y = height - top

    # Titre
    c.setFont(font_name, title_size)
    c.drawString(left, y, title[:120])
    y -= 24

    c.setFont(font_name, body_size)

    def wrap_line(line: str):
        # wrap simple par mots
        words = line.split(" ")
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

    # Corps (markdown "léger" -> rendu texte)
    # On transforme certains marqueurs (#, ##, -) en texte lisible.
    raw_lines = content.replace("\r\n", "\n").split("\n")
    for raw in raw_lines:
        line = raw.strip()

        # Sauts / espaces
        if line == "":
            y -= line_height
            continue

        # Petites conventions markdown
        if line.startswith("### "):
            c.setFont(font_name, 12)
            text = line[4:].strip()
            y -= 4
            for wl in wrap_line(text):
                if y < bottom:
                    c.showPage()
                    c.setFont(font_name, body_size)
                    y = height - top
                    c.setFont(font_name, 12)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        if line.startswith("## "):
            c.setFont(font_name, 13)
            text = line[3:].strip()
            y -= 6
            for wl in wrap_line(text):
                if y < bottom:
                    c.showPage()
                    c.setFont(font_name, body_size)
                    y = height - top
                    c.setFont(font_name, 13)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        if line.startswith("# "):
            c.setFont(font_name, 14)
            text = line[2:].strip()
            y -= 8
            for wl in wrap_line(text):
                if y < bottom:
                    c.showPage()
                    c.setFont(font_name, body_size)
                    y = height - top
                    c.setFont(font_name, 14)
                c.drawString(left, y, wl)
                y -= line_height
            c.setFont(font_name, body_size)
            continue

        if line.startswith("- "):
            text = "• " + line[2:].strip()
        else:
            text = line

        for wl in wrap_line(text):
            if y < bottom:
                c.showPage()
                c.setFont(font_name, body_size)
                y = height - top
            c.drawString(left, y, wl)
            y -= line_height

    # Footer
    if footer:
        c.setFont(font_name, 8)
        c.drawString(left, bottom - 10, footer[:160])

    c.save()
    return buf.getvalue()


# =========================================================
# UI – Edition + Export PDF
# =========================================================
st.markdown("### 📘 Consulter / éditer l’aide")
colA, colB, colC = st.columns([2, 2, 2])

lang = colA.selectbox("Langue", ["Français", "English"], index=0)
mode = colB.selectbox("Mode", ["Édition", "Lecture"], index=0)
pdf_branding = colC.selectbox("En-tête PDF", ["Cabinet interne", "Sans en-tête"], index=0)

if "help_fr" not in st.session_state:
    st.session_state["help_fr"] = DEFAULT_HELP_FR
if "help_en" not in st.session_state:
    st.session_state["help_en"] = DEFAULT_HELP_EN

content_key = "help_fr" if lang == "Français" else "help_en"
content_value = st.session_state[content_key]

if mode == "Édition":
    st.info("Vous pouvez modifier le texte ci-dessous puis exporter en PDF.")
    edited = st.text_area(
        "Contenu de l’aide (modifiable)",
        value=content_value,
        height=520,
    )
    st.session_state[content_key] = edited
else:
    st.markdown(st.session_state[content_key])

st.markdown("---")
st.markdown("### 📄 Export PDF")

export_title = st.text_input(
    "Titre PDF",
    value="Aide – Berenbaum Law App" if lang == "Français" else "Help – Berenbaum Law App",
)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
footer = ""
if pdf_branding == "Cabinet interne":
    footer = f"Document interne cabinet – généré le {now_str}"
else:
    footer = f"Généré le {now_str}"

if st.button("📄 Générer le PDF", type="primary"):
    pdf_bytes = build_help_pdf_bytes(
        title=export_title,
        content=st.session_state[content_key],
        footer=footer,
    )
    st.success("PDF généré. Vous pouvez le télécharger ci-dessous.")

    filename = f"aide_{'FR' if lang=='Français' else 'EN'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    st.download_button(
        label="⬇️ Télécharger le PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )

st.caption(
    "Astuce : si vous souhaitez une meilleure gestion des accents dans le PDF, "
    "ajoutez un fichier police TTF dans assets/ (ex: assets/DejaVuSans.ttf)."
)
