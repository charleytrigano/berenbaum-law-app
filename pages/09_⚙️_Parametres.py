import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()

import pandas as pd
import json
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json
from backend.json_validator import validate_and_fix_json


# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
st.title("⚙️ Paramètres & Outils avancés")

# ---------------------------------------------------------
# 🚨 VALIDATION AUTOMATIQUE AU DÉMARRAGE
# ---------------------------------------------------------
st.markdown("### 🧹 Validation automatique de la base de données")

fixed = validate_and_fix_json()

if fixed:
    st.warning("⚠️ Le JSON contenait des erreurs — corrections appliquées automatiquement.")
else:
    st.success("✔ Base JSON valide — aucune erreur détectée.")

if st.button("🔧 Réparer manuellement le JSON maintenant"):
    fixed = validate_and_fix_json()
    if fixed:
        st.success("✔ JSON réparé avec succès.")
    else:
        st.info("Aucune réparation nécessaire.")


# ---------------------------------------------------------
# ONGLET NAVIGATION
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "📥 Import Excel → JSON",
    "🔄 Synchronisation Dropbox"
])

# ---------------------------------------------------------
# TAB 1 — DEBUG SECRETS
# ---------------------------------------------------------
with tab1:
    st.subheader("🔐 Visualisation sécurisée des secrets")

    try:
        st.json(st.secrets)
    except Exception as e:
        st.error(f"Impossible de lire st.secrets : {e}")

    st.info("⚠️ Certaines valeurs sensibles peuvent être masquées par Streamlit pour votre sécurité.")


# ---------------------------------------------------------
# TAB 2 — DIAGNOSTIC DROPBOX
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Diagnostic de connexion Dropbox")

    dbx = None
    try:
        dbx = get_dbx()
        st.success("Connexion Dropbox OK ✔")
    except Exception as e:
        dbx = None
        st.error(f"❌ Erreur de connexion à Dropbox : {e}")

    st.markdown("### 📄 Fichier JSON configuré")
    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            content = res.content.decode("utf-8")
            st.json(json.loads(content))
            st.success("Lecture JSON Dropbox OK ✔")
        except Exception as e:
            st.error(f"❌ Impossible de lire le fichier JSON Dropbox : {e}")


# ---------------------------------------------------------
# TAB 3 — IMPORT EXCEL → JSON
# ---------------------------------------------------------
with tab3:
    st.subheader("📥 Import Excel")

    st.write("""
    Cet outil reconstruit entièrement `database.json` à partir des fichiers Excel:  
    - Clients.xlsx  
    - Visa.xlsx  
    - Escrow.xlsx  
    - ComptaCli.xlsx  
    """)

    if st.button("📥 Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()
            save_database(new_db)
            st.success("✔ Import Excel terminé — JSON mis à jour.")
            st.json(new_db)
        except Exception as e:
            st.error(f"❌ Erreur d’import : {e}")


# ---------------------------------------------------------
# TAB 4 — SYNCHRONISATION
# ---------------------------------------------------------
with tab4:
    st.subheader("🔄 Synchronisation Dropbox")

    st.write("Recharge la base actuelle puis la renvoie dans Dropbox.")

    if st.button("🔄 Synchroniser maintenant", type="primary"):
        try:
            db = load_database()
            save_database(db)
            st.success("✔ Synchronisation effectuée avec succès.")
            st.json(db)
        except Exception as e:
            st.error(f"❌ Erreur lors de la synchronisation : {e}")
