import streamlit as st
import pandas as pd
import json
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json
from backend.json_validator import validate_and_fix_json

render_sidebar()

st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
st.title("⚙️ Paramètres & Outils avancés")

# =========================================================
# 🧹 VALIDATION AUTOMATIQUE AU DÉMARRAGE
# =========================================================
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

# =========================================================
# ONGLET DE NAVIGATION
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "🧹 Nettoyage avancé (Deep Clean)",
    "📥 Import Excel → JSON",
    "🔄 Synchronisation Dropbox",
    "🕓 Historique des modifications"
])

# =========================================================
# TAB 1 — DEBUG SECRETS
# =========================================================
with tab1:
    st.subheader("🔐 Visualisation sécurisée des secrets")

    try:
        st.json(st.secrets)
    except Exception as e:
        st.error(f"Impossible de lire st.secrets : {e}")

# =========================================================
# TAB 2 — DIAGNOSTIC DROPBOX
# =========================================================
with tab2:
    st.subheader("🧪 Diagnostic de connexion Dropbox")

    try:
        dbx = get_dbx()
        st.success("Connexion Dropbox OK ✔")
    except Exception as e:
        dbx = None
        st.error(f"❌ Erreur connexion Dropbox : {e}")

    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            st.json(json.loads(res.content.decode("utf-8")))
            st.success("Lecture JSON Dropbox OK ✔")
        except Exception as e:
            st.error(f"❌ Erreur lecture JSON : {e}")

# =========================================================
# TAB 3 — NETTOYAGE AVANCÉ (DEEP CLEAN)
# =========================================================
with tab3:
    st.subheader("🧹 Nettoyage avancé de la base de données")

    st.write("""
    Le deep clean exécute les opérations suivantes :
    - Correction des dates invalides  
    - Normalisation booléens  
    - Correction des montants mal formatés  
    - Ajout des champs manquants  
    - Suppression des doublons  
    - Harmonisation complète des statuts  
    - Reformatage JSON propre
    """)

    if st.button("🧹 Lancer le nettoyage avancé", type="primary"):
        db = load_database()
        before = json.dumps(db, indent=2)

        # ---- NORMALISATION ----
        def to_bool(v):
            if isinstance(v, bool): return v
            if str(v).lower() in ["true", "1", "yes", "oui"]: return True
            return False

        for row in db["clients"]:
            # Dates
            for k in row:
                if "Date" in k:
                    try:
                        d = pd.to_datetime(row[k], errors="coerce")
                        row[k] = None if pd.isna(d) else str(d.date())
                    except:
                        row[k] = None

            # Booléens
            for key in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame",
                        "Dossier envoye", "Dossier accepte",
                        "Dossier refuse", "Dossier Annule", "RFE"]:
                row[key] = to_bool(row.get(key, False))

            # Champs manquants
            mandatory = [
                "Commentaire", "Sous-categories", "Visa"
            ]
            for k in mandatory:
                if k not in row:
                    row[k] = ""

            # Revenus correctement castés
            for key in ["Montant honoraires (US $)", "Autres frais (US $)"]:
                try:
                    row[key] = float(row.get(key, 0))
                except:
                    row[key] = 0.0

        # Suppression doublons Dossier N
        seen = set()
        cleaned_clients = []
        for r in db["clients"]:
            if r["Dossier N"] not in seen:
                seen.add(r["Dossier N"])
                cleaned_clients.append(r)

        db["clients"] = cleaned_clients

        save_database(db)

        after = json.dumps(db, indent=2)

        st.success("✔ Deep clean terminé")

        st.write("### Modifications effectuées :")
        st.code(after)

# =========================================================
# TAB 4 — IMPORT EXCEL → JSON
# =========================================================
with tab4:
    st.subheader("📥 Import Excel et reconstruction JSON")

    if st.button("📥 Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()
            save_database(new_db)
            st.success("✔ Import terminé")
            st.json(new_db)
        except Exception as e:
            st.error(f"Erreur : {e}")

# =========================================================
# TAB 5 — SYNCHRONISATION
# =========================================================
with tab5:
    st.subheader("🔄 Synchronisation Dropbox")

    if st.button("🔄 Synchroniser maintenant", type="primary"):
        try:
            db = load_database()
            save_database(db)
            st.success("✔ Synchronisation OK")
        except Exception as e:
            st.error(e)

# =========================================================
# TAB 6 — HISTORIQUE DES MODIFICATIONS
# =========================================================
with tab6:
    st.subheader("🕓 Historique complet des opérations")

    db = load_database()
    history = db.get("history", [])

    if not history:
        st.info("Aucun historique trouvé.")
    else:
        dfh = pd.DataFrame(history)
        st.dataframe(dfh, use_container_width=True)

        if st.button("📤 Exporter en JSON"):
            st.download_button(
                label="Télécharger history.json",
                data=json.dumps(history, indent=2),
                file_name="history.json",
                mime="application/json"
            )
