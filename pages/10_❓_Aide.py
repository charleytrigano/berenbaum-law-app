# pages/10_❓_Aide.py
import os
from datetime import datetime

import streamlit as st

from utils.sidebar import render_sidebar


# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(
    page_title="❓ Aide",
    page_icon="❓",
    layout="wide",
)
render_sidebar()
st.title("❓ Aide & Mode d’emploi (Interne) — Berenbaum Law App")


# =========================================================
# PDF BUILDER (INTERNAL, NO EXTRA IMPORTS)
# =========================================================
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_fonts():
    """
    En environnement Streamlit Cloud, certaines polices peuvent manquer.
    On tente d'utiliser DejaVu si disponible (meilleure gestion des accents).
    """
    fonts_dir = os.path.join("assets", "fonts")
    regular = os.path.join(fonts_dir, "DejaVuSans.ttf")
    bold = os.path.join(fonts_dir, "DejaVuSans-Bold.ttf")

    if os.path.exists(regular):
        try:
            pdfmetrics.registerFont(TTFont("DejaVu", regular))
        except Exception:
            pass
    if os.path.exists(bold):
        try:
            pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))
        except Exception:
            pass


def _styles():
    base = getSampleStyleSheet()

    # Choix de police (fallback Helvetica)
    font_body = "DejaVu" if "DejaVu" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    font_bold = "DejaVu-Bold" if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"

    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=font_bold,
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#111111"),
            spaceAfter=10,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName=font_bold,
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#111111"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=font_bold,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#111111"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName=font_body,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#222222"),
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["BodyText"],
            fontName=font_body,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#444444"),
            spaceAfter=4,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["BodyText"],
            fontName="Courier",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#222222"),
            spaceAfter=6,
        ),
    }


def _escape(s: str) -> str:
    # ReportLab Paragraph utilise un subset HTML, on sécurise quelques caractères
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _header_footer(canvas, doc, title_text: str, cabinet_footer: str | None = None):
    canvas.saveState()

    # Ligne fine
    canvas.setStrokeColor(colors.HexColor("#DDDDDD"))
    canvas.setLineWidth(0.5)
    canvas.line(1.7 * cm, 1.6 * cm, A4[0] - 1.7 * cm, 1.6 * cm)

    # Texte footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#666666"))

    left = title_text
    right = f"Page {doc.page}"

    canvas.drawString(1.7 * cm, 1.1 * cm, left)
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.1 * cm, right)

    if cabinet_footer:
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawCentredString(A4[0] / 2, 1.1 * cm, cabinet_footer)

    canvas.restoreState()


def _try_add_screenshots(story, stl, screenshots_dir: str, lang_code: str):
    """
    Ajoute des captures si le dossier existe.
    Convention conseillée :
      - assets/help_screens/FR/*.png (ou .jpg)
      - assets/help_screens/EN/*.png (ou .jpg)
    Sinon, on prend directement assets/help_screens/*.png
    """
    if not os.path.isdir(screenshots_dir):
        return

    lang_dir = os.path.join(screenshots_dir, lang_code)
    target_dir = lang_dir if os.path.isdir(lang_dir) else screenshots_dir

    imgs = []
    for fn in sorted(os.listdir(target_dir)):
        low = fn.lower()
        if low.endswith(".png") or low.endswith(".jpg") or low.endswith(".jpeg"):
            imgs.append(os.path.join(target_dir, fn))

    if not imgs:
        return

    story.append(Paragraph(_escape("📸 Captures d’écran commentées" if lang_code == "FR" else "📸 Commented screenshots"), stl["h1"]))
    story.append(Paragraph(_escape(
        "Les captures ci-dessous sont optionnelles : ajoute simplement des images dans assets/help_screens."
        if lang_code == "FR"
        else "Screenshots below are optional: just add images inside assets/help_screens."
    ), stl["body"]))
    story.append(Spacer(1, 6))

    # On insère 1 image par page (max largeur)
    max_w = A4[0] - (2 * 2.0 * cm)
    max_h = A4[1] - (2 * 3.0 * cm)

    for path in imgs:
        try:
            story.append(Paragraph(_escape(os.path.basename(path)), stl["small"]))
            story.append(Image(path, width=max_w, height=max_h, kind="proportional"))
            story.append(PageBreak())
        except Exception:
            continue


