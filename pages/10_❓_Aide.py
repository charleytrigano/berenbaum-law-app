import streamlit as st
from utils.sidebar import render_sidebar

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="❓ Aide & User Guide",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

# =====================================================
# LANGUE
# =====================================================
lang = st.radio(
    "🌍 Langue / Language",
    ["🇫🇷 Français", "🇺🇸 English"],
    horizontal=True
)

st.markdown("---")

# =====================================================
# =============== VERSION FRANÇAISE ====================
# =====================================================
if lang == "🇫🇷 Français":

    st.title("❓ AIDE & MODE D’EMPLOI")
    st.markdown("### Application de gestion des dossiers – Cabinet (usage interne)")

    st.markdown("""
    ### 📑 Sommaire
    - 1. Objectif de l’application  
    - 2. Navigation générale  
    - 3. Gestion des dossiers  
    - 4. Facturation & Escrow  
    - 5. Analyses & KPI  
    - 6. Exports  
    - 7. Bonnes pratiques  
    - 8. FAQ  
    - 9. Impression & PDF  
    - 10. Index alphabétique  
    """)

    st.markdown("---")
    st.subheader("1. Objectif de l’application")

    st.write("""
    Cette application permet de gérer l’ensemble des dossiers clients du cabinet,  
    de la création à la clôture, sans aucune compétence technique.

    Elle assure :
    - le suivi administratif,
    - la gestion financière,
    - la gestion des escrows,
    - l’organisation des dossiers parents et sous-dossiers,
    - les analyses et exports.
    """)

    st.subheader("2. Navigation générale")

    st.write("""
    Le menu latéral permet d’accéder aux pages suivantes :

    - 🏠 Dashboard – Vue globale  
    - 📁 Liste des dossiers  
    - ➕ Nouveau dossier  
    - ✏️ Modifier un dossier  
    - 📊 Analyses  
    - 💰 Escrow  
    - 🛂 Visa  
    - 💲 Tarifs  
    - 📤 Export Excel / JSON  
    - ⚙️ Paramètres  
    - ❓ Aide  
    """)

    st.subheader("3. Gestion des dossiers")

    st.write("""
    **Dossier parent**
    - Numéro simple : 13068
    - Dossier principal

    **Sous-dossier (fils)**
    - Numérotation : 13068-1, 13068-2…
    - Utilisé pour plusieurs procédures ou visas différents

    👉 Les sous-dossiers peuvent avoir un visa différent du parent.
    """)

    st.subheader("4. Facturation & Escrow")

    st.write("""
    **Facturation**
    - Honoraires
    - Autres frais
    - Acomptes (1 à 4) avec date et mode de règlement

    **RÈGLE ESCROW (CRITIQUE)**

    - Tant que le dossier n’est ni accepté, ni refusé, ni annulé :
      👉 **TOUS les acomptes sont en escrow**

    - Dès qu’un dossier est accepté / refusé / annulé :
      👉 le montant passe en **Escrow à réclamer**

    - Une fois réclamé :
      👉 **Escrow réclamé**

    Un historique escrow est conservé automatiquement.
    """)

    st.subheader("5. Analyses & KPI")

    st.write("""
    KPI disponibles :
    - Nombre de dossiers
    - Acceptés / Refusés / Annulés
    - Soldés / Non soldés
    - Solde négatif
    - Montants facturés / encaissés
    - Escrow total

    Filtres :
    - Années
    - Catégories
    - Sous-catégories
    - Visa
    - Statuts
    - Comparaisons multi-périodes
    """)

    st.subheader("6. Exports")

    st.write("""
    **Excel**
    - Export multi-feuilles
    - Horodaté
    - Sans signature

    **PDF**
    - Fiche dossier
    - Fiche groupe dossier (parent + fils)
    """)

    st.subheader("7. Bonnes pratiques")

    st.write("""
    ✔ Ne jamais modifier le JSON manuellement  
    ✔ Toujours vérifier les dates de paiement  
    ✔ Utiliser les sous-dossiers pour visas multiples  
    ✔ Utiliser les exports pour archivage  
    """)

    st.subheader("8. FAQ")

    st.write("""
    **Pourquoi un dossier n’apparaît pas ?**
    → Vérifier les filtres.

    **Pourquoi l’escrow ≠ total encaissé ?**
    → Tous les acomptes restent en escrow tant que le dossier n’est pas clôturé.

    **Puis-je modifier un visa sur un sous-dossier ?**
    → Oui.
    """)

    st.subheader("9. Impression & PDF")

    st.write("""
    Cette aide est :
    - consultable en ligne,
    - imprimable,
    - exportable en PDF,
    - document officiel interne du cabinet.
    """)

    st.subheader("10. Index alphabétique")

    index_fr = sorted([
        "Acompte", "Analyses", "Dashboard", "Dossier parent",
        "Dossier fils", "Escrow", "Export Excel", "Export PDF",
        "Facturation", "KPI", "Sous-dossier", "Statuts", "Visa"
    ])

    cols = st.columns(4)
    for i, item in enumerate(index_fr):
        cols[i % 4].write(f"• {item}")

