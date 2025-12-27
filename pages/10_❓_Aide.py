import streamlit as st
from datetime import datetime

from utils.sidebar import render_sidebar
from utils.help_pdf import build_help_pdf_bytes

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="❓ Aide & Mode d’emploi", page_icon="❓", layout="wide")
render_sidebar()
st.title("❓ Aide & Mode d’emploi (FR / EN)")

# ---------------------------------------------------------
# LANGUE
# ---------------------------------------------------------
lang = st.radio("🌍 Langue / Language", ["Français 🇫🇷", "English 🇺🇸"], horizontal=True)
is_fr = "Français" in lang
lang_code = "FR" if is_fr else "EN"

# ---------------------------------------------------------
# CONTENU STRUCTURÉ (AFFICHAGE + PDF)
# ---------------------------------------------------------
APP_NAME = "Berenbaum Law App"

SUBTITLE_FR = "Guide utilisateur officiel (néophytes) – Version imprimable + PDF"
SUBTITLE_EN = "Official user guide (beginners) – Printable version + PDF"

sections_fr = [
    {
        "title": "1) Objectif de l’application",
        "toc": "À quoi sert l’application et à qui elle s’adresse.",
        "body": (
            "Berenbaum Law App est une application Streamlit de gestion de dossiers juridiques.\n"
            "Elle centralise : clients, paiements, statuts, escrow, analyses et exports.\n\n"
            "- Vous n’avez besoin d’aucune compétence technique.\n"
            "- Tout se fait via des pages et des boutons.\n"
            "- La barre latérale (menu à gauche) sert à naviguer."
        ),
        "image": "01_dashboard.png",
        "caption": "Écran : Dashboard (exemple).",
    },
    {
        "title": "2) Navigation (barre latérale)",
        "toc": "Comprendre le menu et comment accéder aux pages.",
        "body": (
            "Le menu à gauche est toujours visible.\n\n"
            "Pages principales :\n"
            "- Dashboard : vue globale\n"
            "- Liste des dossiers : recherche + filtres\n"
            "- Nouveau dossier : création\n"
            "- Modifier dossier : édition complète\n"
            "- Escrow : suivi en 3 états\n"
            "- Analyses : statistiques\n"
            "- Export : Excel / JSON\n"
            "- Paramètres : outils avancés\n\n"
            "Astuce : si une page n’apparaît pas, cela signifie souvent que le fichier n’existe pas dans /pages "
            "ou que son nom a changé."
        ),
        "image": "02_sidebar.png",
        "caption": "Écran : Sidebar / Menu.",
    },
    {
        "title": "3) Dossiers parents et sous-dossiers",
        "toc": "Comprendre la logique parent/fils et les numéros.",
        "body": (
            "Un dossier peut être :\n"
            "- Parent (ex: 12937)\n"
            "- Fils (ex: 12937-1, 12937-2)\n\n"
            "Chaque fils peut avoir :\n"
            "- un visa différent,\n"
            "- ses propres montants,\n"
            "- ses propres acomptes,\n"
            "- ses propres statuts.\n\n"
            "Important : les KPI du Dashboard peuvent compter parents + fils."
        ),
        "image": "03_hierarchy.png",
        "caption": "Écran : Exemple de groupe dossier (parent + fils).",
    },
    {
        "title": "4) Créer un nouveau dossier",
        "toc": "Création simple + règles de paiement visibles.",
        "body": (
            "Sur la page « Nouveau dossier » :\n"
            "1) Remplir Nom, Date, Catégorie, Sous-catégorie, Visa\n"
            "2) Saisir Montant honoraires et Autres frais\n"
            "3) Saisir Acompte 1 + Date + Mode de règlement\n\n"
            "Note : les acomptes 2/3/4 seront visibles dans « Modifier dossier ».\n\n"
            "Mode de règlement : Chèque / CB / Virement / Venmo."
        ),
        "image": "04_new_case.png",
        "caption": "Écran : Nouveau dossier (exemple).",
    },
    {
        "title": "5) Modifier un dossier (édition complète)",
        "toc": "Tout modifier : facture, acomptes, dates, statuts, commentaire.",
        "body": (
            "Sur la page « Modifier dossier » vous pouvez modifier :\n"
            "- Identité / visa / catégorisation\n"
            "- Montants\n"
            "- Acomptes 1 à 4 + dates de paiement + modes de règlement\n"
            "- Statuts + dates associées\n"
            "- Commentaire\n\n"
            "Important : après « Enregistrer », le dossier doit conserver les cases cochées.\n"
            "Si ce n’est pas le cas, cela vient généralement d’un problème de normalisation JSON ou de colonnes alias."
        ),
        "image": "05_edit_case.png",
        "caption": "Écran : Modifier dossier (exemple).",
    },
    {
        "title": "6) Escrow (3 états) et montants",
        "toc": "Escrow actif → à réclamer → réclamé (montant = Acompte 1).",
        "body": (
            "L’Escrow fonctionne en 3 étapes :\n"
            "1) Escrow actif\n"
            "2) Escrow à réclamer\n"
            "3) Escrow réclamé\n\n"
            "Règle de montant : le montant escrow est toujours égal à Acompte 1.\n\n"
            "Lorsqu’un dossier passe de « à réclamer » vers « réclamé »,\n"
            "- il doit disparaître de « à réclamer »\n"
            "- et apparaître dans « réclamé »."
        ),
        "image": "06_escrow.png",
        "caption": "Écran : Escrow (exemple).",
    },
    {
        "title": "7) Analyses",
        "toc": "Filtres, statuts, soldés / non soldés, comparaisons.",
        "body": (
            "La page Analyses sert à piloter l’activité :\n"
            "- filtres Catégorie / Sous-catégorie / Visa\n"
            "- filtre Statuts\n"
            "- dossiers soldés / non soldés / solde < 0\n"
            "- comparaisons temporelles\n\n"
            "Note : si un graphique échoue avec KeyError Date, c’est souvent qu’on envoie au graphique un df déjà agrégé "
            "sans colonne Date. Les fonctions graphiques doivent recevoir des lignes dossiers, pas un groupby."
        ),
        "image": "07_analytics.png",
        "caption": "Écran : Analyses (exemple).",
    },
    {
        "title": "8) Export (Excel / JSON) et bonnes pratiques",
        "toc": "Exporter, archiver, recharger, Excel multi-feuilles horodaté.",
        "body": (
            "L’export est essentiel pour sauvegarder et travailler hors application.\n\n"
            "Recommandation :\n"
            "- Export Excel multi-feuilles horodaté\n"
            "- Stockage sur Dropbox\n"
            "- Utilisation Clients.xlsx pour audits\n\n"
            "Si tu vois : « Timestamp is not JSON serializable »\n"
            "- cela signifie qu’une date pandas Timestamp a été écrite dans le JSON.\n"
            "- il faut convertir en str avant save_database."
        ),
        "image": "08_export.png",
        "caption": "Écran : Export (exemple).",
    },
]