def build_help_pdf_bytes(
    *,
    lang_code: str,
    app_name: str,
    subtitle: str,
    sections: list,
    faq: list,
    screenshots_dir: str = "assets/help_screens",
    logo_path: str = "assets/logo.png",
    cabinet_meta: dict | None = None,
) -> bytes:
    _register_fonts()
    stl = _styles()

    cabinet_meta = cabinet_meta or {}
    cabinet_footer = cabinet_meta.get("footer", None)

    from io import BytesIO
    buf = BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title=app_name,
        author=cabinet_meta.get("cabinet_name", "Berenbaum Law"),
    )

    story = []

    # -------------------------
    # PAGE DE GARDE CABINET (INTERNE)
    # -------------------------
    logo_cab = cabinet_meta.get("logo_cabinet", logo_path)
    if os.path.exists(logo_cab):
        try:
            story.append(Image(logo_cab, width=10.0 * cm, height=3.0 * cm))
            story.append(Spacer(1, 14))
        except Exception:
            pass

    story.append(Paragraph(_escape(cabinet_meta.get("cabinet_name", app_name)), stl["title"]))
    story.append(Paragraph(_escape(cabinet_meta.get("tagline", subtitle)), stl["body"]))
    story.append(Spacer(1, 10))

    # Bloc infos cabinet
    info_lines = cabinet_meta.get("contact_lines", [])
    if info_lines:
        tdata = [[Paragraph(_escape(x), stl["small"])] for x in info_lines]
        t = Table(tdata, colWidths=[A4[0] - 4.0 * cm])
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#DDDDDD")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)

    story.append(Spacer(1, 10))

    disclaimer = cabinet_meta.get("disclaimer", "")
    if disclaimer:
        story.append(Paragraph(_escape(disclaimer), stl["small"]))
        story.append(Spacer(1, 12))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc_code = cabinet_meta.get("doc_code", "")
    version_line = f"{doc_code} – Version : {now}" if doc_code else f"Version : {now}"
    story.append(Paragraph(_escape(version_line), stl["small"]))
    story.append(PageBreak())

    # -------------------------
    # SOMMAIRE
    # -------------------------
    story.append(Paragraph(_escape("Sommaire" if lang_code == "FR" else "Table of contents"), stl["h1"]))
    for i, s in enumerate(sections, start=1):
        story.append(Paragraph(_escape(f"{i}. {s['title']}"), stl["body"]))
    story.append(Spacer(1, 8))
    story.append(PageBreak())

    # -------------------------
    # SECTIONS
    # -------------------------
    for i, s in enumerate(sections, start=1):
        story.append(Paragraph(_escape(f"{i}. {s['title']}"), stl["h1"]))
        for b in s.get("bullets", []):
            story.append(Paragraph(_escape(f"• {b}"), stl["body"]))
        if s.get("notes"):
            story.append(Spacer(1, 4))
            story.append(Paragraph(_escape(s["notes"]), stl["small"]))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # -------------------------
    # FAQ
    # -------------------------
    story.append(Paragraph(_escape("FAQ (interne)" if lang_code == "FR" else "FAQ (internal)"), stl["h1"]))
    for item in faq:
        q = item.get("q", "")
        a = item.get("a", "")
        story.append(KeepTogether([
            Paragraph(_escape(f"Q: {q}"), stl["h2"]),
            Paragraph(_escape(a), stl["body"]),
            Spacer(1, 6),
        ]))

    story.append(PageBreak())

    # -------------------------
    # CAPTURES D’ECRAN (OPTIONNEL)
    # -------------------------
    _try_add_screenshots(story, stl, screenshots_dir=screenshots_dir, lang_code=lang_code)

    footer_title = f"{app_name} – {'Aide interne' if lang_code == 'FR' else 'Internal help'}"
    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, footer_title, cabinet_footer=cabinet_footer),
        onLaterPages=lambda c, d: _header_footer(c, d, footer_title, cabinet_footer=cabinet_footer),
    )

    return buf.getvalue()


