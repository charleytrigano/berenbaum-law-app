import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()
import pandas as pd
import json
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json




st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
st.title("⚙️ Paramètres & Outils avancés")

# ---------------------------------------------------------
# Onglets de navigation
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "📥 Import Excel → JSON",
    "🔄 Synchronisation Dropbox"
])

# ---------------------------------------------------------
# TAB 1 - DEBUG SECRETS
# ---------------------------------------------------------
with tab1:
    st.subheader("🔐 Visualisation des secrets utilisés")

    try:
        st.json(st.secrets)
    except Exception as e:
        st.error(f"Impossible de lire st.secrets : {e}")

    st.info("⚠️ Les valeurs critiques sont masquées automatiquement pour la sécurité.")

# ---------------------------------------------------------
# TAB 2 - DIAGNOSTIC DROPBOX
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Analyse de connexion et lecture des fichiers Dropbox")

    dbx = None
    try:
        dbx = get_dbx()
        st.success("Connexion Dropbox OK ✔")
    except Exception as e:
        st.error(f"❌ Erreur connexion Dropbox : {e}")

    st.write("### 📄 Fichier JSON configuré")
    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            content = res.content.decode("utf-8")
            st.json(json.loads(content))
            st.success("Lecture JSON Dropbox OK ✔")
        except Exception as e:
            st.error(f"❌ Erreur lecture JSON : {e}")

# ---------------------------------------------------------
# TAB 3 - IMPORT EXCEL
# ---------------------------------------------------------
with tab3:
    st.subheader("📥 Importer les fichiers Excel et recréer le JSON")

    st.write("""
    Cet outil lit :  
    - Clients.xlsx  
    - Visa.xlsx  
    - Escrow.xlsx  
    - ComptaCli.xlsx  
    et reconstruit entièrement *database.json*.
    """)

    if st.button("📥 Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()
            save_database(new_db)
            st.success("✔ Import Excel terminé — JSON mis à jour.")
            st.json(new_db)
        except Exception as e:
            st.error(f"❌ Erreur import : {e}")

# ---------------------------------------------------------
# TAB 4 - SYNCHRONISATION
# ---------------------------------------------------------
with tab4:
    st.subheader("🔄 Forcer la synchronisation Dropbox")

    st.write("Recharge la base actuelle et la renvoie dans Dropbox.")

    if st.button("🔄 Synchroniser maintenant", type="primary"):
        try:
            db = load_database()
            save_database(db)
            st.success("✔ Synchronisation effectuée.")
            st.json(db)
        except Exception as e:
            st.error(f"❌ Erreur synchronisation : {e}")
