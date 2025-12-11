import streamlit as st
from backend.dropbox_utils import load_database, save_database

st.title("🔧 Migration des statuts (fix JSON)")

db = load_database()
clients = db.get("clients", [])
changed = False

for c in clients:
    # 1) Si l'ancien champ existe → on le copie vers le nouveau
    if "Dossier_envoye" in c:
        c["Dossier envoye"] = bool(c.get("Dossier_envoye"))
        del c["Dossier_envoye"]
        changed = True

    # 2) Alias possibles
    if "Dossier envoyé" in c:
        c["Dossier envoye"] = bool(c.get("Dossier envoyé"))
        del c["Dossier envoyé"]
        changed = True

db["clients"] = clients

if changed:
    save_database(db)
    st.success("✔ Migration terminée. Le JSON a été corrigé.")
else:
    st.info("Aucune migration nécessaire.")