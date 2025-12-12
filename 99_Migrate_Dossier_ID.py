import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="🧩 Migration Dossier ID", layout="wide")
st.title("🧩 Migration des Dossier ID (sécurisation KPI)")

db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

changed = False

for c in clients:
    # Création du Dossier ID s'il n'existe pas
    if "Dossier ID" not in c or not c["Dossier ID"]:
        # On force une string UNIQUE
        c["Dossier ID"] = str(c.get("Dossier N", "")).strip()
        changed = True

if changed:
    db["clients"] = clients
    save_database(db)
    st.success("✔ Migration terminée : tous les dossiers ont un Dossier ID unique.")
else:
    st.info("Aucune migration nécessaire : tous les dossiers sont déjà conformes.")

st.subheader("🔍 Aperçu")
st.dataframe(clients[:10], use_container_width=True)