# =========================================================
# CONTENU "CABINET INTERNE" (FR/EN)
# =========================================================
APP_NAME = "Berenbaum Law App"

CABINET_NAME = "Berenbaum Law"
CABINET_DOC_CODE = "BL-APP-HELP"
CABINET_CONTACT = {
    "phone": "+1 (xxx) xxx-xxxx",
    "email": "contact@yourfirm.com",
    "address": "New York, NY",
    "website": "www.yourfirm.com",
}

CABINET_DISCLAIMER_FR = (
    "Document interne – diffusion interdite sans autorisation. "
    "Les informations contenues ici ne constituent pas un avis juridique."
)
CABINET_DISCLAIMER_EN = (
    "Internal document – do not distribute without authorization. "
    "This document does not constitute legal advice."
)

CABINET_TAGLINE_FR = "Guide interne – Procédures, cohérence des données, exploitation et contrôles"
CABINET_TAGLINE_EN = "Internal guide – Procedures, data consistency, operations and controls"


def _content_fr():
    subtitle = "Mode d’emploi interne (FR) — Gestion des dossiers, statuts, paiements, escrow, exports"

    sections = [
        {
            "title": "Présentation générale (ce que fait l’application)",
            "bullets": [
                "Centralise les dossiers clients (création, modification, consultation).",
                "Normalise les champs pour éviter les incohérences (statuts, dates, montants).",
                "Fournit des KPI (tableau de bord) et des analyses (filtres, graphiques, soldes).",
                "Gère le cycle Escrow en 3 états : Escrow actif → Escrow à réclamer → Escrow réclamé.",
                "Permet l’import/export (Excel ↔ JSON) et l’administration (Paramètres).",
            ],
            "notes": "Usage interne : l’objectif est la fiabilité des données et la traçabilité des actions.",
        },
        {
            "title": "Navigation (Sidebar) – comment s’orienter",
            "bullets": [
                "Dashboard : vue globale (KPI + table dossiers).",
                "Liste des dossiers : recherche/filtrage et contrôle qualité.",
                "Nouveau dossier : création guidée.",
                "Modifier dossier : édition complète (paiements, statuts, commentaires, etc.).",
                "Escrow : pilotage des escrows par état + totaux exacts.",
                "Analyses : KPI + graphiques + filtres (incluant soldé / non soldé / <0).",
                "Paramètres : diagnostic Dropbox, import Excel, export, nettoyage/validation.",
                "Aide : documentation + export PDF (ce document).",
            ],
            "notes": "Le logo doit rester visible en haut de la sidebar sur toutes les pages.",
        },
        {
            "title": "Créer un dossier (Nouveau dossier) – procédure fiable",
            "bullets": [
                "Renseigner Nom, Date de création, Catégorie, Sous-catégorie et Visa (obligatoires).",
                "Saisir Montant honoraires (US $) et Autres frais (US $).",
                "Saisir Acompte 1, sa date de paiement, et le mode de règlement (Chèque/CB/Virement/Venmo).",
                "Ne pas saisir Acompte 2/3/4 ici (ils sont gérés dans Modifier dossier).",
                "Cocher Escrow uniquement si le dossier doit démarrer en escrow actif.",
                "Ajouter un Commentaire si nécessaire (information interne).",
            ],
            "notes": "Important : un dossier mal catégorisé casse les filtres et les statistiques.",
        },
        {
            "title": "Dossier Parent / Fils (sous-dossiers) – bonnes pratiques",
            "bullets": [
                "Un dossier peut être créé comme parent (principal) ou comme sous-dossier (fils).",
                "Un fils peut avoir un Visa différent du parent (cas fréquent).",
                "Toujours vérifier que parent/fils sont correctement rattachés (sinon décompte KPI incorrect).",
                "Pour les futurs dossiers : utiliser systématiquement la logique parent/fils prévue dans la création.",
            ],
            "notes": "Si tu constates un écart de décompte (ex. Dashboard ≠ Liste), vérifier le format et l’identifiant dossier.",
        },
        {
            "title": "Modifier un dossier – ce qu’il faut mettre à jour",
            "bullets": [
                "Infos générales : Nom, Date, Catégorie, Sous-catégorie, Visa, Commentaire.",
                "Facturation : Montant honoraires (US $) + Autres frais (US $).",
                "Paiements : Acompte 1/2/3/4, dates de paiement et modes de règlement associés.",
                "Statuts : cocher/décocher et renseigner les dates correspondantes.",
                "Escrow : gérer les états via les boutons de transition (voir section Escrow).",
            ],
            "notes": "Règle : toute modification doit être sauvegardée puis vérifiée en réouvrant le dossier.",
        },
        {
            "title": "Statuts (envoyé, accepté, refusé, annulé, RFE) – règles et impacts",
            "bullets": [
                "Cocher un statut doit l’écrire dans le JSON (booléen) et l’inclure dans les KPI/Analyses.",
                "Chaque statut doit avoir une date dédiée : Date envoi, Date acceptation, Date refus, Date annulation, Date reclamation.",
                "Ne pas laisser de dates incohérentes (ex. acceptation avant envoi).",
                "Les KPI d’Analyses incluent : envoyés, acceptés, refusés, annulés, RFE, escrow (selon page).",
            ],
            "notes": "Si un statut ne tient pas : suspicion d’alias de colonnes (ex. Dossier_envoye vs Dossier envoye).",
        },
        {
            "title": "Paiements & soldes – calculs standard",
            "bullets": [
                "Total facturé = Montant honoraires (US $) + Autres frais (US $).",
                "Total encaissé = Acompte 1 + Acompte 2 + Acompte 3 + Acompte 4.",
                "Solde dû = Total facturé − Total encaissé.",
                "Solde < 0 : trop-perçu (à investiguer).",
                "Analyses propose des filtres : dossiers non soldés, soldés, et < 0.",
            ],
            "notes": "La cohérence des nombres est essentielle : pas de texte dans les colonnes de montants.",
        },
        {
            "title": "Escrow (3 états) – logique interne et transitions",
            "bullets": [
                "Escrow actif : l’argent est en escrow (montant = Acompte 1).",
                "Escrow à réclamer : le dossier a quitté escrow actif et attend réclamation.",
                "Escrow réclamé : la réclamation est faite, le dossier doit disparaître des listes 'à réclamer'.",
                "Boutons requis : Actif → À réclamer, puis À réclamer → Réclamé.",
                "Chaque onglet Escrow affiche un total exact (nombre + montant).",
            ],
            "notes": "Si un dossier reste dans plusieurs états : vérifier que les flags sont exclusifs (un seul True à la fois).",
        },
        {
            "title": "Imports / Exports (Excel ↔ JSON) – précautions",
            "bullets": [
                "Import Excel → JSON : recrée la base à partir des fichiers Excel (Clients, Visa, Escrow, Compta).",
                "Export JSON → Excel : génère un fichier multi-feuilles horodaté pour mise à jour Clients.xlsx.",
                "Attention aux dates : éviter les Timestamp non sérialisables (convertir en string date).",
                "Toujours vérifier que la colonne Commentaire existe et est bien persistée.",
            ],
            "notes": "Après import : vérifier qu’il reste des dossiers (sinon fichier Excel vide / mauvais mapping).",
        },
        {
            "title": "Paramètres – diagnostic et maintenance",
            "bullets": [
                "Diagnostic Dropbox : confirme lecture/écriture du JSON et affiche le chemin Dropbox.",
                "Nettoyage/validation : corrige champs manquants, normalise types, supprime incohérences simples.",
                "Historique : conserver les actions importantes (imports, corrections, changements tarif).",
                "En cas d’erreur : lire le message exact et identifier le fichier/ligne concernée.",
            ],
            "notes": "La stabilité prime : éviter les modifications multiples sans validation intermédiaire.",
        },
    ]

    faq = [
        {
            "q": "Je coche un statut mais il ne reste pas coché après sauvegarde. Pourquoi ?",
            "a": "Cas le plus fréquent : alias de colonnes (ex. Dossier_envoye au lieu de Dossier envoye). "
                 "Il faut normaliser/écrire dans les colonnes canoniques et gérer la compatibilité.",
        },
        {
            "q": "Pourquoi un dossier apparaît dans 'Escrow à réclamer' alors que 'Escrow actif' n’est pas coché ?",
            "a": "Cela peut arriver si une transition a basculé le flag 'Escrow_a_reclamer' à True. "
                 "Vérifier que les états Escrow sont exclusifs et que les boutons appliquent la bonne logique.",
        },
        {
            "q": "Import Excel → JSON finit avec clients = []",
            "a": "Le fichier Excel peut être vide, mal lu, ou les colonnes ne correspondent pas. "
                 "Vérifier Clients.xlsx, les noms de colonnes, et la lecture dans l’onglet Paramètres.",
        },
        {
            "q": "Erreur : Timestamp is not JSON serializable",
            "a": "Une date est restée au format Timestamp (pandas). Convertir en string (YYYY-MM-DD) avant save_database.",
        },
        {
            "q": "Dashboard et Liste des dossiers ne comptent pas pareil",
            "a": "Souvent lié à la numérotation (ex. 12937-1/12937-2) ou à la logique parent/fils. "
                 "La Liste montre tout, le Dashboard peut filtrer/normaliser différemment si l’identifiant n’est pas stable.",
        },
    ]

    return subtitle, sections, faq


