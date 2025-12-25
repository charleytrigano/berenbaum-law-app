# utils/sidebar.py
import streamlit as st
import os
from PIL import Image

def _safe_page_link(page_path: str, label: str, icon: str = None):
    """
    Affiche un lien vers une page Streamlit uniquement si le fichier existe.
    Évite StreamlitPageNotFoundError qui casse toute l'app.
    """
    if os.path.exists(page_path):
        st.page_link(page_path, label=label, icon=icon)
        return True
    return False


def render_sidebar():
    with st.sidebar:
        # --- LOGO TOUJOURS EN HAUT ---
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] img {
                margin-top: 0px !important;
                margin-bottom: 14px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.warning("⚠️ Logo introuvable : assets/logo.png")

        st.markdown("---")

        # --- NAVIGATION (liens pages) ---
        # IMPORTANT : les chemins doivent correspondre EXACTEMENT aux noms de fichiers dans /pages
        _safe_page_link("pages/00_🏠_Dashboard.py", "🏠 Dashboard")
        _safe_page_link("pages/01_📁_Liste_dossiers.py", "📁 Liste des dossiers")
        _safe_page_link("pages/02_➕_Nouveau_dossier.py", "➕ Nouveau dossier")
        _safe_page_link("pages/03_✏️_Modifier_dossier.py", "✏️ Modifier dossier")
        _safe_page_link("pages/04_📊_Analyses.py", "📊 Analyses")
        _safe_page_link("pages/06_💰_Escrow.py", "💰 Escrow")
        _safe_page_link("pages/07_🛂_Visa.py", "🛂 Visa")
        _safe_page_link("pages/09_⚙️_Parametres.py", "⚙️ Paramètres")
        _safe_page_link("pages/10_❓_Aide.py", "❓ Aide")
        _safe_page_link("pages/11_📄_Fiche_dossier.py", "📄 Fiche dossier")

        # --- OPTIONNEL : Export Excel ↔ JSON ---
        # Ce lien ne s’affichera QUE si le fichier existe.
        # Tu peux garder ce bloc même si la page n’est pas encore créée.
        found = _safe_page_link(
            "pages/14_🔄_Export_JSON_Excel.py",
            "🔄 Export Excel ↔ JSON"
        )

        # (Option debug : si tu veux voir quand ça manque)
        # if not found:
        #     st.caption("ℹ️ Page Export Excel ↔ JSON non installée (fichier absent).")