faq_fr = [
    {
        "q": "Pourquoi je ne vois plus mes dossiers après import Excel ?",
        "a": (
            "Causes fréquentes :\n"
            "- mauvais mapping des colonnes Excel\n"
            "- feuille Excel vide ou mauvais nom d’onglet\n"
            "- erreur silencieuse : l’import recrée un JSON vide\n\n"
            "Solution :\n"
            "- vérifier que Clients.xlsx contient bien des lignes\n"
            "- vérifier les noms exacts de colonnes attendues\n"
            "- ajouter un affichage du nombre de lignes importées avant save_database."
        ),
    },
    {
        "q": "Pourquoi une case cochée revient décochée ?",
        "a": (
            "Cause la plus fréquente : colonnes alias (ex: Dossier_envoye vs Dossier envoye) ou nettoyage JSON "
            "qui écrase la valeur.\n\n"
            "Solution :\n"
            "- normaliser les colonnes au chargement\n"
            "- écrire dans la colonne canonique ET ses alias si nécessaire\n"
            "- éviter les clean_database qui remettent systématiquement False."
        ),
    },
    {
        "q": "Pourquoi un dossier apparaît dans Escrow à réclamer alors qu’Escrow actif est décoché ?",
        "a": (
            "C’est souvent une règle métier automatique :\n"
            "- si le dossier est marqué « envoyé », on peut basculer vers « à réclamer ».\n\n"
            "Important : on ne change pas la logique si elle correspond à ton process.\n"
            "Dans tous les cas, le dossier doit être dans un seul état escrow à la fois."
        ),
    },
]