def _content_en():
    subtitle = "Internal user guide (EN) — Cases, statuses, payments, escrow, exports"

    sections = [
        {
            "title": "Overview (what the app does)",
            "bullets": [
                "Centralizes client cases (create, edit, view).",
                "Normalizes fields to prevent inconsistencies (statuses, dates, amounts).",
                "Provides KPIs (dashboard) and analytics (filters, charts, balances).",
                "Manages Escrow lifecycle with 3 states: Active → To claim → Claimed.",
                "Supports import/export (Excel ↔ JSON) and administration (Settings).",
            ],
            "notes": "Internal usage: accuracy and traceability are the priorities.",
        },
        {
            "title": "Navigation (Sidebar) – how to find pages",
            "bullets": [
                "Dashboard: global KPIs + case table.",
                "Case list: search/filter and quality checks.",
                "New case: guided creation.",
                "Edit case: full edit (payments, statuses, comments, etc.).",
                "Escrow: manage escrows by state + exact totals.",
                "Analytics: KPIs + charts + filters (including paid/unpaid/<0).",
                "Settings: Dropbox diagnostic, Excel import, exports, validation.",
                "Help: documentation + PDF export (this document).",
            ],
            "notes": "Logo should stay visible at the top of the sidebar on all pages.",
        },
        {
            "title": "Create a case (New case) – reliable procedure",
            "bullets": [
                "Fill Name, Creation date, Category, Sub-category, and Visa (mandatory).",
                "Enter Fees amount (US $) and Other fees (US $).",
                "Enter Deposit 1 plus its payment date and payment method (Check/Card/Wire/Venmo).",
                "Do not enter Deposit 2/3/4 here (managed in Edit case).",
                "Check Escrow only if the case starts in escrow active mode.",
                "Add an internal Comment if needed.",
            ],
            "notes": "A wrong categorization breaks filters and analytics.",
        },
        {
            "title": "Parent / Child cases – best practices",
            "bullets": [
                "A case can be a parent (main) or a child (sub-case).",
                "A child can have a different Visa from the parent (common).",
                "Always verify proper parent/child linkage to avoid KPI count mismatch.",
                "For future cases: consistently follow the parent/child workflow during creation.",
            ],
            "notes": "If you see a count mismatch (Dashboard ≠ List), check IDs and parent/child structure.",
        },
        {
            "title": "Edit a case – what must be updated",
            "bullets": [
                "General info: Name, Date, Category, Sub-category, Visa, Comment.",
                "Billing: Fees amount (US $) + Other fees (US $).",
                "Payments: Deposits 1–4 with payment dates and payment methods.",
                "Statuses: toggle and fill the related dates.",
                "Escrow: manage states via transition buttons (see Escrow section).",
            ],
            "notes": "Rule: after saving, reopen the case to confirm persistence.",
        },
        {
            "title": "Statuses (sent, accepted, refused, canceled, RFE) – rules & impact",
            "bullets": [
                "Toggling a status must write to JSON (boolean) and update KPIs/Analytics.",
                "Each status must have its own date field.",
                "Avoid inconsistent dates (e.g., accepted before sent).",
                "Analytics KPIs include: sent, accepted, refused, canceled, RFE, escrow (depending on page).",
            ],
            "notes": "If a status does not persist: suspect column aliases (e.g., Dossier_envoye vs Dossier envoye).",
        },
        {
            "title": "Payments & balances – standard formulas",
            "bullets": [
                "Total billed = Fees + Other fees.",
                "Total received = Deposit 1 + 2 + 3 + 4.",
                "Balance due = Total billed − Total received.",
                "Balance < 0 means overpayment (needs review).",
                "Analytics offers filters: unpaid / paid / <0.",
            ],
            "notes": "Amounts must be numeric (no text in amount columns).",
        },
        {
            "title": "Escrow (3 states) – internal logic & transitions",
            "bullets": [
                "Escrow active: money is in escrow (amount = Deposit 1).",
                "Escrow to claim: case moved out of active and awaits claim.",
                "Escrow claimed: claim completed; the case must disappear from 'to claim' list.",
                "Required buttons: Active → To claim, then To claim → Claimed.",
                "Each Escrow tab shows exact totals (count + amount).",
            ],
            "notes": "If a case appears in multiple escrow states: ensure state flags are mutually exclusive.",
        },
        {
            "title": "Imports / Exports (Excel ↔ JSON) – precautions",
            "bullets": [
                "Excel → JSON import rebuilds the database from Excel sources.",
                "JSON → Excel export creates a timestamped multi-sheet workbook.",
                "Dates must be strings (YYYY-MM-DD), not pandas Timestamp.",
                "Ensure the Comment field is preserved end-to-end.",
            ],
            "notes": "After import: verify cases are present; otherwise mapping or Excel is wrong/empty.",
        },
        {
            "title": "Settings – diagnostics & maintenance",
            "bullets": [
                "Dropbox diagnostic confirms JSON path and read/write access.",
                "Validation/cleanup normalizes missing fields and simple type issues.",
                "History keeps track of key actions (imports, fixes, tariff changes).",
                "On errors: read the exact file/line from traceback to target the fix.",
            ],
            "notes": "Stability first: avoid multiple unverified edits in a row.",
        },
    ]

    faq = [
        {
            "q": "I toggle a status but it resets after saving. Why?",
            "a": "Most common cause is column alias mismatch. Write to canonical columns and keep compatibility if needed.",
        },
        {
            "q": "Why is a case in 'Escrow to claim' while 'Escrow active' is not checked?",
            "a": "A transition may have set Escrow_a_reclamer to True. Ensure escrow states are mutually exclusive.",
        },
        {
            "q": "Excel → JSON import ends with clients = []",
            "a": "Excel may be empty, unreadable, or columns don’t match. Check Clients.xlsx and the mapping.",
        },
        {
            "q": "Error: Timestamp is not JSON serializable",
            "a": "A date stayed as pandas Timestamp. Convert to string YYYY-MM-DD before saving JSON.",
        },
        {
            "q": "Dashboard count differs from Case List count",
            "a": "Usually due to ID format (e.g., 12937-1/12937-2) or parent/child logic.",
        },
    ]

    return subtitle, sections, faq


