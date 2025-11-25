import streamlit as st
import pandas as pd
from backend.google_sheets import (
    load_compta,
    add_compta_entry,
    update_compta_row,
    delete_compta_row
)

st.title("📒 Comptabilité – Suivi Financier")

# Charger les données comptables
df = load_compta()

if df.empty:
    st.warning("Aucune donnée trouvée dans l'onglet ComptaCli.")
    st.stop()

st.subheader("📄 Tableau des opérations")
st.dataframe(df, use_container_width=True)

columns = df.columns.tolist()

st.markdown("---")

# --------------------------------------------------
# AJOUT D’UNE OPÉRATION
# --------------------------------------------------
st.subheader("➕ Ajouter une opération")

new_op = {}

with st.form("add_compta_form"):
    colA, colB = st.columns(2)
    for i, col in enumerate(columns):
        if "Date" in col:
            new_op[col] = (colA if i % 2 == 0 else colB).date_input(col)
        elif "Montant" in col:
            new_op[col] = (colA if i % 2 == 0 else colB).number_input(col, value=0.0)
        else:
            new_op[col] = (colA if i % 2 == 0 else colB).text_input(col)
    submit_new = st.form_submit_button("Ajouter")

if submit_new:
    row = [new_op[c] for c in columns]
    add_compta_entry(row)
    st.success("Opération ajoutée ✔")
    st.info("Actualisez la page pour voir la mise à jour.")

st.markdown("---")

# --------------------------------------------------
# MODIFICATION D’UNE OPÉRATION
# --------------------------------------------------
st.subheader("✏️ Modifier une opération")

op_select = st.selectbox("Choisir une opération :", df.index.tolist())

selected_row = df.loc[op_select].to_dict()
updated_op = {}

for col in columns:
    val = selected_row[col]
    if "Date" in col:
        val = pd.to_datetime(val).date() if val else None
        updated_op[col] = st.date_input(col, value=val)
    elif "Montant" in col:
        updated_op[col] = st.number_input(col, value=float(val) if val else 0 else 0.0)
    else:
        updated_op[col] = st.text_input(col, value=val)

if st.button("💾 Enregistrer les modifications"):
    row_vals = [updated_op[c] for c in columns]
    update_compta_row(op_select, row_vals)
    st.success("Opération mise à jour ✔")

st.markdown("---")

# --------------------------------------------------
# SUPPRIMER OPÉRATION
# --------------------------------------------------
st.subheader("❌ Supprimer une opération")

op_delete = st.selectbox("Opération à supprimer :", df.index.tolist(), key="delete")
if st.button("Supprimer définitivement"):
    delete_compta_row(op_delete)
    st.error("Opération supprimée ❗")

st.markdown("---")
st.subheader("💵 Solde par dossier")

if "Dossier N" in df.columns and "Montant" in df.columns:
    solde = df.groupby("Dossier N")["Montant"].sum()
    st.write(solde)

st.subheader("💰 Solde global")

if "Montant" in df.columns:
    st.metric("Solde total", f"{df['Montant'].sum():,.2f} USD")