# EN content (mirror)
sections_en = [
    {
        "title": "1) Purpose of the application",
        "toc": "What the app is for and who it is for.",
        "body": (
            "Berenbaum Law App is a Streamlit application for legal case management.\n"
            "It centralizes clients, payments, statuses, escrow, analytics and exports.\n\n"
            "- No technical knowledge is required.\n"
            "- Everything is done via pages and buttons.\n"
            "- The left sidebar is used for navigation."
        ),
        "image": "01_dashboard.png",
        "caption": "Screen: Dashboard (example).",
    },
    {
        "title": "2) Navigation (sidebar)",
        "toc": "How to use the menu and open pages.",
        "body": (
            "The left sidebar is always visible.\n\n"
            "Main pages:\n"
            "- Dashboard: global overview\n"
            "- Case list: search + filters\n"
            "- New case: create\n"
            "- Edit case: full edition\n"
            "- Escrow: 3-state tracking\n"
            "- Analytics: statistics\n"
            "- Export: Excel / JSON\n"
            "- Settings: advanced tools\n\n"
            "Tip: if a page is missing, the file may not exist in /pages or its name changed."
        ),
        "image": "02_sidebar.png",
        "caption": "Screen: Sidebar / Menu.",
    },
    {
        "title": "3) Parent and child cases",
        "toc": "Understand parent/child logic and numbering.",
        "body": (
            "A case can be:\n"
            "- Parent (e.g., 12937)\n"
            "- Child (e.g., 12937-1, 12937-2)\n\n"
            "Each child case can have:\n"
            "- a different visa,\n"
            "- its own amounts,\n"
            "- its own deposits,\n"
            "- its own statuses.\n\n"
            "Dashboard KPIs may count both parents and children."
        ),
        "image": "03_hierarchy.png",
        "caption": "Screen: Case group example (parent + children).",
    },
    {
        "title": "4) Creating a new case",
        "toc": "Simple creation + visible payment rules.",
        "body": (
            "On the “New case” page:\n"
            "1) Fill Name, Date, Category, Sub-category, Visa\n"
            "2) Enter Legal fees and Additional fees\n"
            "3) Enter Deposit 1 + Payment date + Payment method\n\n"
            "Note: Deposits 2/3/4 are handled in “Edit case”.\n\n"
            "Payment method: Check / Card / Wire / Venmo."
        ),
        "image": "04_new_case.png",
        "caption": "Screen: New case (example).",
    },
    {
        "title": "5) Editing a case (full edition)",
        "toc": "Edit billing, deposits, dates, statuses, comment.",
        "body": (
            "On “Edit case”, you can edit:\n"
            "- identity / visa / categorization\n"
            "- amounts\n"
            "- deposits 1–4 + payment dates + payment methods\n"
            "- statuses + associated dates\n"
            "- comments\n\n"
            "Important: after saving, checkboxes must remain checked.\n"
            "If not, it is usually due to JSON normalization or alias columns."
        ),
        "image": "05_edit_case.png",
        "caption": "Screen: Edit case (example).",
    },
    {
        "title": "6) Escrow (3 states) and amounts",
        "toc": "Active → To be claimed → Claimed (amount = Deposit 1).",
        "body": (
            "Escrow works in 3 steps:\n"
            "1) Active\n"
            "2) To be claimed\n"
            "3) Claimed\n\n"
            "Amount rule: escrow amount always equals Deposit 1.\n\n"
            "When moving from “to be claimed” to “claimed”,\n"
            "- it must disappear from “to be claimed”\n"
            "- and appear under “claimed”."
        ),
        "image": "06_escrow.png",
        "caption": "Screen: Escrow (example).",
    },
    {
        "title": "7) Analytics",
        "toc": "Filters, statuses, paid/unpaid, comparisons.",
        "body": (
            "Analytics is used to monitor activity:\n"
            "- Category / Sub-category / Visa filters\n"
            "- Status filter\n"
            "- paid / unpaid / negative balance\n"
            "- time comparisons\n\n"
            "If a chart fails with KeyError Date, the chart probably received a grouped dataframe "
            "without a Date column. Charts must receive case-level rows, not a groupby result."
        ),
        "image": "07_analytics.png",
        "caption": "Screen: Analytics (example).",
    },
    {
        "title": "8) Export (Excel / JSON) and best practices",
        "toc": "Export, archive, reload, multi-sheet Excel with timestamp.",
        "body": (
            "Export is essential for backup and offline work.\n\n"
            "Recommendation:\n"
            "- timestamped multi-sheet Excel export\n"
            "- store on Dropbox\n"
            "- use Clients.xlsx for audits\n\n"
            "If you see: “Timestamp is not JSON serializable”,\n"
            "- a pandas Timestamp was written into JSON.\n"
            "- convert to string before save_database."
        ),
        "image": "08_export.png",
        "caption": "Screen: Export (example).",
    },
]

