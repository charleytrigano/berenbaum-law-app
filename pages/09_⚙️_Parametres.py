import streamlit as st
import pandas as pd
import json
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json
from backend.json_validator import validate_and_fix_json, analyse_incoherences

# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="⚙️ Paramètres",
    page_icon="⚙️",
    layout="wide"
)

render_sidebar()
st.title("⚙️ Paramètres & Outils avancés")

# =========================================================
# 🧹 VALIDATION AUTOMATIQUE AU DÉMARRAGE
# =========================================================
st.markdown("### 🧹 Validation automatique de la base")

fixed = validate_and_fix_json()
if fixed:
    st.warning(
        "⚠️ La base JSON contenait des incohérences techniques "
        "(types, dates, champs manquants) et a été automatiquement réparée."
    )
else:
    st.success("✔ Structure JSON valide. Aucune réparation nécessaire.")

# =========================================================
# ONGLET DE NAVIGATION
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "📥 Import Excel → JSON",
    "📤 Export JSON",
    "🩺 Analyse & Historique"
])

# =========================================================
# TAB 1 — DEBUG SECRETS
# =========================================================
with tab1:
    st.subheader("🔐 Visualisation des secrets (sécurisée)")

    try:
        st.json(st.secrets)
    except Exception as e:
        st.error(f"Impossible de lire st.secrets : {e}")

    st.info("⚠️ Les valeurs sensibles sont masquées automatiquement.")

# =========================================================
# TAB 2 — DIAGNOSTIC DROPBOX
# =========================================================
with tab2:
    st.subheader("🧪 Diagnostic Dropbox")

    try:
        dbx = get_dbx()
        st.success("Connexion Dropbox OK ✔")
    except Exception as e:
        dbx = None
        st.error(f"❌ Erreur connexion Dropbox : {e}")

    st.write("### 📄 Fichier JSON utilisé")
    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            content = res.content.decode("utf-8")
            json_content = json.loads(content)

            st.success("Lecture JSON Dropbox OK ✔")
            st.json(json_content)

        except Exception as e:
            st.error(f"❌ Erreur lecture JSON : {e}")

# =========================================================
# TAB 3 — IMPORT EXCEL → JSON
# =========================================================
with tab3:
    st.subheader("📥 Import Excel → JSON (Clients, Visa, Escrow, Compta)")

    st.write("""
    Cet outil lit directement **les fichiers Excel présents dans Dropbox** :
    - `Clients.xlsx` (**obligatoire**)
    - `Visa.xlsx`
    - `Escrow.xlsx`
    - `ComptaCli.xlsx`

    ⚠️ **Si `Clients.xlsx` est vide ou introuvable, l'import est refusé**
    pour éviter d’écraser la base.
    """)

    if st.button("📥 Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()

            st.markdown("### ✅ Résumé de l'import")
            st.write(f"- Clients importés : {len(new_db.get('clients', []))}")
            st.write(f"- Visa importés : {len(new_db.get('visa', []))}")
            st.write(f"- Escrow importés : {len(new_db.get('escrow', []))}")
            st.write(f"- Compta importés : {len(new_db.get('compta', []))}")

            if len(new_db.get("clients", [])) == 0:
                st.error(
                    "❌ Import refusé : 0 dossier importé. "
                    "Le JSON existant n’a PAS été écrasé."
                )
                st.stop()

            save_database(new_db)
            st.success("✔ Import Excel terminé — JSON mis à jour.")

            with st.expander("📂 Voir le JSON importé"):
                st.json(new_db)

        except Exception as e:
            st.error(f"❌ Erreur import : {e}")

# =========================================================
# TAB 4 — EXPORT JSON
# =========================================================
with tab4:
    st.subheader("📤 Export complet du JSON")

    try:
        db = load_database()

        export_name = f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        st.download_button(
            label="⬇️ Télécharger database.json",
            data=json.dumps(db, indent=2),
            file_name=export_name,
            mime="application/json"
        )

        st.success("✔ Export prêt")

    except Exception as e:
        st.error(f"Erreur export JSON : {e}")

# =========================================================
# TAB 5 — ANALYSE & HISTORIQUE
# =========================================================
with tab5:
    st.subheader("🩺 Analyse des incohérences métier")

    try:
        db = load_database()
        alerts = analyse_incoherences(db)

        if alerts:
            st.error(f"⚠️ {len(alerts)} incohérences détectées :")
            for a in alerts:
                st.markdown(f"- {a}")
        else:
            st.success("✔ Aucune incohérence détectée.")

    except Exception as e:
        st.error(f"Erreur analyse JSON : {e}")

    st.markdown("---")
    st.subheader("🕓 Historique des modifications")

    history = db.get("history", [])

    if not history:
        st.info("Aucun historique enregistré pour le moment.")
    else:
        df_hist = pd.DataFrame(history)
        st.dataframe(df_hist, use_container_width=True)

        st.download_button(
            label="⬇️ Exporter l'historique",
            data=json.dumps(history, indent=2),
            file_name="history.json",
            mime="application/json"
        )
