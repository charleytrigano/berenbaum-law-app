import streamlit as st
import pandas as pd
from backend.google_sheets import (
    load_visa,
    add_visa_entry,
    update_visa_row,
    delete_visa_row
)

st.title("🛂 Gestion des Visas")

# Chargement
df = load_visa()

if df.empty:
    st.warning("Aucune donnée trouvée dans l’onglet Visa.")
else:
    st.subheader("📄 Données actuelles")
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# AJOUTER UNE ENTRÉE VISA
# --------------------------------------------------
st.subheader("➕ Ajouter un suivi Visa")

if not df.empty:
    columns = df.columns.tolist()
else:
    st.error("Impossible de déterminer les colonnes — aucun enregistrement existant.")
    st.stop()

new_entry = {}

with st.form("visa_add_form"):
    colA, colB = st.columns(2)

    for i, col in enumerate(columns):
        if "Date" in col:
            new_entry[col] = (colA if i % 2 == 0 else colB).date_input(col)
        elif "Montant" in col:
            new_entry[col] = (colA if i % 2 == 0 else colB).number_input(col, value=0.0)
        else:
            new_entry[col] = (colA if i % 2 == 0 else colB).text_input(col)

    add_submit = st.form_submit_button("Ajouter")

if add_submit:
    row = [new_entry[c] for c in columns]
    add_visa_entry(row)
    st.success("entrée Visa ajoutée ✔")
    st.info("Actualisez la page pour voir les nouvelles données.")


# --------------------------------------------------
# MODIFIER UNE ENTRÉE VISA
# --------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un suivi Visa existant")

if not df.empty:
    dossier_select = st.selectbox("Choisir un dossier (Dossier N) :", df["Dossier N"].tolist())

    row_index = df.index[df["Dossier N"] == dossier_select][0]
    row_data = df.loc[row_index].to_dict()

    updated = {}

    st.write("Valeurs actuelles :", row_data)

    for col in columns:
        val = row_data[col]
        if "Date" in col:
            val = pd.to_datetime(val).date() if val else None
            updated[col] = st.date_input(f"{col}", value=val)
        elif "Montant" in col:
            updated[col] = st.number_input(col, value=float(val) if val else 0.0)
        else:
            updated[col] = st.text_input(col, value=val)

    if st.button("💾 Enregistrer les modifications"):
        row_vals = [updated[c] for c in columns]
        update_visa_row(row_index, row_vals)
        st.success("Données Visa mises à jour ✔")


# --------------------------------------------------
# SUPPRIMER UNE ENTRÉE VISA
# --------------------------------------------------
st.markdown("---")
st.subheader("❌ Supprimer une entrée Visa")

if not df.empty:
    dossier_delete = st.selectbox("Sélectionner une entrée à supprimer :", df["Dossier N"].tolist())

    if st.button("Supprimer définitivement"):
        idx = df.index[df["Dossier N"] == dossier_delete][0]
        delete_visa_row(idx)
        st.error("Entrée Visa supprimée ❗")
