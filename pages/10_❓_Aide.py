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
# CONTENU AIDE (FR: fourni par toi) + (EN: traduction)
# =========================================================
DEFAULT_HELP_FR = """# ❓ AIDE & MODE D’EMPLOI
Application de gestion des dossiers – Cabinet (Interne)

## 1. Objectif de l’application
Cette application permet de gérer l’ensemble des dossiers clients du cabinet, depuis la création jusqu’à la clôture, avec :

- Suivi administratif (statuts, dates)
- Suivi financier (honoraires, acomptes, soldes)
- Gestion des escrows
- Organisation des dossiers parents et sous-dossiers
- Analyses, KPI et exports (Excel / PDF)

Elle est conçue pour être utilisée sans connaissance technique.

## 2. Navigation générale

### Menu latéral (sidebar)
Le menu à gauche permet d’accéder aux pages suivantes :

- 🏠 Dashboard – Vue globale
- 📁 Liste des dossiers
- ➕ Nouveau dossier
- ✏️ Modifier un dossier
- 📊 Analyses
- 💰 Escrow
- 🛂 Visa
- 📤 Export Excel
- ⚙️ Paramètres
- ❓ Aide
- 📄 Fiche dossier
- 📁 Fiche groupe dossier
- 💲 Tarifs
- 📤 Export JSON ↔ Excel

**Astuce :**
Si une page n’apparaît pas, vérifier son nom exact dans le dossier `/pages`.

## 3. 🏠 Dashboard – Vue globale

### À quoi sert le Dashboard ?
Le Dashboard est la page principale.
Il donne une vision instantanée de l’activité du cabinet.

### 3.1 Filtres (en haut)
Les filtres permettent d’afficher uniquement certains dossiers :

- Année
- Catégorie
- Sous-catégorie
- Visa
- Statut

Les KPI et les tableaux se recalculent automatiquement selon les filtres.

### 3.2 Indicateurs clés (KPI)
Les KPI affichés sont :

- Nombre de dossiers
- Montant honoraires (US $)
- Autres frais (US $)
- Total facturé
- Total encaissé
- Solde dû
- Escrow total (Acompte 1 uniquement)

**Règle importante :**
Le montant en escrow correspond toujours à **Acompte 1**, jamais aux acomptes 2, 3 ou 4.

### 3.3 Tableau “Dossiers (parents & fils)”
Ce tableau affiche :

- Les dossiers parents
- Les sous-dossiers (fils)
- Leur hiérarchie
- Les montants financiers
- Les informations visa

Les sous-dossiers peuvent avoir un visa différent du dossier parent.

## 4. 📁 Liste complète des dossiers
Cette page affiche tous les dossiers, avec :

- Filtres par année, catégorie, sous-catégorie, visa
- Colonnes financières détaillées
- Acomptes visibles

Elle sert principalement à :

- Contrôler les données
- Vérifier les montants
- Rechercher un dossier précis

## 5. ➕ Nouveau dossier

### 5.1 Choix du type de dossier
Deux options :

- **Dossier parent**
- **Sous-dossier (fils)**

**Dossier parent**
- Numéro automatique (ex: 13068)
- Dossier principal

**Sous-dossier (fils)**
- Rattaché à un dossier parent
- Numérotation : 13068-1, 13068-2, etc.

Les sous-dossiers sont utilisés lorsque :
- Un même client a plusieurs procédures
- Des visas différents sont nécessaires

### 5.2 Informations dossier
Champs obligatoires :
- Nom
- Date de création
- Catégorie
- Sous-catégorie
- Visa

### 5.3 Facturation
- Montant honoraires
- Autres frais
- Total calculé automatiquement

### 5.4 Acompte 1 (seul visible ici)
- Montant Acompte 1
- Date de paiement
- Mode de règlement : Chèque / CB / Virement / Venmo

Les acomptes 2, 3 et 4 seront saisis plus tard dans “Modifier dossier”.

## 6. ✏️ Modifier un dossier
Page centrale pour la gestion quotidienne.

### 6.1 Informations générales
- Nom
- Date du dossier
- Catégorie / Sous-catégorie
- Visa
- Commentaire (toujours sauvegardé)

### 6.2 Facturation
- Montant honoraires (US $)
- Autres frais
- Total facturé
- Total encaissé
- Solde dû

### 6.3 Acomptes (1 à 4)
Pour chaque acompte :
- Montant
- Date de paiement
- Mode de règlement

### 6.4 Escrow
- Case Escrow actif
- Passage automatique vers : Escrow à réclamer → Escrow réclamé
- Le dossier disparaît automatiquement des listes précédentes lorsqu’il change d’état.

### 6.5 Statuts du dossier
Cases à cocher :
- Dossier envoyé
- Dossier accepté
- Dossier refusé
- Dossier annulé
- RFE

Dates associées :
- Date dossier envoyé
- Date dossier accepté
- Date dossier refusé
- Date dossier annulé
- Date RFE

## 7. 💰 Gestion des Escrows
États possibles :
- Escrow actif
- Escrow à réclamer
- Escrow réclamé

Règles clés :
- Le montant affiché = Acompte 1
- Les KPI sont recalculés automatiquement
- Boutons de transition entre états

## 8. 📊 Analyses
KPI disponibles :
- Nombre de dossiers
- Dossiers acceptés
- Dossiers refusés
- Dossiers annulés
- Dossiers soldés
- Dossiers non soldés
- Dossiers avec solde négatif

Filtres avancés :
- Multi-années
- Comparaison de périodes
- Statuts

## 9. 💲 Tarifs par Visa
- Chaque visa possède un tarif
- Les modifications sont horodatées
- Historique conservé automatiquement
- Le tarif applicable dépend de la date du dossier

## 10. 📤 Export JSON ↔ Excel

### Export JSON → Excel
Fichier Excel multi-feuilles :
- Clients
- Visa
- Escrow
- Comptabilité

Nom horodaté
Sans signature
Prêt pour audit ou archivage

### Import Excel → JSON
Toujours utiliser un fichier conforme (colonnes exactes).

## 11. 📄 Fiches dossiers
- Fiche dossier : un dossier
- Fiche groupe dossier : parent + fils
- Export PDF possible
- Utilisable pour clients ou interne

## 12. Bonnes pratiques (IMPORTANT)
- Toujours utiliser les filtres
- Ne jamais modifier le JSON manuellement
- Utiliser les exports pour archivage
- Vérifier les dates lors des paiements
- Utiliser les sous-dossiers pour visas multiples

## 13. FAQ rapide
**Q : Pourquoi un dossier n’apparaît pas dans un KPI ?**  
Vérifier les filtres actifs.

**Q : Pourquoi l’escrow ne correspond pas au total encaissé ?**  
L’escrow = Acompte 1 uniquement.

**Q : Puis-je modifier un visa sur un sous-dossier ?**  
Oui, indépendamment du parent.

## 14. Versions & impression
Cette aide est :
- Imprimable
- Exportable PDF
- Déclinable en version américaine (EN)
"""

