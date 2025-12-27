# pages/10_❓_Aide.py
import os
from datetime import datetime
import streamlit as st
from utils.sidebar import render_sidebar

# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(
    page_title="❓ Aide — Manuel interne Cabinet",
    page_icon="❓",
    layout="wide",
)
render_sidebar()
st.title("📘 Manuel interne — Berenbaum Law App")


# =========================================================
# PDF ENGINE (AUTONOME – AUCUNE DÉPENDANCE EXTERNE)
# =========================================================
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_fonts():
    fonts_dir = "assets/fonts"
    regular = os.path.join(fonts_dir, "DejaVuSans.ttf")
    bold = os.path.join(fonts_dir, "DejaVuSans-Bold.ttf")

    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont("DejaVu", regular))
    if os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))


def get_styles():
    base = getSampleStyleSheet()
    body_font = "DejaVu" if "DejaVu" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    bold_font = "DejaVu-Bold" if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"

    return {
        "title": ParagraphStyle(
            "title",
            fontName=bold_font,
            fontSize=20,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName=bold_font,
            fontSize=15,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName=bold_font,
            fontSize=12,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            fontName=body_font,
            fontSize=10.5,
            spaceAfter=6,
        ),
    }


def build_pdf(title, sections):
    register_fonts()
    styles = get_styles()
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    story.append(Paragraph(title, styles["title"]))
    story.append(Paragraph(
        f"Version interne — Généré le {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["body"]
    ))
    story.append(PageBreak())

    for section in sections:
        story.append(Paragraph(section["title"], styles["h1"]))
        for block in section["content"]:
            if block["type"] == "text":
                story.append(Paragraph(block["value"], styles["body"]))
            elif block["type"] == "list":
                for item in block["items"]:
                    story.append(Paragraph(f"• {item}", styles["body"]))
        story.append(PageBreak())

    doc.build(story)
    return buffer.getvalue()


# =========================================================
# CONTENU DU MANUEL (FR / EN)
# =========================================================

