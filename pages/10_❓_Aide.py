import os
from datetime import datetime

import streamlit as st

from utils.sidebar import render_sidebar

# =========================================================
# PDF BUILDER (AUTONOUS / NO EXTERNAL IMPORT)
# =========================================================
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _try_register_fonts():
    font_dir = os.path.join("assets", "fonts")
    dejavu = os.path.join(font_dir, "DejaVuSans.ttf")
    dejavu_b = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    try:
        if os.path.exists(dejavu):
            pdfmetrics.registerFont(TTFont("DejaVuSans", dejavu))
        if os.path.exists(dejavu_b):
            pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", dejavu_b))
    except Exception:
        pass


def _styles():
    _try_register_fonts()
    styles = getSampleStyleSheet()

    base_font = "Helvetica"
    base_bold = "Helvetica-Bold"
    if "DejaVuSans" in pdfmetrics.getRegisteredFontNames():
        base_font = "DejaVuSans"
    if "DejaVuSans-Bold" in pdfmetrics.getRegisteredFontNames():
        base_bold = "DejaVuSans-Bold"

    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName=base_bold,
        fontSize=20,
        leading=24,
        spaceAfter=14,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName=base_bold,
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName=base_bold,
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName=base_font,
        fontSize=10.5,
        leading=14,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontName=base_font,
        fontSize=9,
        leading=12,
        textColor=colors.grey,
        spaceAfter=6,
    )
    mono = ParagraphStyle(
        "Mono",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9.5,
        leading=12,
        backColor=colors.whitesmoke,
        borderColor=colors.lightgrey,
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=6,
    )
    return {
        "title": title,
        "h1": h1,
        "h2": h2,
        "body": body,
        "small": small,
        "mono": mono,
        "base_font": base_font,
        "base_bold": base_bold,
    }


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraphs_from_text(text: str, body_style, mono_style):
    flow = []
    lines = text.split("\n")
    in_code = False
    code_buf = []
    bullet_buf = []

    def flush_code():
        nonlocal code_buf
        if code_buf:
            code_text = "<br/>".join(_escape(x) for x in code_buf)
            flow.append(Paragraph(code_text, mono_style))
            code_buf = []

    def flush_bullets():
        nonlocal bullet_buf
        if bullet_buf:
            items = "".join(f"<li>{_escape(x)}</li>" for x in bullet_buf)
            flow.append(Paragraph(f"<ul>{items}</ul>", body_style))
            bullet_buf = []

    for raw in lines:
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if not in_code:
                flush_bullets()
                in_code = True
                code_buf = []
            else:
                in_code = False
                flush_code()
            continue

        if in_code:
            code_buf.append(line)
            continue

        if line.strip() == "":
            flush_bullets()
            flow.append(Spacer(1, 6))
            continue

        if line.lstrip().startswith("- "):
            bullet_buf.append(line.lstrip()[2:])
            continue

        flush_bullets()
        flow.append(Paragraph(_escape(line), body_style))

    flush_bullets()
    flush_code()
    return flow


def _header_footer(canvas, doc, title_text: str):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)

    canvas.line(1.7 * cm, 1.6 * cm, A4[0] - 1.7 * cm, 1.6 * cm)
    canvas.drawString(1.7 * cm, 1.1 * cm, title_text)
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, f"Page {doc.page}")

    canvas.restoreState()


