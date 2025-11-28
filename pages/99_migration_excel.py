import streamlit as st
from backend.migrate_excel_to_json import migrate_all_sheets_to_json

st.title("🛠️ Migration Excel → Base JSON globale")

st.write("""
Cette opération convertit **toutes les feuilles Excel** en une base JSON
complète utilisable par toute l'application.
""")

if st.button("Lancer la migration maintenant"):
    data = migrate_all_sheets_to_json()
    st.success("Migration terminée ! Voici la structure générée :")
    st.json(data)