def manual_fr():
    return [
        {
            "title": "1) Objectif du manuel (Cabinet interne)",
            "content": [
                {"type": "text", "value": (
                    "Ce document est le manuel interne officiel de l’application Berenbaum Law App. "
                    "Il décrit les procédures opérationnelles standard (SOP), les règles métier, "
                    "et les bonnes pratiques pour garantir une saisie cohérente, une facturation fiable "
                    "et un suivi strict des dossiers."
                )},
                {"type": "list", "items": [
                    "Public : Assistant(e), Paralegal, Manager / Associé.",
                    "Objectif : zéro perte de données, cohérence du JSON, KPI exacts, traçabilité.",
                    "Principe : toute action de saisie doit produire un impact cohérent dans les KPI."
                ]},
            ],
        },
        {
            "title": "2) Vue d’ensemble de l’application",
            "content": [
                {"type": "text", "value": (
                    "L’application est organisée en onglets (pages) accessibles depuis la sidebar. "
                    "Chaque onglet remplit une fonction précise : création, modification, analyses, escrow, export, paramètres."
                )},
                {"type": "list", "items": [
                    "Dashboard : vue globale (KPI + filtres + listes synthétiques).",
                    "Liste des dossiers : consultation structurée (parents / fils si activé).",
                    "Nouveau dossier : création d’un dossier (avec Acompte 1 + date + mode + escrow si besoin).",
                    "Modifier dossier : mise à jour complète (statuts, dates, acomptes, escrow, commentaire).",
                    "Analyses : KPI + graphiques + filtres avancés.",
                    "Escrow : suivi opérationnel (Actif → À réclamer → Réclamé).",
                    "Export Excel : export/import (selon votre page existante).",
                    "Paramètres : diagnostic Dropbox, import Excel → JSON, synchronisation, validation.",
                    "Aide : manuel + export PDF (cette page)."
                ]},
            ],
        },
        {
            "title": "3) Règles métier fondamentales",
            "content": [
                {"type": "text", "value": (
                    "Les KPI et la qualité des données reposent sur des règles de cohérence. "
                    "Tout utilisateur doit les appliquer systématiquement."
                )},
                {"type": "h2", "value": "3.1 Dossier N et sous-dossiers"},
                {"type": "list", "items": [
                    "Dossier N peut être numérique (ex: 12904) ou composé (ex: 12937-1, 12937-2).",
                    "Un dossier composé doit être traité comme un dossier distinct dans les listes et KPI.",
                    "La cohérence de tri et d’affichage dépend de la normalisation (parent num, index, etc.)."
                ]},
                {"type": "text", "value": (
                    "Recommandation cabinet : utiliser un parent (12937) et des fils (12937-1, 12937-2) "
                    "pour séparer des visas différents, des étapes différentes ou des prestations additionnelles."
                )},
                {"type": "h2", "value": "3.2 Facturation et paiements"},
                {"type": "list", "items": [
                    "Total facturé = Montant honoraires (US $) + Autres frais (US $).",
                    "Total encaissé = Acompte 1 + Acompte 2 + Acompte 3 + Acompte 4.",
                    "Solde dû = Total facturé - Total encaissé.",
                    "Acompte 1 doit avoir sa date de paiement + mode (Chèque / CB / Virement / Venmo)."
                ]},
                {"type": "h2", "value": "3.3 Statuts et dates"},
                {"type": "list", "items": [
                    "Chaque statut (envoyé / accepté / refusé / annulé / RFE) doit être cohérent avec sa date.",
                    "Si un statut est coché, la date associée doit être renseignée lorsque connue.",
                    "Les KPI se basent sur les booléens : True / False (pas 0 / 1 / \"\").",
                ]},
                {"type": "h2", "value": "3.4 Escrow (règle officielle cabinet)"},
                {"type": "text", "value": (
                    "Le montant mis en escrow est toujours égal à Acompte 1. "
                    "Aucun autre acompte (2/3/4) ne va en escrow."
                )},
                {"type": "list", "items": [
                    "Escrow actif = fonds détenus en escrow (montant = Acompte 1).",
                    "Escrow à réclamer = action cabinet : demande de libération / facturation à effectuer.",
                    "Escrow réclamé = action terminée : dossier retiré de l’onglet “à réclamer”.",
                    "Transitions : Actif → À réclamer → Réclamé (dans cet ordre, sans doublons).",
                ]},
            ],
        },
        {
            "title": "4) Procédures opérationnelles — Assistant(e)",
            "content": [
                {"type": "text", "value": (
                    "Rôle : saisie initiale, réception paiements, mise à jour de base. "
                    "Objectif : dossier exploitable immédiatement par le paralegal."
                )},
                {"type": "h2", "value": "4.1 Créer un nouveau dossier"},
                {"type": "list", "items": [
                    "Aller dans “Nouveau dossier”.",
                    "Vérifier Catégorie, Sous-catégorie, Visa (doivent proposer des choix).",
                    "Saisir Montant honoraires et Autres frais.",
                    "Saisir Acompte 1 + Date acompte 1 + Mode de règlement (obligatoire si paiement reçu).",
                    "Cocher “Mettre en escrow” uniquement si Acompte 1 doit être détenu en escrow.",
                    "Ajouter un commentaire interne si nécessaire (contexte, urgence, pièces manquantes).",
                    "Enregistrer. Vérifier que le dossier apparaît dans Dashboard + Liste."
                ]},
                {"type": "h2", "value": "4.2 Encaisser un paiement ultérieur"},
                {"type": "list", "items": [
                    "Aller dans “Modifier dossier”.",
                    "Mettre à jour l’acompte concerné (2/3/4).",
                    "Renseigner Date paiement + Mode de règlement pour l’acompte modifié.",
                    "Enregistrer, puis vérifier l’impact dans Dashboard (Total encaissé / Solde dû)."
                ]},
            ],
        },
        {
            "title": "5) Procédures opérationnelles — Paralegal",
            "content": [
                {"type": "text", "value": (
                    "Rôle : suivi production, statuts, RFE, cohérence dossier. "
                    "Objectif : reporting exact et traçabilité."
                )},
                {"type": "h2", "value": "5.1 Mise à jour des statuts"},
                {"type": "list", "items": [
                    "Aller dans “Modifier dossier”.",
                    "Cocher/décocher le statut correspondant (Envoyé / Accepté / Refusé / Annulé / RFE).",
                    "Renseigner immédiatement la date correspondante (Date envoi, Date acceptation, etc.).",
                    "Enregistrer.",
                    "Contrôler l’apparition correcte dans KPI Analyses."
                ]},
                {"type": "h2", "value": "5.2 Gestion Escrow en production"},
                {"type": "list", "items": [
                    "Si Escrow actif est TRUE, vérifier que Acompte 1 est renseigné.",
                    "Quand le dossier passe à l’étape “à réclamer” (action cabinet), utiliser le bouton de transition dans l’onglet Escrow.",
                    "Quand le dossier est effectivement réclamé (action terminée), cliquer sur “Marquer comme réclamé”.",
                    "Vérifier que le dossier disparaît de “à réclamer” et apparaît dans “réclamé”."
                ]},
            ],
        },
        {
            "title": "6) Procédures opérationnelles — Manager / Associé",
            "content": [
                {"type": "text", "value": (
                    "Rôle : contrôle qualité, cohérence KPI, export, audits, performance du cabinet."
                )},
                {"type": "h2", "value": "6.1 Contrôle KPI"},
                {"type": "list", "items": [
                    "Dashboard : vérifier Nombre de dossiers = base réelle.",
                    "Comparer avec Liste des dossiers si dossier-id composés (xxxx-1/xxxx-2).",
                    "Contrôler Total facturé, Total encaissé, Solde dû.",
                    "Contrôler KPI Escrow global = somme des Acompte 1 des dossiers en escrow actif/à réclamer (selon définition)."
                ]},
                {"type": "h2", "value": "6.2 Export et audit"},
                {"type": "list", "items": [
                    "Utiliser Export Excel / PDF (si disponible) pour audit.",
                    "Exporter par état (Escrow actif / à réclamer / réclamé) avec totaux certifiés.",
                    "Archiver les exports avec horodatage.",
                ]},
            ],
        },
        {
            "title": "7) Dépannage — erreurs courantes",
            "content": [
                {"type": "list", "items": [
                    "Les KPI ne bougent pas : vérifier que les champs sont bien True/False (pas 0/1/\"\").",
                    "Un dossier n’apparaît pas : vérifier Dossier N, et qu’il existe dans db['clients'].",
                    "Statut ne s’enregistre pas : vérifier save_database + clean_database ne réécrit pas les champs en False.",
                    "Escrow incohérent : rappeler que le montant escrow = Acompte 1 uniquement.",
                    "Import Excel vide : vérifier format Clients.xlsx, noms de colonnes, sheet name, et erreurs Timestamp."
                ]},
            ],
        },
        {
            "title": "8) FAQ interne",
            "content": [
                {"type": "list", "items": [
                    "Q: Comment créer un sous-dossier ? R: Créer un Dossier N sous forme xxxx-1, xxxx-2 ; traiter comme dossier distinct.",
                    "Q: Pourquoi KPI Dashboard ≠ Liste ? R: Souvent dû aux Dossier N composés non normalisés ou filtrés.",
                    "Q: Pourquoi Escrow actif mais pas coché ? R: Vérifier transitions (Actif → À réclamer) et règles d’auto-déplacement si existantes.",
                    "Q: Pourquoi Export Excel échoue sur Timestamp ? R: Convertir dates en string avant save_database.",
                ]},
            ],
        },
    ]


