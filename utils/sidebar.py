# utils/sidebar.py
import os
import streamlit as st

try:
    from streamlit.errors import StreamlitPageNotFoundError
except Exception:
    StreamlitPageNotFoundError = Exception


# =====================================================
# OUTIL SÉCURISÉ POUR LIENS DE PAGES
# =====================================================
def safe_page_link(path: str, label: str):
    """
    Affiche un lien vers une page Streamlit sans jamais faire planter l'app.
    - Vérifie l'existence du fichier
    - Capture les erreurs StreamlitPageNotFoundError
    """
    if not os.path.exists(path):
        st.markdown(
            f"<span style='opacity:0.5'>🚫 {label} (introuvable)</span>",
            unsafe_allow_html=True,
        )
        return

    try:
        st.page_link(path, label=label)
    except StreamlitPageNotFoundError:
        st.markdown(
            f"<span style='opacity:0.5'>⚠️ {label} (non chargé)</span>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            f"<span style='opacity:0.5'>❌ {label} (erreur)</span>",
            unsafe_allow_html=True,
        )


# =====================================================
# SIDEBAR PRINCIPALE
# =====================================================
def render_sidebar():
    with st.sidebar:

        # -------------------------------
        # LOGO CABINET
        # -------------------------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
        else:
            st.markdown("### 🏛️ Cabinet")

        st.markdown("---")

        # -------------------------------
        # NAVIGATION PRINCIPALE
        # -------------------------------
        safe_page_link("pages/00_Dashboard.py", "🏠 Dashboard")
        safe_page_link("pages/01_📁_Liste_dossiers.py", "📁 Liste des dossiers")
        safe_page_link("pages/02_➕_Nouveau_dossier.py", "➕ Nouveau dossier")
        safe_page_link("pages/03_✏️_Modifier_dossier.py", "✏️ Modifier un dossier")
        safe_page_link("pages/04_📊_Analyses.py", "📊 Analyses")
        safe_page_link("pages/06_💰_Escrow.py", "💰 Escrow")

        st.markdown("---")

        # -------------------------------
        # RÉFÉRENTIELS
        # -------------------------------
        safe_page_link("pages/07_🛂_Visa.py", "🛂 Visa")
        safe_page_link("pages/13_💲_Tarifs.py", "💲 Tarifs par Visa")

        st.markdown("---")

        # -------------------------------
        # EXPORTS & OUTILS
        # -------------------------------
        safe_page_link("pages/08_📤_Export_Excel.py", "📤 Export Excel")
        safe_page_link("pages/14_📤_Export_JSON_Excel.py", "🔄 Export JSON ↔ Excel")

        st.markdown("---")

        # -------------------------------
        # FICHES & DOCUMENTS
        # -------------------------------
        safe_page_link("pages/11_📄_Fiche_dossier.py", "📄 Fiche dossier")
        safe_page_link("pages/12_📁_Fiche_groupe_dossier.py", "📁 Fiche groupe dossier")

        st.markdown("---")

        # -------------------------------
        # ADMIN & AIDE
        # -------------------------------
        safe_page_link("pages/09_⚙️_Parametres.py", "⚙️ Paramètres")
        safe_page_link("pages/10_❓_Aide.py", "❓ Aide & mode d’emploi")

        st.markdown("---")
        st.caption("Berenbaum Law App — Usage interne cabinet")