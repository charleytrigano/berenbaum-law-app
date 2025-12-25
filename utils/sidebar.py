# utils/sidebar.py
import streamlit as st
import os

def render_sidebar():
    with st.sidebar:

        # =====================================================
        # 🎨 STYLE – Logo toujours en haut
        # =====================================================
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                padding-top: 10px;
            }
            [data-testid="stSidebar"] img {
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # =====================================================
        # 🖼️ LOGO
        # =====================================================
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=130)
        else:
            st.warning("⚠️ Logo introuvable (assets/logo.png)")

        st.markdown("---")

        # =====================================================
        # 🧭 NAVIGATION
        # =====================================================
        st.markdown("### 📂 Navigation")

        st.page_link("pages/00_🏠_Dashboard.py", label="🏠 Dashboard")
        st.page_link("pages/01_📁_Liste_dossiers.py", label="📁 Liste des dossiers")
        st.page_link("pages/02_➕_Nouveau_dossier.py", label="➕ Nouveau dossier")
        st.page_link("pages/03_✏️_Modifier_dossier.py", label="✏️ Modifier dossier")
        st.page_link("pages/11_📄_Fiche_dossier.py", label="📄 Fiche dossier")
        st.page_link("pages/12_📁_Fiche_groupe_dossier.py", label="📁 Groupe dossiers")

        st.markdown("---")

        # =====================================================
        # 💰 FINANCES
        # =====================================================
        st.markdown("### 💰 Finances")

        st.page_link("pages/06_💰_Escrow.py", label="💰 Escrow")
        st.page_link("pages/07_🛂_Visa.py", label="🛂 Visas & Tarifs")

        st.markdown("---")

        # =====================================================
        # 📊 ANALYSES
        # =====================================================
        st.markdown("### 📊 Analyses")

        st.page_link("pages/04_📊_Analyses.py", label="📊 Analyses")

        st.markdown("---")

        # =====================================================
        # 🔁 IMPORT / EXPORT
        # =====================================================
        st.markdown("### 🔁 Import / Export")

        st.page_link(
            "pages/14_🔄_Export_JSON_Excel.py",
            label="🔄 Export Excel ↔ JSON"
        )

        st.markdown("---")

        # =====================================================
        # ⚙️ PARAMÈTRES
        # =====================================================
        st.markdown("### ⚙️ Paramètres")

        st.page_link("pages/09_⚙️_Parametres.py", label="⚙️ Paramètres")
        st.page_link("pages/10_❓_Aide.py", label="❓ Aide")

        st.markdown("---")

        # =====================================================
        # ℹ️ FOOTER
        # =====================================================
        st.caption("© Berenbaum Law App — Gestion des dossiers")