def manual_en():
    return [
        {
            "title": "1) Purpose (Internal firm manual)",
            "content": [
                {"type": "text", "value": (
                    "This document is the official internal manual for Berenbaum Law App. "
                    "It describes standard operating procedures (SOP), business rules, and best practices "
                    "to ensure consistent data entry, reliable KPIs, and audit-ready case tracking."
                )},
                {"type": "list", "items": [
                    "Audience: Assistant, Paralegal, Manager/Partner.",
                    "Goal: zero data loss, JSON consistency, accurate KPIs, traceability.",
                    "Rule: every data entry must produce consistent KPI outcomes."
                ]},
            ],
        },
        {
            "title": "2) App overview",
            "content": [
                {"type": "text", "value": (
                    "The app is organized as pages accessible from the sidebar. "
                    "Each page has a precise operational function: creation, editing, analytics, escrow, export, settings."
                )},
                {"type": "list", "items": [
                    "Dashboard: global view (KPIs + filters + summary lists).",
                    "Cases list: structured browsing (parent/child when enabled).",
                    "New case: create a case (Deposit 1 + date + payment method + optional escrow).",
                    "Edit case: full update (statuses, dates, deposits, escrow, comments).",
                    "Analytics: KPIs + charts + advanced filters.",
                    "Escrow: operational tracking (Active → To claim → Claimed).",
                    "Export: Excel/PDF export/import (depending on your existing page).",
                    "Settings: Dropbox diagnostics, Excel→JSON import, sync, validation.",
                    "Help: manual + PDF export (this page)."
                ]},
            ],
        },
        {
            "title": "3) Core business rules",
            "content": [
                {"type": "text", "value": (
                    "KPIs and data quality rely on consistency rules. "
                    "All users must apply them systematically."
                )},
                {"type": "h2", "value": "3.1 Case number and sub-cases"},
                {"type": "list", "items": [
                    "Case number can be numeric (e.g., 12904) or composite (e.g., 12937-1, 12937-2).",
                    "A composite case must be treated as a distinct record in lists and KPIs.",
                    "Sorting/display consistency depends on normalization (parent num, index, etc.)."
                ]},
                {"type": "h2", "value": "3.2 Billing and payments"},
                {"type": "list", "items": [
                    "Total billed = Attorney fees + Other fees.",
                    "Total collected = Deposit 1 + Deposit 2 + Deposit 3 + Deposit 4.",
                    "Balance due = Total billed - Total collected.",
                    "Deposit 1 must include payment date + payment method (Check / Card / Wire / Venmo)."
                ]},
                {"type": "h2", "value": "3.3 Statuses and dates"},
                {"type": "list", "items": [
                    "Each status (sent/approved/denied/cancelled/RFE) must be consistent with its date.",
                    "If a status is checked, its date should be filled when known.",
                    "KPIs rely on booleans: True/False (not 0/1/empty strings)."
                ]},
                {"type": "h2", "value": "3.4 Escrow (official firm rule)"},
                {"type": "text", "value": (
                    "The escrow amount is always equal to Deposit 1 only. "
                    "Deposits 2/3/4 never go to escrow."
                )},
                {"type": "list", "items": [
                    "Escrow active = funds held in escrow (amount = Deposit 1).",
                    "Escrow to claim = firm action required (release request / billing step).",
                    "Escrow claimed = completed action, removed from 'to claim'.",
                    "Transitions: Active → To claim → Claimed (no duplicates)."
                ]},
            ],
        },
        {
            "title": "4) SOP — Assistant",
            "content": [
                {"type": "text", "value": (
                    "Role: initial entry, payment intake, base updates. "
                    "Goal: deliver an immediately workable file to the paralegal."
                )},
                {"type": "h2", "value": "4.1 Create a new case"},
                {"type": "list", "items": [
                    "Open “New case”.",
                    "Select Category, Sub-category, Visa (must provide choices).",
                    "Fill attorney fees and other fees.",
                    "Fill Deposit 1 + Deposit 1 date + payment method (mandatory if payment received).",
                    "Check escrow only if Deposit 1 must be held in escrow.",
                    "Add internal comments if needed.",
                    "Save. Verify it appears in Dashboard + Case list."
                ]},
            ],
        },
        {
            "title": "5) SOP — Paralegal",
            "content": [
                {"type": "text", "value": (
                    "Role: production tracking, status updates, RFE, consistency. "
                    "Goal: accurate reporting and traceability."
                )},
                {"type": "h2", "value": "5.1 Update statuses"},
                {"type": "list", "items": [
                    "Open “Edit case”.",
                    "Check/uncheck the appropriate status.",
                    "Fill the corresponding date (sent date, approval date, etc.).",
                    "Save. Verify impact in Analytics KPIs."
                ]},
                {"type": "h2", "value": "5.2 Escrow operations"},
                {"type": "list", "items": [
                    "If escrow active is TRUE, verify Deposit 1 is set.",
                    "When moving to “to claim”, use the transition button in Escrow page.",
                    "When action is completed, click “Mark as claimed”.",
                    "Verify it disappears from 'to claim' and appears in 'claimed'."
                ]},
            ],
        },
        {
            "title": "6) SOP — Manager/Partner",
            "content": [
                {"type": "text", "value": (
                    "Role: quality control, KPI consistency, exports, audits, firm performance."
                )},
                {"type": "h2", "value": "6.1 KPI controls"},
                {"type": "list", "items": [
                    "Dashboard: verify total cases matches reality.",
                    "Compare with Case list when composite IDs exist.",
                    "Validate Total billed / Total collected / Balance due.",
                    "Validate global escrow KPI equals sum of Deposit 1 of relevant escrow states (per firm definition)."
                ]},
            ],
        },
        {
            "title": "7) Troubleshooting",
            "content": [
                {"type": "list", "items": [
                    "KPIs not updating: ensure JSON values are True/False, not 0/1/\"\".",
                    "Case missing: verify it exists in db['clients'] and has correct Case number.",
                    "Status not saved: check save_database and cleaning layer is not resetting fields.",
                    "Excel import empty: verify sheet name/columns and Timestamp serialization issues."
                ]},
            ],
        },
        {
            "title": "8) Internal FAQ",
            "content": [
                {"type": "list", "items": [
                    "Q: How to create a sub-case? A: Use xxxx-1, xxxx-2; treat each as a separate record.",
                    "Q: Why Dashboard count differs from Case list? A: usually composite IDs or normalization issues.",
                    "Q: Why Excel export/import errors about Timestamp? A: convert all dates to strings before JSON write.",
                ]},
            ],
        },
    ]


