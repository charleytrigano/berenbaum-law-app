import streamlit as st
import pandas as pd
import json
from datetime import datetime

from utils.sidebar import render_sidebar
from backend.dropbox_utils import get_dbx, load_database, save_database
from backend.migrate_excel_to_json import convert_all_excels_to_json
from backend.json_validator import validate_and_fix_json, analyse_incoherences

import os
st.write("CONTENU DU DOSSIER RACINE :", os.listdir("."))
st.write("CONTENU DU DOSSIER backend :", os.listdir("backend"))


# ---------------------------------------------------------
# CONFIG PAGE
# ---------------------------------------------------------
st.set_page_config(page_title="⚙️ Paramètres", page_icon="⚙️", layout="wide")
render_sidebar()
st.title("⚙️ Paramètres & Outils avancés")

# =========================================================
# 🧹 VALIDATION + ALERTES AUTOMATIQUES
# =========================================================
st.markdown("### 🧹 Validation & alertes automatiques")

fixed = validate_and_fix_json()
if fixed:
    st.warning(
        "⚠️ La base JSON contenait des incohérences techniques "
        "(types, dates, champs manquants) et a été automatiquement réparée."
    )
else:
    st.success("✔ Structure JSON valide (aucune réparation structurelle nécessaire).")

# Analyse métier des incohérences
alerts = analyse_incoherences()

if alerts:
    st.error(f"🚨 {len(alerts)} incohérences métier détectées dans les dossiers.")
    with st.expander("Voir le détail des incohérences détectées"):
        for msg in alerts:
            st.markdown(f"- {msg}")
else:
    st.info("✅ Aucune incohérence métier détectée sur les dossiers (statuts / escrow / acomptes).")

st.markdown("---")

# =========================================================
# ONGLET DE NAVIGATION
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔐 Debug Secrets",
    "🧪 Diagnostic Dropbox",
    "🧹 Nettoyage avancé (Deep Clean)",
    "📥 Import Excel → JSON",
    "🔄 Synchronisation Dropbox",
    "🕓 Historique & Alertes"
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

    st.info("⚠️ Les valeurs critiques sont masquées automatiquement pour la sécurité.")

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

    st.write("### 📄 Fichier JSON configuré")
    st.code(st.secrets["paths"]["DROPBOX_JSON"])

    if dbx:
        try:
            meta, res = dbx.files_download(st.secrets["paths"]["DROPBOX_JSON"])
            content = res.content.decode("utf-8")
            json_content = json.loads(content)
            st.json(json_content)
            st.success("Lecture JSON Dropbox OK ✔")

            # Export complet du JSON
            st.markdown("#### 📤 Export complet du JSON")
            st.download_button(
                label="⬇️ Télécharger database.json complet",
                data=json.dumps(json_content, indent=2),
                file_name="database.json",
                mime="application/json",
            )

        except Exception as e:
            st.error(f"❌ Erreur lecture JSON : {e}")

# =========================================================
# TAB 3 — NETTOYAGE AVANCÉ (DEEP CLEAN)
# =========================================================
with tab3:
    st.subheader("🧹 Nettoyage avancé de la base de données")

    st.write("""
    Le **deep clean** exécute les opérations suivantes :
    - Correction des dates invalides  
    - Normalisation des booléens  
    - Correction des montants mal formatés  
    - Ajout des champs manquants (Commentaire, etc.)  
    - Suppression des doublons de dossiers  
    - Harmonisation des statuts  
    - Reformatage propre du JSON
    """)

    if st.button("🧹 Lancer le nettoyage avancé", type="primary"):
        db = load_database()

        def to_bool(v):
            if isinstance(v, bool):
                return v
            if str(v).lower() in ["true", "1", "yes", "oui"]:
                return True
            return False

        clients = db.get("clients", [])
        cleaned_clients = []

        for row in clients:
            if not isinstance(row, dict):
                continue

            r = row.copy()

            # Dates
            for k in list(r.keys()):
                if "Date" in k:
                    try:
                        d = pd.to_datetime(r[k], errors="coerce")
                        r[k] = None if pd.isna(d) else str(d.date())
                    except Exception:
                        r[k] = None

            # Booléens
            for key in [
                "Escrow",
                "Escrow_a_reclamer",
                "Escrow_reclame",
                "Dossier envoye",
                "Dossier accepte",
                "Dossier refuse",
                "Dossier Annule",
                "RFE",
            ]:
                r[key] = to_bool(r.get(key, False))

            # Montants
            for key in ["Montant honoraires (US $)", "Autres frais (US $)"]:
                try:
                    r[key] = float(r.get(key, 0) or 0)
                except Exception:
                    r[key] = 0.0

            for i in range(1, 5):
                k = f"Acompte {i}"
                try:
                    r[k] = float(r.get(k, 0) or 0)
                except Exception:
                    r[k] = 0.0

            # Champs texte
            for key in ["Categories", "Sous-categories", "Visa", "Commentaire"]:
                if key not in r or r[key] is None:
                    r[key] = ""

            cleaned_clients.append(r)

        # Suppression doublons Dossier N
        seen = set()
        unique_clients = []
        for r in cleaned_clients:
            num = r.get("Dossier N")
            if num in seen:
                continue
            seen.add(num)
            unique_clients.append(r)

        db["clients"] = unique_clients
        save_database(db)

        st.success("✔ Nettoyage avancé terminé. Base mise à jour.")
        st.json(db)

# =========================================================
# TAB 4 — IMPORT EXCEL → JSON
# =========================================================
with tab4:
    st.subheader("📥 Importer les fichiers Excel et recréer le JSON")

    st.write("""
    Cet outil lit :  
    - `Clients.xlsx`  
    - `Visa.xlsx`  
    - `Escrow.xlsx`  
    - `ComptaCli.xlsx`  
    puis reconstruit entièrement `database.json`.
    """)

    if st.button("📥 Importer maintenant", type="primary"):
        try:
            new_db = convert_all_excels_to_json()
            save_database(new_db)
            st.success("✔ Import Excel terminé — JSON mis à jour.")
            st.json(new_db)
        except Exception as e:
            st.error(f"❌ Erreur import : {e}")

# =========================================================
# TAB 5 — SYNCHRONISATION
# =========================================================
with tab5:
    st.subheader("🩺 Analyse des incohérences JSON")

    db = load_database()
    alerts = analyse_incoherences(db)

    if alerts:
        st.error("⚠️ Incohérences détectées dans la base :")
        for a in alerts:
            st.markdown(f"- {a}")
    else:
        st.success("✔ Aucune incohérence détectée dans la base JSON.")


# =========================================================
# TAB 6 — HISTORIQUE & ALERTES
# =========================================================
with tab6:
    st.subheader("🕓 Historique des modifications")

    db = load_database()
    history = db.get("history", [])

    if not history:
        st.info("Aucun historique trouvé pour le moment.")
    else:
        dfh = pd.DataFrame(history)
        st.dataframe(dfh, use_container_width=True)

        if st.button("📤 Exporter l'historique en JSON"):
            st.download_button(
                label="Télécharger history.json",
                data=json.dumps(history, indent=2),
                file_name="history.json",
                mime="application/json",
            )

    st.markdown("---")
    st.subheader("🚨 Rappel des incohérences détectées")

    alerts = analyse_incoherences()
    if alerts:
        st.error(f"{len(alerts)} incohérences actuellement détectées :")
        for msg in alerts:
            st.markdown(f"- {msg}")
    else:
        st.success("Aucune incohérence métier détectée pour l’instant.")
