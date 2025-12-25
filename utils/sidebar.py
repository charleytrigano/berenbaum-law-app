# utils/sidebar.py
import os
import streamlit as st


# ⚠️ CHEMINS EXACTS DES FICHIERS DANS /pages
PAGES = [
    ("pages/00_🏠_Dashboard.py", "🏠 Dashboard"),
    ("pages/01_📁_Liste_dossiers.py", "📁 Liste des dossiers"),
    ("pages/02_➕_Nouveau_dossier.py", "➕ Nouveau dossier"),
    ("pages/03_✏️_Modifier_dossier.py", "✏️ Modifier dossier"),
    ("pages/04_📊_Analyses.py", "📊 Analyses"),
    ("pages/06_💰_Escrow.py", "💰 Escrow"),
    ("pages/07_🛂_Visa.py", "🛂 Visa"),
    ("pages/08_📤_Export_Excel.py", "📤 Export Excel"),
    ("pages/09_⚙️_Parametres.py", "⚙️ Paramètres"),
    ("pages/10_❓_Aide.py", "❓ Aide"),
    ("pages/11_📄_Fiche_dossier.py", "📄 Fiche dossier"),
    ("pages/12_📁_Fiche_groupe_dossier.py", "📁 Fiche groupe dossiers"),
    ("pages/13_💲_Tarifs.py", "💲 Tarifs"),
    ("pages/14_📤_Export_JSON_Excel.py", "📤 Export JSON ↔ Excel"),
]


def render_sidebar():
    with st.sidebar:

        # ----------------------------
        # CSS (logo toujours en haut)
        # ----------------------------
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] img {
                margin-top: 0px !important;
                margin-bottom: 16px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------
        # LOGO
        # ----------------------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.warning("⚠️ Logo introuvable (assets/logo.png)")

        st.markdown("---")
        st.markdown("### Navigation")

        # ----------------------------
        # NAVIGATION ROBUSTE
        # (ne casse jamais l'app)
        # ----------------------------
        for path, label in PAGES:
            if os.path.exists(path):
                try:
                    st.page_link(path, label=label)
                except Exception:
                    # Sécurité ultime : n'empêche jamais l'app de démarrer
                    st.write(f"{label} (lien indisponible)")
            else:
                st.write(f"{label} (page absente)")

        st.markdown("---")