def build_help_pdf_bytes(
    *,
    lang_code: str,
    app_name: str,
    subtitle: str,
    sections: list,
    faq: list,
    screenshots_dir: str = "assets/help_screens",
    logo_path: str = "assets/logo.png",
):
    stl = _styles()
    bio = BytesIO()

    doc = SimpleDocTemplate(
        bio,
        pagesize=A4,
        leftMargin=1.7 * cm,
        rightMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2.0 * cm,
        title=f"{app_name} - Help",
        author=app_name,
    )

    story = []

    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=3.2 * cm, height=3.2 * cm))
            story.append(Spacer(1, 10))
        except Exception:
            pass

    story.append(Paragraph(_escape(app_name), stl["title"]))
    story.append(Paragraph(_escape(subtitle), stl["body"]))
    story.append(Spacer(1, 8))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(_escape(f"Version : {now}"), stl["small"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(_escape("Sommaire" if lang_code == "FR" else "Contents"), stl["h1"]))

    toc_data = [[_escape("Section" if lang_code == "FR" else "Section"),
                 _escape("Description" if lang_code == "FR" else "Description")]]

    for s in sections:
        toc_data.append([_escape(s.get("title", "")), _escape(s.get("toc", ""))])

    toc_table = Table(toc_data, colWidths=[7.5 * cm, 8.0 * cm])
    toc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), stl["base_bold"]),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("FONTNAME", (0, 1), (-1, -1), stl["base_font"]),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    for s in sections:
        story.append(Paragraph(_escape(s.get("title", "")), stl["h1"]))
        story.append(Spacer(1, 4))

        story.extend(_paragraphs_from_text(s.get("body", ""), stl["body"], stl["mono"]))
        story.append(Spacer(1, 10))

        img_name = s.get("image")
        if img_name:
            img_path = os.path.join(screenshots_dir, img_name)
            if os.path.exists(img_path):
                try:
                    caption = s.get("caption", "")
                    if caption:
                        story.append(Paragraph(_escape(caption), stl["small"]))
                    story.append(Image(img_path, width=16.0 * cm, height=9.0 * cm))
                    story.append(Spacer(1, 10))
                except Exception:
                    story.append(Paragraph(_escape("Capture non lisible (format/poids)."), stl["small"]))
            else:
                note = f"Capture introuvable : {img_path}" if lang_code == "FR" else f"Screenshot not found: {img_path}"
                story.append(Paragraph(_escape(note), stl["small"]))

        story.append(Spacer(1, 6))

    story.append(PageBreak())
    story.append(Paragraph(_escape("FAQ – Questions fréquentes" if lang_code == "FR" else "FAQ – Common questions"), stl["h1"]))
    story.append(Spacer(1, 6))

    for item in faq:
        story.append(Paragraph(_escape("Q: " + item["q"]), stl["h2"]))
        story.extend(_paragraphs_from_text(item["a"], stl["body"], stl["mono"]))
        story.append(Spacer(1, 8))

    footer_title = f"{app_name} – {'Aide' if lang_code == 'FR' else 'Help'}"
    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, footer_title),
        onLaterPages=lambda c, d: _header_footer(c, d, footer_title),
    )

    bio.seek(0)
    return bio.getvalue()


# =========================================================
# STREAMLIT PAGE
# =========================================================
st.set_page_config(page_title="❓ Aide & Mode d’emploi", page_icon="❓", layout="wide")
render_sidebar()
st.title("❓ Aide & Mode d’emploi (FR / EN)")

lang = st.radio("🌍 Langue / Language", ["Français 🇫🇷", "English 🇺🇸"], horizontal=True)
is_fr = "Français" in lang
lang_code = "FR" if is_fr else "EN"

APP_NAME = "Berenbaum Law App"
subtitle = "Guide utilisateur officiel (néophytes) – Version imprimable + PDF" if is_fr else "Official user guide (beginners) – Printable version + PDF"
st.caption(subtitle)

