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

st.title("❓ AIDE & MODE D’EMPLOI")
st.markdown("### Application de gestion des dossiers – **Cabinet interne**")

# =====================================================
# LANGUAGE SELECTOR
# =====================================================
lang = st.radio(
    "🌐 Langue / Language",
    options=["Français 🇫🇷", "English 🇺🇸"],
    horizontal=True
)

# =====================================================
# TABS
# =====================================================
tabs = st.tabs([
    "📘 Objectif / Purpose",
    "🧭 Navigation",
    "📁 Dossiers",
    "💰 Facturation & Escrow",
    "📊 Analyses & KPI",
    "📤 Exports",
    "⚠️ Bonnes pratiques",
    "❓ FAQ",
    "📄 Impression & PDF"
])

# =====================================================
# FR VERSION
# =====================================================
if lang.startswith("Français"):

    with tabs[0]:
        st.subheader("1. Objectif de l’application")
        st.write("""
Cette application centralise **toute la gestion des dossiers du cabinet** :

- Suivi administratif (statuts, dates)
- Suivi financier (honoraires, acomptes, soldes)
- Gestion complète des escrows
- Dossiers parents & sous-dossiers
- Analyses, KPI et exports professionnels

👉 **Aucune connaissance technique requise.**
        """)

    with tabs[1]:
        st.subheader("2. Navigation générale")
        st.markdown("""
Le menu latéral donne accès à toutes les pages :

- 🏠 Dashboard
- 📁 Liste des dossiers
- ➕ Nouveau dossier
- ✏️ Modifier dossier
- 📊 Analyses
- 💰 Escrow
- 💲 Tarifs
- 📤 Exports
- 📄 Fiches dossiers
- ⚙️ Paramètres
- ❓ Aide
        """)
        st.info("Astuce : si une page n’apparaît pas, vérifier son nom exact dans le dossier /pages.")

    with tabs[2]:
        st.subheader("3. Gestion des dossiers")
        st.markdown("""
### Types de dossiers

**Dossier parent**
- Numéro simple (ex: 13068)

**Sous-dossier (fils)**
- Numérotation : 13068-1, 13068-2…
- Visa et facturation propres
        """)

    with tabs[3]:
        st.subheader("4. Facturation & Escrow")
        st.markdown("""
### Règle Escrow (fondamentale)

- Tant que le dossier n’est **ni accepté, ni refusé, ni annulé** :
  👉 **Tous les acomptes sont en escrow**
- Lorsqu’il est accepté / refusé / annulé :
  👉 Passage en **Escrow à réclamer**
- Étape finale :
  👉 **Escrow réclamé**

L’historique est conservé automatiquement.
        """)

    with tabs[4]:
        st.subheader("5. Analyses & KPI")
        st.markdown("""
KPI disponibles :
- Nombre de dossiers
- Acceptés / refusés / annulés
- Soldés / non soldés
- Soldes négatifs
- Montant total en escrow

Filtres :
- Multi-années
- Comparaison de périodes
- Statuts
        """)

    with tabs[5]:
        st.subheader("6. Exports")
        st.markdown("""
- Export Excel multi-feuilles
- Export PDF dossiers & groupes
- Export JSON ↔ Excel
        """)

    with tabs[6]:
        st.subheader("7. Bonnes pratiques")
        st.markdown("""
✔ Utiliser les filtres  
✔ Ne jamais modifier le JSON manuellement  
✔ Vérifier les dates de paiement  
✔ Utiliser les sous-dossiers pour visas multiples
        """)

    with tabs[7]:
        st.subheader("8. FAQ")
        st.markdown("""
**Pourquoi un dossier n’apparaît pas ?**  
➡ Vérifier les filtres actifs.

**Pourquoi l’escrow est élevé ?**  
➡ Tous les paiements restent en escrow tant que le dossier n’est pas finalisé.
        """)

    with tabs[8]:
        st.subheader("9. Impression & PDF")
        st.write("""
Cette aide est :
- Consultable en ligne
- Imprimable
- Exportable en PDF
        """)

# =====================================================
# EN VERSION
# =====================================================
else:

    with tabs[0]:
        st.subheader("1. Application Purpose")
        st.write("""
This application centralizes **all case management operations** of the firm:

- Administrative tracking
- Financial tracking
- Full escrow management
- Parent & sub-cases
- Analytics and exports
        """)

    with tabs[1]:
        st.subheader("2. Navigation")
        st.markdown("""
Main pages include:
- Dashboard
- Case List
- New Case
- Edit Case
- Analytics
- Escrow
- Fees
- Exports
- Help
        """)

    with tabs[2]:
        st.subheader("3. Case Management")
        st.markdown("""
**Parent Case**
- Simple number

**Sub-case**
- Numbering: 13068-1, 13068-2
- Independent visa & billing
        """)

    with tabs[3]:
        st.subheader("4. Billing & Escrow")
        st.markdown("""
### Escrow Rule

- Until accepted / refused / canceled:
  👉 All payments remain in escrow
- Then:
  👉 Escrow to claim
- Final:
  👉 Escrow claimed
        """)

    with tabs[4]:
        st.subheader("5. Analytics & KPIs")
        st.markdown("""
KPIs include:
- Case counts
- Status breakdown
- Escrow totals
- Multi-year comparisons
        """)

    with tabs[5]:
        st.subheader("6. Exports")
        st.markdown("""
- Excel exports
- PDF exports
- JSON ↔ Excel sync
        """)

    with tabs[6]:
        st.subheader("7. Best Practices")
        st.markdown("""
✔ Use filters  
✔ Never edit JSON manually  
✔ Verify payment dates  
✔ Use sub-cases properly
        """)

    with tabs[7]:
        st.subheader("8. FAQ")
        st.markdown("""
**Why is escrow high?**  
➡ All payments remain in escrow until case finalization.
        """)

    with tabs[8]:
        st.subheader("9. Printing & PDF")
        st.write("""
This guide is printable and exportable to PDF.
        """)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("© Cabinet – Internal Use Only")