# =========================================================
# UI (LANG + PDF EXPORT)
# =========================================================
lang = st.radio("🌍 Langue / Language", ["Français 🇫🇷", "English 🇺🇸"], horizontal=True)
is_fr = "Français" in lang
lang_code = "FR" if is_fr else "EN"

subtitle, sections, faq = _content_fr() if is_fr else _content_en()

st.markdown("### Contenu de l’aide" if is_fr else "### Help contents")
for s in sections:
    st.markdown(f"- **{s['title']}**")

st.markdown("---")
st.markdown("### Export PDF (Cabinet interne)" if is_fr else "### PDF Export (Internal firm version)")

with st.expander("⚙️ Paramètres PDF (optionnel)" if is_fr else "⚙️ PDF settings (optional)", expanded=False):
    st.write("Tu peux ajouter des captures dans `assets/help_screens/FR/` ou `assets/help_screens/EN/`." if is_fr
             else "You can add screenshots in `assets/help_screens/FR/` or `assets/help_screens/EN/`.")
    screenshots_dir = st.text_input("Dossier captures (screenshots dir)", value="assets/help_screens")
    logo_path = st.text_input("Logo (path)", value="assets/logo.png")
    logo_cabinet = st.text_input("Logo Cabinet (optionnel)", value="assets/logo_cabinet.png")