sections_fr = [
    {
        "title": "1) Objectif de l’application",
        "toc": "À quoi sert l’application et à qui elle s’adresse.",
        "body": (
            "Berenbaum Law App est une application Streamlit de gestion de dossiers.\n"
            "Elle centralise : clients, paiements, statuts, escrow, analyses et exports.\n\n"
            "- Navigation simple via le menu à gauche\n"
            "- Pas de compétence technique requise\n"
            "- Les données sont stockées dans un JSON sur Dropbox"
        ),
        "image": "01_dashboard.png",
        "caption": "Écran : Dashboard (exemple).",
    },
    {
        "title": "2) Navigation (barre latérale)",
        "toc": "Comprendre le menu et accéder aux pages.",
        "body": (
            "Le menu à gauche sert à naviguer entre les pages.\n\n"
            "Pages principales :\n"
            "- Dashboard\n"
            "- Liste des dossiers\n"
            "- Nouveau dossier\n"
            "- Modifier dossier\n"
            "- Escrow\n"
            "- Analyses\n"
            "- Export\n"
            "- Paramètres\n"
            "- Aide"
        ),
        "image": "02_sidebar.png",
        "caption": "Écran : Sidebar / Menu.",
    },
    {
        "title": "3) Dossiers parents et sous-dossiers",
        "toc": "Comprendre la logique parent/fils.",
        "body": (
            "Un dossier peut être Parent (ex: 12937) ou Fils (ex: 12937-1).\n\n"
            "Chaque fils peut avoir un visa différent et ses propres montants/statuts.\n"
            "Les KPI peuvent compter parents + fils selon la page."
        ),
        "image": "03_hierarchy.png",
        "caption": "Écran : Groupe dossier (exemple).",
    },
    {
        "title": "4) Créer un nouveau dossier",
        "toc": "Création et champs obligatoires.",
        "body": (
            "Sur « Nouveau dossier » :\n"
            "- Renseigner Nom et Date\n"
            "- Choisir Catégorie, Sous-catégorie, Visa\n"
            "- Saisir Montant honoraires et Autres frais\n"
            "- Saisir Acompte 1 + Date de paiement + Mode (Chèque/CB/Virement/Venmo)\n\n"
            "Les acomptes 2/3/4 se gèrent dans « Modifier dossier »."
        ),
        "image": "04_new_case.png",
        "caption": "Écran : Nouveau dossier (exemple).",
    },
    {
        "title": "5) Modifier un dossier",
        "toc": "Édition complète : montants, acomptes, statuts, commentaire.",
        "body": (
            "Sur « Modifier dossier » :\n"
            "- Mettre à jour Montant honoraires (US $)\n"
            "- Gérer Acomptes 1 à 4 avec dates et modes\n"
            "- Cocher les statuts + dates associées\n"
            "- Renseigner le champ Commentaire\n\n"
            "Après enregistrement : vérifier que les cases restent cochées."
        ),
        "image": "05_edit_case.png",
        "caption": "Écran : Modifier dossier (exemple).",
    },
    {
        "title": "6) Escrow (3 états) + montants",
        "toc": "Actif → à réclamer → réclamé (montant = Acompte 1).",
        "body": (
            "Escrow fonctionne en 3 états :\n"
            "1) Escrow actif\n"
            "2) Escrow à réclamer\n"
            "3) Escrow réclamé\n\n"
            "Règle : le montant en escrow est toujours égal à Acompte 1.\n"
            "Un dossier doit être dans un seul état à la fois."
        ),
        "image": "06_escrow.png",
        "caption": "Écran : Escrow (exemple).",
    },
    {
        "title": "7) Analyses",
        "toc": "Filtres, comparaisons, soldés/non soldés.",
        "body": (
            "La page Analyses permet :\n"
            "- Filtrer par Catégorie / Sous-catégorie / Visa\n"
            "- Filtrer par Statuts\n"
            "- Filtrer dossiers soldés / non soldés / solde < 0\n"
            "- Comparaisons temporelles\n\n"
            "Si un graphique plante (KeyError Date), il faut vérifier que la fonction reçoit un df avec colonne Date."
        ),
        "image": "07_analytics.png",
        "caption": "Écran : Analyses (exemple).",
    },
    {
        "title": "8) Export et bonnes pratiques",
        "toc": "Exporter, archiver, recharger.",
        "body": (
            "Exporter régulièrement est recommandé.\n\n"
            "Bonnes pratiques :\n"
            "- Faire un export Excel multi-feuilles horodaté\n"
            "- Conserver l’historique\n\n"
            "Erreur typique : « Timestamp is not JSON serializable »\n"
            "→ il faut convertir les dates en chaînes avant sauvegarde JSON."
        ),
        "image": "08_export.png",
        "caption": "Écran : Export (exemple).",
    },
]

