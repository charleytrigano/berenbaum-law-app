# utils/sidebar.py
import os
import re
import streamlit as st


def _extract_order(filename: str) -> int:
    """
    Extrait le préfixe numérique d'une page Streamlit: "08_📤_Export_Excel.py" -> 8
    Si absent, renvoie 9999.
    """
    m = re.match(r"^(\d+)_", filename)
    return int(m.group(1)) if m else 9999


def _label_from_filename(filename: str) -> str:
    """
    Transforme "08_📤_Export_Excel.py" -> "📤 Export Excel"
    """
    name = filename[:-3] if filename.endswith(".py") else filename
    name = re.sub(r"^\d+_", "", name)  # retire "08_"
    name = name.replace("_", " ")
    return name


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

        # --- AUTO NAVIGATION À PARTIR DU DOSSIER /pages ---
        pages_dir = "pages"
        if not os.path.isdir(pages_dir):
            st.error("❌ Dossier 'pages' introuvable.")
            return

        files = [f for f in os.listdir(pages_dir) if f.endswith(".py")]
        files = sorted(files, key=_extract_order)

        # Affiche tous les liens dans l'ordre: 00, 01, 02, ...
        for f in files:
            page_path = os.path.join(pages_dir, f)

            # IMPORTANT: st.page_link exige un chemin existant
            if os.path.exists(page_path):
                label = _label_from_filename(f)

                # Sécurité: si Streamlit refuse un nom bizarre, on n'explose pas
                try:
                    st.page_link(page_path, label=label)
                except Exception:
                    # fallback minimal si un fichier a un nom "incompatible"
                    st.write(f"• {label}")

        st.markdown("---")