# Métadonnées cabinet interne
cab_tagline = CABINET_TAGLINE_FR if is_fr else CABINET_TAGLINE_EN
cab_disclaimer = CABINET_DISCLAIMER_FR if is_fr else CABINET_DISCLAIMER_EN

contact_lines = [
    CABINET_NAME,
    CABINET_CONTACT["address"],
    f"T: {CABINET_CONTACT['phone']}  |  E: {CABINET_CONTACT['email']}",
    CABINET_CONTACT["website"],
]

cabinet_meta = {
    "cabinet_name": CABINET_NAME,
    "tagline": cab_tagline,
    "disclaimer": cab_disclaimer,
    "doc_code": CABINET_DOC_CODE,
    "logo_cabinet": logo_cabinet if os.path.exists(logo_cabinet) else logo_path,
    "contact_lines": contact_lines,
    "footer": f"{CABINET_NAME} – {CABINET_DOC_CODE}",
}

colA, colB = st.columns([1, 2])
with colA:
    if st.button("📄 Générer le PDF" if is_fr else "📄 Generate PDF", type="primary"):
        pdf_bytes = build_help_pdf_bytes(
            lang_code=lang_code,
            app_name=APP_NAME,
            subtitle=subtitle,
            sections=sections,
            faq=faq,
            screenshots_dir=screenshots_dir,
            logo_path=logo_path,
            cabinet_meta=cabinet_meta,
        )
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{CABINET_DOC_CODE}_{lang_code}_{ts}.pdf"
        st.session_state["help_pdf_bytes"] = pdf_bytes
        st.session_state["help_pdf_filename"] = filename

with colB:
    if "help_pdf_bytes" in st.session_state:
        st.success("PDF prêt." if is_fr else "PDF ready.")
        st.download_button(
            label="⬇️ Télécharger le PDF" if is_fr else "⬇️ Download PDF",
            data=st.session_state["help_pdf_bytes"],
            file_name=st.session_state["help_pdf_filename"],
            mime="application/pdf",
        )

st.markdown("---")
st.markdown("### FAQ" if is_fr else "### FAQ")
for item in faq:
    with st.expander(f"Q: {item['q']}"):
        st.write(item["a"])