faq_fr = [
    {
        "q": "Pourquoi une case cochée revient décochée ?",
        "a": (
            "Causes fréquentes :\n"
            "- colonnes alias (ex: Dossier_envoye vs Dossier envoye)\n"
            "- une fonction de nettoyage qui écrase la valeur\n\n"
            "Solution :\n"
            "- normaliser les statuts au chargement\n"
            "- écrire dans la colonne canonique et ses alias si nécessaire."
        ),
    },
    {
        "q": "Pourquoi le JSON devient vide après import Excel ?",
        "a": (
            "Cause : mapping Excel incorrect ou feuille vide.\n\n"
            "Solution :\n"
            "- vérifier que Clients.xlsx a des lignes\n"
            "- afficher le nombre de lignes importées avant save."
        ),
    },
]

sections_en = [
    {
        "title": "1) Purpose of the application",
        "toc": "What the app is for and who it is for.",
        "body": (
            "Berenbaum Law App is a Streamlit application for case management.\n"
            "It centralizes clients, payments, statuses, escrow, analytics and exports.\n\n"
            "- Easy navigation via the left menu\n"
            "- No technical skills required\n"
            "- Data stored as a JSON file on Dropbox"
        ),
        "image": "01_dashboard.png",
        "caption": "Screen: Dashboard (example).",
    },
    {
        "title": "2) Navigation (sidebar)",
        "toc": "How to use the menu and open pages.",
        "body": (
            "The left sidebar is used to navigate between pages.\n\n"
            "Main pages:\n"
            "- Dashboard\n"
            "- Case list\n"
            "- New case\n"
            "- Edit case\n"
            "- Escrow\n"
            "- Analytics\n"
            "- Export\n"
            "- Settings\n"
            "- Help"
        ),
        "image": "02_sidebar.png",
        "caption": "Screen: Sidebar / Menu.",
    },
    {
        "title": "3) Parent and child cases",
        "toc": "Understand parent/child logic.",
        "body": (
            "A case can be Parent (e.g., 12937) or Child (e.g., 12937-1).\n\n"
            "Each child can have a different visa and its own amounts/statuses.\n"
            "KPIs may count both parents and children depending on the page."
        ),
        "image": "03_hierarchy.png",
        "caption": "Screen: Case group (example).",
    },
    {
        "title": "4) Creating a new case",
        "toc": "Creation and required fields.",
        "body": (
            "On “New case”:\n"
            "- Fill Name and Date\n"
            "- Choose Category, Sub-category, Visa\n"
            "- Enter Legal fees and Additional fees\n"
            "- Enter Deposit 1 + Payment date + Method (Check/Card/Wire/Venmo)\n\n"
            "Deposits 2/3/4 are managed in “Edit case”."
        ),
        "image": "04_new_case.png",
        "caption": "Screen: New case (example).",
    },
    {
        "title": "5) Editing a case",
        "toc": "Full edition: amounts, deposits, statuses, comment.",
        "body": (
            "On “Edit case”:\n"
            "- Update Legal fees (US $)\n"
            "- Manage Deposits 1–4 with dates and methods\n"
            "- Set statuses + associated dates\n"
            "- Fill the Comment field\n\n"
            "After saving: check that boxes remain checked."
        ),
        "image": "05_edit_case.png",
        "caption": "Screen: Edit case (example).",
    },
    {
        "title": "6) Escrow (3 states) + amounts",
        "toc": "Active → to be claimed → claimed (amount = Deposit 1).",
        "body": (
            "Escrow has 3 states:\n"
            "1) Active\n"
            "2) To be claimed\n"
            "3) Claimed\n\n"
            "Rule: escrow amount always equals Deposit 1.\n"
            "A case must be in only one escrow state at a time."
        ),
        "image": "06_escrow.png",
        "caption": "Screen: Escrow (example).",
    },
    {
        "title": "7) Analytics",
        "toc": "Filters, comparisons, paid/unpaid.",
        "body": (
            "Analytics allows:\n"
            "- Filter by Category / Sub-category / Visa\n"
            "- Filter by Status\n"
            "- Filter paid / unpaid / negative balance\n"
            "- Time comparisons\n\n"
            "If a chart fails (KeyError Date), the chart probably received a dataframe without a Date column."
        ),
        "image": "07_analytics.png",
        "caption": "Screen: Analytics (example).",
    },
    {
        "title": "8) Export and best practices",
        "toc": "Export, archive, reload.",
        "body": (
            "Regular exporting is recommended.\n\n"
            "Best practices:\n"
            "- Timestamped multi-sheet Excel export\n"
            "- Keep history\n\n"
            "Typical error: “Timestamp is not JSON serializable”\n"
            "→ convert dates to strings before JSON save."
        ),
        "image": "08_export.png",
        "caption": "Screen: Export (example).",
    },
]

