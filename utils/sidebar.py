# utils/sidebar.py
import streamlit as st
import os


def render_sidebar():
    """
    Sidebar unique (logo + navigation custom).
    - Cache définitivement la navigation automatique Streamlit ("main", "View less", etc.)
    - Affiche le logo en haut
    - Fournit des liens vers les pages existantes (compatibles avec tes noms actuels)
    """

    # =====================================================
    # 1) CSS : cacher le menu automatique Streamlit (GARANTI)
    # =====================================================
    st.markdown(
        """
        <style>
        /* Cache le menu auto "Pages" (main / View less / etc.) */
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="stSidebarNavItems"] { display: none !important; }
        [data-testid="stSidebarNavSeparator"] { display: none !important; }

        /* Ajustements spacing logo */
        [data-testid="stSidebar"] img {
            margin-bottom: 16px;
            margin-top: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # 2) UI Sidebar
    # =====================================================
    with st.sidebar:
        # --- Logo ---
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=140)
        else:
            st.warning("⚠️ Logo introuvable : assets/logo.png")

        st.markdown("---")

        # =================================================
        # 3) Navigation custom (page_link)
        # IMPORTANT : chemins = noms EXACTS dans /pages
        # =================================================
        try:
            st.page_link("pages/00_Dashboard.py", label="🏠 Dashboard")
        except Exception:
            st.write("🏠 Dashboard")

        try:
            st.page_link("pages/01_📁_Liste_dossiers.py", label="📁 Liste dossiers")
        except Exception:
            st.write("📁 Liste dossiers")

        try:
            st.page_link("pages/02_➕_Nouveau_dossier.py", label="➕ Nouveau dossier")
        except Exception:
            st.write("➕ Nouveau dossier")

        try:
            st.page_link("pages/03_✏️_Modifier_dossier.py", label="✏️ Modifier dossier")
        except Exception:
            st.write("✏️ Modifier dossier")

        try:
            st.page_link("pages/04_📊_Analyses.py", label="📊 Analyses")
        except Exception:
            st.write("📊 Analyses")

        try:
            st.page_link("pages/06_💰_Escrow.py", label="💰 Escrow")
        except Exception:
            st.write("💰 Escrow")

        try:
            st.page_link("pages/07_🛂_Visa.py", label="🛂 Visa")
        except Exception:
            st.write("🛂 Visa")

        try:
            st.page_link("pages/08_📤_Export_Excel.py", label="📤 Export Excel")
        except Exception:
            st.write("📤 Export Excel")

        try:
            st.page_link("pages/09_⚙️_Parametres.py", label="⚙️ Paramètres")
        except Exception:
            st.write("⚙️ Paramètres")

        try:
            st.page_link("pages/10_❓_Aide.py", label="❓ Aide")
        except Exception:
            st.write("❓ Aide")

        try:
            st.page_link("pages/11_📄_Fiche_dossier.py", label="📄 Fiche dossier")
        except Exception:
            st.write("📄 Fiche dossier")

        try:
            st.page_link("pages/12_📁_Fiche_groupe_dossier.py", label="📁 Fiche groupe dossier")
        except Exception:
            st.write("📁 Fiche groupe dossier")

        try:
            st.page_link("pages/13_💲_Tarifs.py", label="💲 Tarifs")
        except Exception:
            st.write("💲 Tarifs")

        try:
            st.page_link("pages/14_📤_Export_JSON_Excel.py", label="📤 Export JSON ↔ Excel")
        except Exception:
            st.write("📤 Export JSON ↔ Excel")

        st.markdown("---")
        st.caption("Berenbaum Law App — Interne")