# Traduction EN best-effort (tu peux éditer dans l’onglet EN directement)
DEFAULT_HELP_EN = """# ❓ HELP & USER GUIDE
Case management application – Internal (Law Firm)

## 1. Purpose of the application
This application helps the firm manage all client cases from creation to closing, including:

- Administrative tracking (statuses, dates)
- Financial tracking (fees, deposits, balances)
- Escrow management
- Parent/child case organization
- Analytics, KPIs and exports (Excel / PDF)

It is designed to be used without any technical knowledge.

## 2. General navigation

### Left menu (sidebar)
The left menu provides access to the following pages:

- 🏠 Dashboard – Global view
- 📁 Case list
- ➕ New case
- ✏️ Edit a case
- 📊 Analytics
- 💰 Escrow
- 🛂 Visa
- 📤 Excel export
- ⚙️ Settings
- ❓ Help
- 📄 Case sheet
- 📁 Case group sheet
- 💲 Pricing
- 📤 JSON ↔ Excel export

**Tip:**
If a page does not appear, verify its exact filename in the `/pages` folder.

## 3. 🏠 Dashboard – Global view

### What is the Dashboard for?
The Dashboard is the main page.
It provides an instant overview of the firm’s activity.

### 3.1 Filters (top)
Filters let you display only specific cases:

- Year
- Category
- Sub-category
- Visa
- Status

KPIs and tables recalculate automatically based on filters.

### 3.2 Key indicators (KPIs)
Displayed KPIs:

- Number of cases
- Attorney fees (US $)
- Other fees (US $)
- Total invoiced
- Total received
- Amount due
- Total escrow (Deposit 1 only)

**Important rule:**
Escrow amount always equals **Deposit 1** only; deposits 2, 3, and 4 are never escrowed.

### 3.3 “Cases (parents & children)” table
This table shows:

- Parent cases
- Child cases (sub-cases)
- Their hierarchy
- Financial amounts
- Visa information

Child cases may have a different visa than the parent case.

## 4. 📁 Full case list
This page shows all cases, with:

- Filters by year, category, sub-category, visa
- Detailed financial columns
- Visible deposits

Main uses:

- Data control
- Amount verification
- Searching a specific case

## 5. ➕ New case

### 5.1 Choose the case type
Two options:

- **Parent case**
- **Child case (sub-case)**

**Parent case**
- Automatic number (e.g., 13068)
- Main case

**Child case (sub-case)**
- Attached to a parent case
- Numbering: 13068-1, 13068-2, etc.

Child cases are used when:
- The same client has multiple procedures
- Different visas are required

### 5.2 Case information
Required fields:
- Name
- Creation date
- Category
- Sub-category
- Visa

### 5.3 Billing
- Attorney fees
- Other fees
- Total computed automatically

### 5.4 Deposit 1 (only visible here)
- Deposit 1 amount
- Payment date
- Payment method: Check / Card / Wire / Venmo

Deposits 2, 3 and 4 are entered later in “Edit case”.

## 6. ✏️ Edit a case
Main page for daily operations.

### 6.1 General information
- Name
- Case date
- Category / Sub-category
- Visa
- Comment (always saved)

### 6.2 Billing
- Attorney fees (US $)
- Other fees
- Total invoiced
- Total received
- Amount due

### 6.3 Deposits (1 to 4)
For each deposit:
- Amount
- Payment date
- Payment method

### 6.4 Escrow
- “Escrow active” checkbox
- Automatic transitions: Escrow to claim → Escrow claimed
- The case disappears from previous lists when state changes.

### 6.5 Case statuses
Checkboxes:
- Sent
- Approved
- Denied
- Cancelled
- RFE

Associated dates:
- Sent date
- Approved date
- Denied date
- Cancelled date
- RFE date

## 7. 💰 Escrow management
Possible states:
- Active escrow
- Escrow to claim
- Escrow claimed

Key rules:
- Displayed amount = Deposit 1
- KPIs recalculate automatically
- Transition buttons between states

## 8. 📊 Analytics
Available KPIs:
- Number of cases
- Approved cases
- Denied cases
- Cancelled cases
- Paid-in-full cases
- Unpaid cases
- Negative balance cases

Advanced filters:
- Multi-year
- Period comparisons
- Status filters

## 9. 💲 Visa pricing
- Each visa has its own price
- Changes are timestamped
- History is stored automatically
- Applicable price depends on the case date

## 10. 📤 JSON ↔ Excel export

### Export JSON → Excel
Multi-sheet Excel file:
- Clients
- Visa
- Escrow
- Accounting

Timestamped filename
No signature
Ready for audit/archiving

### Import Excel → JSON
Always use a compliant file (exact columns).

## 11. 📄 Case sheets
- Case sheet: one case
- Group case sheet: parent + children
- PDF export possible
- Usable for clients or internal use

## 12. Best practices (IMPORTANT)
- Always use filters
- Never edit the JSON manually
- Use exports for archiving
- Verify payment dates
- Use child cases for multiple visas

## 13. Quick FAQ
**Q: Why doesn’t a case appear in a KPI?**  
Check active filters.

**Q: Why doesn’t escrow match total received?**  
Escrow = Deposit 1 only.

**Q: Can I edit the visa on a child case?**  
Yes, independently from the parent.

## 14. Versions & printing
This help is:
- Printable
- Exportable to PDF
- Available as a US/English version (EN)
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
    Optionnel : si assets/DejaVuSans.ttf existe, meilleure compatibilité accents.
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
            # Logo
            if logo is not None:
                lw = 2.0 * cm
                lh_img = 2.0 * cm
                c.drawImage(logo, left, y_top - lh_img, width=lw, height=lh_img, mask="auto")
                x_txt = left + lw + 0.6 * cm
            else:
                x_txt = left

            # Cabinet name
            c.setFont(font, 14)
            c.drawString(x_txt, y_top - 0.6 * cm, (cabinet_name or "")[:80])

            # Title
            c.setFont(font, 12)
            c.drawString(x_txt, y_top - 1.25 * cm, title[:95])

            # Separator line
            c.setLineWidth(0.5)
            c.line(left, y_top - 2.2 * cm, W - right, y_top - 2.2 * cm)
            return y_top - 2.7 * cm

        # Without branding
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

        # Headings
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

        # Bullet
        text = "• " + s[2:].strip() if s.startswith("- ") else s

        for l in wrap_text(c, text, font, body_size, max_w):
            if y < bottom:
                new_page()
            c.drawString(left, y, l)
            y -= lh

    # Annex images (optional)
    if images:
        if y < bottom + 6 * cm:
            new_page()

        c.setFont(font, 12)
        c.drawString(left, y, "Annexes – Captures d’écran" if lang_label == "FR" else "Appendix – Screenshots")
        y -= (lh + 6)

        for img_bytes, name in images:
            try:
                img = ImageReader(BytesIO(img_bytes))
                img_max_w = max_w
                img_max_h = 12 * cm

                if y < bottom + img_max_h:
                    new_page()

                c.setFont(font, 9)
                c.drawString(left, y, f"{name}")
                y -= 12

                c.drawImage(
                    img,
                    left,
                    y - img_max_h,
                    width=img_max_w,
                    height=img_max_h,
                    preserveAspectRatio=True,
                    anchor="sw",
                    mask="auto",
                )
                y -= (img_max_h + 18)

            except Exception:
                continue

    footer(page)
    c.save()
    return buf.getvalue()


# =========================================================
# UI
# =========================================================
st.markdown("## ❓ Aide – Consultation / Édition / Export PDF")

# Top header with logo + cabinet name
top_l, top_r = st.columns([1, 5])
with top_l:
    lp = st.session_state["cabinet_logo_path"]
    if lp and os.path.exists(lp):
        st.image(lp, width=120)
    else:
        st.write("")
with top_r:
    st.markdown(f"### {st.session_state['cabinet_name']}")
    st.caption("Aide interne : consultation, édition, export PDF (FR/EN) et annexes (captures d’écran).")

st.markdown("---")

with st.expander("⚙️ Paramètres (logo / nom cabinet / options PDF)", expanded=False):
    st.session_state["cabinet_name"] = st.text_input(
        "Nom du cabinet",
        value=st.session_state["cabinet_name"]
    )
    st.session_state["cabinet_logo_path"] = st.text_input(
        "Chemin du logo",
        value=st.session_state["cabinet_logo_path"]
    )
    if st.session_state["cabinet_logo_path"] and not os.path.exists(st.session_state["cabinet_logo_path"]):
        st.warning("Logo introuvable : le PDF “Cabinet interne” sera généré sans logo (mais avec le nom).")

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
        height=600
    )
else:
    st.markdown(st.session_state[content_key])

st.markdown("---")

# Import markdown/txt (optional)
with st.expander("📥 Importer un fichier (Markdown / TXT) pour remplacer le contenu", expanded=False):
    uploaded = st.file_uploader("Choisir un fichier .md ou .txt", type=["md", "txt"])
    if uploaded is not None:
        try:
            txt = uploaded.read().decode("utf-8", errors="replace")
            st.session_state[content_key] = txt
            st.success("Contenu importé et appliqué. Tu peux maintenant l’éditer et/ou l’exporter en PDF.")
        except Exception as e:
            st.error(f"Erreur import : {e}")

# Screenshot uploads for PDF annex
with st.expander("🖼️ Annexes PDF – ajouter des captures d’écran (optionnel)", expanded=False):
    shots = st.file_uploader(
        "Uploader des images (PNG/JPG/WEBP) à inclure dans le PDF",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True
    )

st.markdown("### 📄 Export PDF")
default_title = "Aide & Mode d’emploi – Cabinet (Interne)" if lang == "Français" else "Help & User Guide – Internal"
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
    st.caption("Le PDF est généré directement par l’application. Aucun module externe requis.")

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
    "Amélioration recommandée (optionnelle) : ajouter une police pour accents dans `assets/DejaVuSans.ttf` "
    "pour une compatibilité parfaite. Sinon, Helvetica est utilisée."
)