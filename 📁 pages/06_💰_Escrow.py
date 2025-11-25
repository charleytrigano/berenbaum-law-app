import streamlit as st
import pandas as pd
from backend.google_sheets import (
    load_escrow,
    add_escrow_entry,
    update_escrow_row,
    delete_escrow_row,
    find_row_index
)

st.title("💰 Gestion de l’Escrow")

df = load_escrow()

if df.empty:
    st.warning("Aucune donnée trouvée dans l’onglet Escrow.")
else:
    st.subheader("📄 Tableau Escrow")
    st.dataframe(df, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# AJOUT D’UN MOUVEMENT ESCROW
# --------------------------------------------------
st.subheader("➕ Ajouter un mouvement")

columns = df.columns.tolist()
new_entry = {}

with st.form("escrow_add"):
    cols = st.columns(2)
    for i, col in enumerate(columns):
        if "Date" in col:
            new_entry[col] = cols[i % 2].date_input(col)
        elif "Montant" in col or "Acompte" in col:
            new_entry[col] = cols[i % 2].number_input(col, value=0.0)
        else:
            new_entry[col] = cols[i % 2].text_input(col)

    add_submit = st.form_submit_button("Ajouter")

if add_submit:
    row = [new_entry[c] for c in columns]
    add_escrow_entry(row)
    st.success("Mouvement ajouté ✔")
    st.info("Actualisez la page pour voir les modifications.")


# --------------------------------------------------
# MODIFICATION D’UN MOUVEMENT
# --------------------------------------------------
st.markdown("---")
st.subheader("✏️ Modifier un mouvement Escrow")

if not df.empty:
    dossier_options = df["Dossier N"].unique().tolist()
    dossier_select = st.selectbox("Choisir un Dossier N :", dossier_options)

    row_index = df.index[df["Dossier N"] == dossier_select][0]
    row_data = df.loc[row_index].to_dict()

    st.write("Valeurs actuelles :", row_data)

    updated_data = {}

    for col in columns:
        if "Date" in col:
            val = pd.to_datetime(row_data[col]).date() if row_data[col] else None
            updated_data[col] = st.date_input(f"{col}", value=val)
        elif "Montant" in col or "Acompte" in col:
            updated_data[col] = st.number_input(col, value=float(row_data[col]) if row_data[col] else 0.0)
        else:
            updated_data[col] = st.text_input(col, value=row_data[col])

    if st.button("💾 Enregistrer les modifications"):
        row = [updated_data[c] for c in columns]
        update_escrow_row(row_index, row)
        st.success("Mouvement mis à jour ✔")


# --------------------------------------------------
# SUPPRESSION D’UN MOUVEMENT
# --------------------------------------------------
st.markdown("---")
st.subheader("❌ Supprimer un mouvement Escrow")

if not df.empty:
    to_delete = st.selectbox("Sélectionner un mouvement à supprimer :", df["Dossier N"].tolist())

    if st.button("Supprimer définitivement"):
        idx = df.index[df["Dossier N"] == to_delete][0]
        delete_escrow_row(idx)
        st.error("Mouvement supprimé ❗")