# =====================================================
# =============== ENGLISH VERSION ======================
# =====================================================
else:

    st.title("❓ HELP & USER GUIDE")
    st.markdown("### Case Management Application – Internal Use")

    st.markdown("""
    ### 📑 Contents
    - 1. Application purpose  
    - 2. Navigation  
    - 3. Case management  
    - 4. Billing & Escrow  
    - 5. Analytics & KPIs  
    - 6. Exports  
    - 7. Best practices  
    - 8. FAQ  
    - 9. Printing & PDF  
    - 10. Alphabetical index  
    """)

    st.markdown("---")
    st.subheader("1. Application purpose")

    st.write("""
    This application allows the firm to manage all client cases,
    from creation to closure, without technical knowledge.

    It covers:
    - administrative tracking,
    - financial management,
    - escrow management,
    - parent / child case hierarchy,
    - analytics and exports.
    """)

    st.subheader("2. Navigation")

    st.write("""
    Use the left sidebar to access:
    - Dashboard
    - Case list
    - New case
    - Edit case
    - Analytics
    - Escrow
    - Visa
    - Pricing
    - Exports
    - Settings
    - Help
    """)

    st.subheader("3. Case management")

    st.write("""
    **Parent case**
    - Simple number: 13068

    **Child case**
    - Format: 13068-1, 13068-2…
    - Used for multiple procedures or visas

    Child cases may have a different visa than the parent.
    """)

    st.subheader("4. Billing & Escrow")

    st.write("""
    **Billing**
    - Fees
    - Additional costs
    - Payments with date and payment method

    **ESCROW RULE (CRITICAL)**

    - Until a case is accepted, refused, or cancelled:
      → ALL payments remain in escrow

    - When the case is accepted / refused / cancelled:
      → escrow becomes “to be claimed”

    - Once claimed:
      → escrow claimed

    Escrow history is automatically stored.
    """)

    st.subheader("5. Analytics & KPIs")

    st.write("""
    Available KPIs:
    - Total cases
    - Accepted / Refused / Cancelled
    - Paid / Unpaid
    - Negative balance
    - Billed / Collected amounts
    - Total escrow
    """)

    st.subheader("6. Exports")

    st.write("""
    **Excel**
    - Multi-sheet export
    - Timestamped
    - Audit-ready

    **PDF**
    - Single case
    - Parent + child group
    """)

    st.subheader("7. Best practices")

    st.write("""
    ✔ Never edit the JSON manually  
    ✔ Always check payment dates  
    ✔ Use child cases for multiple visas  
    ✔ Use exports for archiving  
    """)

    st.subheader("8. FAQ")

    st.write("""
    **Why does a case not appear?**
    → Check filters.

    **Why escrow ≠ collected amount?**
    → All payments remain in escrow until case closure.

    **Can I change a visa on a child case?**
    → Yes.
    """)

    st.subheader("9. Printing & PDF")

    st.write("""
    This guide is:
    - viewable online,
    - printable,
    - exportable to PDF,
    - the firm’s official internal manual.
    """)

    st.subheader("10. Alphabetical index")

    index_en = sorted([
        "Analytics", "Billing", "Case", "Dashboard",
        "Escrow", "Export", "Fees", "KPI",
        "Parent case", "Child case", "Visa"
    ])

    cols = st.columns(4)
    for i, item in enumerate(index_en):
        cols[i % 4].write(f"• {item}")