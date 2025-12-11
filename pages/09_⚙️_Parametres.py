import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

from utils.sidebar import render_sidebar
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json
from backend.json_validator import validate_and_fix_json, analyse_incoherences

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
render_sidebar()
st.title("⚙️ Paramètres & Outils avancés")

# ---------------------------------------------------------
# DEBUG VISUEL (facultatif)
# ---------------------------------------------------------
st.write("CONTENU DU DOSSIER RACINE :", os.listdir("."))
st.write("CONTENU DU DOSSIER backend :", os.listdir("backend"))

# ---------------------------------------------------------
# VALIDATION AUTOMATIQUE DU JSON
# ---------------------------------------------------------
st.markdown("### 🧹 Validation & alertes automatiques")

fixed = validate_and_fix_json()
if fixed:
    st.warning("⚠️ La base JSON contenait des incohérences techniques et a été réparée automatiquement.")
else:
    st.success("✔ Structure JSON valide. Aucune réparation nécessaire.")

# ---------------------------------------------------------
# ONGLET PRINCIPAL
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "🧹 Nettoyage avancé",
    "📥 Import Excel",
    "🔄 Synchronisation",
    "🩺 Analyse JSON & Historique"
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
    st.info("Les valeurs sensibles sont masquées automatiquement.")

# ---------------------------------------------------------
# TAB 2 — DIAGNOSTIC DROPBOX
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Diagnostic Dropbox")

    try:
        dbx = get_dbx()
        st.success("Connexion Dropbox OK ✔")
    except Exception as e:
        dbx = None
        st.error(f"Erreur connexion Dropbox : {e}")

    st.write("### 📄 Fichier JSON utilisé")
    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            content = res.content.decode("utf-8")
            json_content = json.loads(content)
            st.json(json_content)

            st.download_button(
                label="⬇️ Télécharger database.json",
                data=json.dumps(json_content, indent=2),
                file_name="database.json",
                mime="application/json",
            )
        except Exception as e:
            st.error(f"Erreur lecture JSON : {e}")

# ---------------------------------------------------------
# TAB 3 — NETTOYAGE AVANCÉ
# ---------------------------------------------------------
with tab3:
    st.subheader("🧹 Nettoyage avancé (Deep Clean)")

    st.write("""
    Corrige :
    - Dates invalides  
    - Montants incorrects  
    - Booléens incohérents  
    - Champs manquants  
    - Doublons de dossiers  
    - Structure JSON  
    """)

    if st.button("Lancer le nettoyage avancé", type="primary"):
        db = load_database()

        def to_bool(v):
            if isinstance(v, bool):
                return v
            return str(v).lower() in ["true", "1", "yes", "oui"]

        clients = db.get("clients", [])
        cleaned = []

        for row in clients:
            if not isinstance(row, dict):
                continue

            r = row.copy()

            # Dates
            for k in r:
                if "Date" in k:
                    dt = pd.to_datetime(r[k], errors="coerce")
                    r[k] = None if pd.isna(dt) else str(dt.date())

            # Booléens
            for k in ["Escrow", "Escrow_a_reclamer", "Escrow_reclame",
                      "Dossier envoye", "Dossier accepte", "Dossier refuse",
                      "Dossier Annule", "RFE"]:
                r[k] = to_bool(r.get(k, False))

            # Montants
            for k in ["Montant honoraires (US $)", "Autres frais (US $)"]:
                try:
                    r[k] = float(r.get(k, 0))
                except:
                    r[k] = 0.0

            for i in range(1, 5):
                try:
                    r[f"Acompte {i}"] = float(r.get(f"Acompte {i}", 0))
                except:
                    r[f"Acompte {i}"] = 0.0

            # Champs texte
            for k in ["Categories", "Sous-categories", "Visa", "Commentaire"]:
                r[k] = r.get(k, "") or ""

            cleaned.append(r)

        # Suppression des doublons
        seen = set()
        unique = []
        for r in cleaned:
            n = r.get("Dossier N")
            if n in seen:
                continue
            seen.add(n)
            unique.append(r)

        db["clients"] = unique
        save_database(db)
        st.success("✔ Nettoyage avancé terminé.")
        st.json(db)

# ---------------------------------------------------------
# TAB 4 — IMPORT EXCEL
# ---------------------------------------------------------
with tab4:
    st.subheader("📥 Import Excel → JSON")

    if st.button("Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()
            save_database(new_db)
            st.success("Import terminé ✔")
            st.json(new_db)
        except Exception as e:
            st.error(f"Erreur import : {e}")

# ---------------------------------------------------------
# TAB 5 — SYNCHRONISATION DROPBOX
# ---------------------------------------------------------
with tab5:
    st.subheader("🔄 Synchronisation Dropbox")

    if st.button("Synchroniser maintenant", type="primary"):
        try:
            db = load_database()
            save_database(db)
            st.success("Synchronisation effectuée ✔")
        except Exception as e:
            st.error(f"Erreur : {e}")

# ---------------------------------------------------------
# TAB 6 — ANALYSE JSON & HISTORIQUE
# ---------------------------------------------------------
with tab6:
    st.subheader("🩺 Analyse JSON")

    try:
        db = load_database()
        alerts = analyse_incoherences(db)
        if alerts:
            st.error("Incohérences détectées :")
            for a in alerts:
                st.markdown(f"- {a}")
        else:
            st.success("Aucune incohérence détectée ✔")
    except Exception as e:
        st.error(f"Erreur analyse JSON : {e}")

    st.markdown("---")
    st.subheader("🕓 Historique des modifications")

    history = db.get("history", [])
    if history:
        dfh = pd.DataFrame(history)
        st.dataframe(dfh, use_container_width=True)
    else:
        st.info("Aucun historique disponible.")
