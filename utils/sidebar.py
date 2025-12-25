# utils/sidebar.py
import os
import streamlit as st


# Pages attendues (chemins "safe" + labels)
# IMPORTANT : on utilise les chemins EXACTS présents dans /pages.
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
    ("pages/12_📁_Fiche_groupe_dossier.py", "📁 Fiche groupe"),
    ("pages/13_💲_Tarifs.py", "💲 Tarifs"),
    # Attention : ton fichier 14 est tronqué dans ta liste ("14_📤_Expo")
    # On ne l'ajoute PAS tant que le nom exact n'est pas confirmé, sinon ça recrashe.
]


def render_sidebar():
    with st.sidebar:
        # ----------------------------
        # CSS logo toujours en haut
        # ----------------------------
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] img {
                margin-top: 0px !important;
                margin-bottom: 14px !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------
        # Logo
        # ----------------------------
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.warning("⚠️ Logo introuvable : assets/logo.png")

        st.markdown("---")

        # ----------------------------
        # Navigation robuste
        # - Ne plante jamais si une page manque
        # ----------------------------
        st.markdown("### Navigation")

        for path, label in PAGES:
            if os.path.exists(path):
                # Streamlit page_link peut lever si le "page" n'est pas reconnu :
                # on sécurise avec try/except pour éviter de casser toute l'app.
                try:
                    st.page_link(path, label=label)
                except Exception:
                    # fallback : affiche juste le label sans lien
                    st.write(label + " (lien indisponible)")
            else:
                # Page absente : on n'affiche pas de lien pour ne pas planter
                st.write(label + " (page manquante)")

        st.markdown("---")