faq_en = [
    {
        "q": "Why does a checked box become unchecked after saving?",
        "a": (
            "Common causes:\n"
            "- alias columns (e.g., Dossier_envoye vs Dossier envoye)\n"
            "- a cleaning function overwriting values\n\n"
            "Fix:\n"
            "- normalize statuses on load\n"
            "- write to canonical columns and aliases if needed."
        ),
    },
    {
        "q": "Why does JSON become empty after Excel import?",
        "a": (
            "Cause: wrong Excel mapping or empty sheet.\n\n"
            "Fix:\n"
            "- ensure Clients.xlsx has rows\n"
            "- display imported row count before saving."
        ),
    },
]

sections = sections_fr if is_fr else sections_en
faq = faq_fr if is_fr else faq_en

st.markdown("## 📘 Guide")
for sec in sections:
    st.markdown(f"### {sec['title']}")
    st.write(sec["body"])
    if sec.get("image"):
        st.info(
            ("Capture attendue : " if is_fr else "Expected screenshot: ")
            + f"assets/help_screens/{sec['image']}\n"
            + ("(Le PDF l’intégrera automatiquement si le fichier existe.)" if is_fr else "(PDF will embed it automatically if present.)")
        )

st.markdown("---")
st.markdown("## ❓ FAQ")
for item in faq:
    st.markdown(f"**Q:** {item['q']}")
    st.write(item["a"])

st.markdown("---")
st.subheader("📄 Export PDF imprimable")

filename = f"Aide_{'FR' if is_fr else 'EN'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

if st.button("📤 Générer le PDF imprimable", type="primary"):
    pdf_bytes = build_help_pdf_bytes(
        lang_code=lang_code,
        app_name=APP_NAME,
        subtitle=subtitle,
        sections=sections,
        faq=faq,
        screenshots_dir="assets/help_screens",
        logo_path="assets/logo.png",
    )

    st.download_button(
        label="⬇️ Télécharger le PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )

st.markdown(
    """
### 📸 Captures d’écran (optionnel)
Pour inclure des captures dans le PDF, place tes images ici :

- `assets/help_screens/01_dashboard.png`
- `assets/help_screens/02_sidebar.png`
- `assets/help_screens/03_hierarchy.png`
- `assets/help_screens/04_new_case.png`
- `assets/help_screens/05_edit_case.png`
- `assets/help_screens/06_escrow.png`
- `assets/help_screens/07_analytics.png`
- `assets/help_screens/08_export.png`

Si un fichier n’existe pas, le PDF affichera une note “capture introuvable”.
"""
)