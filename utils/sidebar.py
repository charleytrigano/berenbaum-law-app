# utils/sidebar.py
import os
import streamlit as st

try:
    # Streamlit >= 1.32
    from streamlit.errors import StreamlitPageNotFoundError
except Exception:  # pragma: no cover
    StreamlitPageNotFoundError = Exception


# =====================================================
# Helpers
# =====================================================
def _safe_page_link(path: str, label: str):
    """
    Affiche un lien vers une page Streamlit sans jamais casser l'app.
    - Vérifie l'existence du fichier
    - Attrape StreamlitPageNotFoundError si Streamlit ne "voit" pas la page
    """
    # 1) Fichier absent -> lien inactif
    if not os.path.exists(path):
        st.markdown(f"<span style='opacity:0.55'>{label} (introuvable)</span>", unsafe_allow_html=True)
        return

    # 2) Fichier présent mais Streamlit refuse -> lien inactif (no crash)
    try:
        st.page_link(path, label=label)
    except StreamlitPageNotFoundError:
        st.markdown(f"<span style='opacity:0.55'>{label} (non chargé par Streamlit)</span>", unsafe_allow_html=True)
    except Exception:
        # Dernier filet de sécurité : pas de crash
        st.markdown(f"<span style='opacity:0.55'>{label} (erreur lien)</span>", unsafe_allow_html=True)


def _logo_block():
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=140)
    else:
        st.markdown("### 🏛️ Cabinet")


# =====================================================
# Sidebar principale
# =====================================================
def render_sidebar():
    with st.sidebar:
        _logo_block()
        st.markdown("---")

        # -------------------------------------------------
        # NAVIGATION (paths EXACTS)
        # -------------------------------------------------
        # NOTE : si Streamlit Cloud n'aime pas certains noms Unicode,
        # cette sidebar ne cassera plus : elle "grise" simplement le lien.

        _safe_page_link("pages/00_🏠_Dashboard.py", "🏠 Dashboard")
        _safe_page_link("pages/01_📁_Liste_dossiers.py", "📁 Liste des dossiers")
        _safe_page_link("pages/02_➕_Nouveau_dossier.py", "➕ Nouveau dossier")
        _safe_page_link("pages/03_✏️_Modifier_dossier.py", "✏️ Modifier un dossier")
        _safe_page_link("pages/04_📊_Analyses.py", "📊 Analyses")
        _safe_page_link("pages/06_💰_Escrow.py", "💰 Escrow")

        st.markdown("---")

        _safe_page_link("pages/07_🛂_Visa.py", "🛂 Visa")
        _safe_page_link("pages/13_💲_Tarifs.py", "💲 Tarifs par Visa")
        _safe_page_link("pages/08_📤_Export_Excel.py", "📤 Export Excel")
        _safe_page_link("pages/14_📤_Export_JSON_Excel.py", "🔄 Export JSON ↔ Excel")

        st.markdown("---")

        _safe_page_link("pages/11_📄_Fiche_dossier.py", "📄 Fiche dossier")
        _safe_page_link("pages/12_📁_Fiche_groupe_dossier.py", "📁 Fiche groupe dossier")

        st.markdown("---")

        _safe_page_link("pages/09_⚙️_Parametres.py", "⚙️ Paramètres")
        _safe_page_link("pages/10_❓_Aide.py", "❓ Aide & mode d’emploi")

        st.markdown("---")
        st.caption("Berenbaum Law App — Interne Cabinet")