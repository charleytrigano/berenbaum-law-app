# utils/sidebar.py
import streamlit as st
import os

# =====================================================
# SIDEBAR PRINCIPALE
# =====================================================
def render_sidebar():
    with st.sidebar:

        # -------------------------------------------------
        # LOGO CABINET
        # -------------------------------------------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
        else:
            st.markdown("### 🏛️ Cabinet")

        st.markdown("---")

        # -------------------------------------------------
        # NAVIGATION PRINCIPALE
        # -------------------------------------------------
        st.page_link("pages/00_🏠_Dashboard.py", label="🏠 Dashboard")
        st.page_link("pages/01_📁_Liste_dossiers.py", label="📁 Liste des dossiers")
        st.page_link("pages/02_➕_Nouveau_dossier.py", label="➕ Nouveau dossier")
        st.page_link("pages/03_✏️_Modifier_dossier.py", label="✏️ Modifier un dossier")
        st.page_link("pages/04_📊_Analyses.py", label="📊 Analyses")
        st.page_link("pages/05_🔎_Recherche_universelle.py", label="🔎 Recherche universelle")
        st.page_link("pages/06_💰_Escrow.py", label="💰 Escrow")

        st.markdown("---")

        # -------------------------------------------------
        # DONNÉES & PARAMÉTRAGE
        # -------------------------------------------------
        st.page_link("pages/07_🛂_Visa.py", label="🛂 Visas")
        st.page_link("pages/13_💲_Tarifs.py", label="💲 Tarifs par Visa")
        st.page_link("pages/08_📤_Export_Excel.py", label="📤 Export Excel")
        st.page_link("pages/14_📤_Export_JSON_Excel.py", label="🔄 Export JSON ↔ Excel")

        st.markdown("---")

        # -------------------------------------------------
        # FICHES & DOCUMENTS
        # -------------------------------------------------
        st.page_link("pages/11_📄_Fiche_dossier.py", label="📄 Fiche dossier")
        st.page_link("pages/12_📁_Fiche_groupe_dossier.py", label="📁 Fiche groupe dossier")

        st.markdown("---")

        # -------------------------------------------------
        # PARAMÈTRES & AIDE
        # -------------------------------------------------
        st.page_link("pages/09_⚙️_Parametres.py", label="⚙️ Paramètres")
        st.page_link("pages/10_❓_Aide.py", label="❓ Aide & mode d’emploi")

        st.markdown("---")

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------
        st.caption("Berenbaum Law App — Interne Cabinet")