# =========================================================
# UI STREAMLIT — AFFICHAGE + EXPORT PDF
# =========================================================
st.markdown("### 📌 Mode d’emploi interne (FR/EN) + Export PDF")

colA, colB, colC = st.columns([1, 1, 2])

language = colA.selectbox("Langue du manuel", ["Français (Interne Cabinet)", "English (Internal Firm)"])
doc_type = colB.selectbox("Type de document", ["Cabinet interne + Procédures opérationnelles"])
show_preview = colC.checkbox("Afficher l’aperçu dans la page", value=True)

if language.startswith("Français"):
    sections = manual_fr()
    pdf_title = "Manuel interne — Berenbaum Law App (FR)"
else:
    sections = manual_en()
    pdf_title = "Internal Manual — Berenbaum Law App (EN)"

# Aperçu UI
if show_preview:
    st.markdown("---")
    st.subheader("Aperçu du manuel")
    for s in sections:
        st.markdown(f"## {s['title']}")
        for block in s["content"]:
            if block["type"] == "text":
                st.write(block["value"])
            elif block["type"] == "list":
                for it in block["items"]:
                    st.write(f"• {it}")
        st.markdown("---")

# Export PDF
pdf_bytes = build_pdf(pdf_title, sections)

st.download_button(
    label="🖨️ Télécharger le PDF (prêt à imprimer)",
    data=pdf_bytes,
    file_name=f"Manuel_Interne_{'FR' if language.startswith('Français') else 'EN'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
    mime="application/pdf",
)

st.info(
    "Note: Les “captures d’écran” ne sont pas intégrées automatiquement dans ce PDF car Streamlit Cloud "
    "ne fournit pas un mécanisme fiable de capture dynamique. "
    "Si vous souhaitez une version PDF avec captures, fournissez 3-5 screenshots (PNG/JPG) et je vous renverrai "
    "la version enrichie (FR/EN)."
)
