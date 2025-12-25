# utils/sidebar.py
import streamlit as st
import os

def render_sidebar():
    with st.sidebar:
        # ---------------- LOGO ----------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.write("")

        st.markdown("---")

        # ---------------- NAVIGATION ----------------
        st.page_link("pages/00_🏠_Dashboard.py", label="🏠 Dashboard")
        st.page_link("pages/01_📁_Liste_dossiers.py", label="📁 Liste des dossiers")
        st.page_link("pages/02_➕_Nouveau_dossier.py", label="➕ Nouveau dossier")
        st.page_link("pages/03_✏️_Modifier_dossier.py", label="✏️ Modifier dossier")
        st.page_link("pages/04_📊_Analyses.py", label="📊 Analyses")
        st.page_link("pages/06_💰_Escrow.py", label="💰 Escrow")
        st.page_link("pages/07_🛂_Visa.py", label="🛂 Visa")
        st.page_link("pages/08_📤_Export_Excel.py", label="📤 Export Excel")
        st.page_link("pages/09_⚙️_Parametres.py", label="⚙️ Paramètres")
        st.page_link("pages/10_❓_Aide.py", label="❓ Aide")
