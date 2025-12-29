# utils/sidebar.py
import os
import streamlit as st

try:
    from streamlit.errors import StreamlitPageNotFoundError
except Exception:
    StreamlitPageNotFoundError = Exception


# =====================================================
# LIEN DE PAGE SÉCURISÉ (ANTI-CRASH)
# =====================================================
def safe_page_link(path: str, label: str):
    if not os.path.exists(path):
        return  # on n’affiche rien si la page n’existe pas

    try:
        st.page_link(path, label=label)
    except StreamlitPageNotFoundError:
        pass
    except Exception:
        pass


# =====================================================
# SIDEBAR ÉPURÉE
# =====================================================
def render_sidebar():
    with st.sidebar:

        # -------------------------------
        # LOGO UNIQUEMENT
        # -------------------------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)

        st.markdown("---")

        # -------------------------------
        # NAVIGATION PRINCIPALE
        # -------------------------------
        safe_page_link("pages/00_Dashboard.py", "🏠 Dashboard")
        safe_page_link("pages/01_📁_Liste_dossiers.py", "📁 Dossiers")
        safe_page_link("pages/02_➕_Nouveau_dossier.py", "➕ Nouveau dossier")
        safe_page_link("pages/03_✏️_Modifier_dossier.py", "✏️ Modifier dossier")
        safe_page_link("pages/04_📊_Analyses.py", "📊 Analyses")
        safe_page_link("pages/06_💰_Escrow.py", "💰 Escrow")

        st.markdown("---")

        # -------------------------------
        # RÉFÉRENTIELS
        # -------------------------------
        safe_page_link("pages/07_🛂_Visa.py", "🛂 Visas")
        safe_page_link("pages/13_💲_Tarifs.py", "💲 Tarifs")

        st.markdown("---")

        # -------------------------------
        # EXPORTS
        # -------------------------------
        safe_page_link("pages/08_📤_Export_Excel.py", "📤 Export Excel")
        safe_page_link("pages/14_📤_Export_JSON_Excel.py", "🔄 Export JSON ↔ Excel")

        st.markdown("---")

        # -------------------------------
        # FICHES
        # -------------------------------
        safe_page_link("pages/11_📄_Fiche_dossier.py", "📄 Fiche dossier")
        safe_page_link("pages/12_📁_Fiche_groupe_dossier.py", "📁 Fiche groupe")

        st.markdown("---")

        # -------------------------------
        # ADMIN / AIDE
        # -------------------------------
        safe_page_link("pages/09_⚙️_Parametres.py", "⚙️ Paramètres")
        safe_page_link("pages/10_❓_Aide.py", "❓ Aide")

        st.markdown("---")