faq_en = [
    {
        "q": "Why do I see no cases after Excel import?",
        "a": (
            "Common causes:\n"
            "- wrong Excel column mapping\n"
            "- empty worksheet or wrong sheet name\n"
            "- silent failure producing an empty JSON\n\n"
            "Fix:\n"
            "- check Clients.xlsx has rows\n"
            "- check expected column names\n"
            "- display imported row counts before save_database."
        ),
    },
    {
        "q": "Why does a checked box become unchecked after saving?",
        "a": (
            "Most common cause: alias columns (e.g. Dossier_envoye vs Dossier envoye) or a JSON cleaner "
            "overwriting values.\n\n"
            "Fix:\n"
            "- normalize columns on load\n"
            "- write to canonical column AND its aliases\n"
            "- avoid cleaners that reset values to False."
        ),
    },
    {
        "q": "Why does a case appear in “Escrow to be claimed” when “Escrow active” is unchecked?",
        "a": (
            "Often due to a business rule:\n"
            "- if the case is marked as “sent”, it may move to “to be claimed”.\n\n"
            "In any case, a case must belong to one escrow state at a time."
        ),
    },
]

# ---------------------------------------------------------
# RENDU PAGE
# ---------------------------------------------------------
subtitle = SUBTITLE_FR if is_fr else SUBTITLE_EN
st.caption(subtitle)

sections = sections_fr if is_fr else sections_en
faq = faq_fr if is_fr else faq_en

st.markdown("## 📘 Guide")
for sec in sections:
    st.markdown(f"### {sec['title']}")
    st.write(sec["body"])

    # Info screenshot
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

# ---------------------------------------------------------
# EXPORT PDF PREMIUM
# ---------------------------------------------------------
st.markdown("---")
st.subheader("📄 Export PDF (mise en page premium)")

filename = f"Aide_{'FR' if is_fr else 'EN'}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

if st.button("📤 Générer le PDF imprimable", type="primary"):
    pdf_bytes = build_help_pdf_bytes(
        lang_code=("FR" if is_fr else "EN"),
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

Si un fichier n’existe pas, le PDF affichera simplement une note “capture introuvable”.
"""
)