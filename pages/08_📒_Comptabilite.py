import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("📒 Comptabilité – Gestion des mouvements financiers")

# ---------------------------------------------------------
# Fonction sécurisée de conversion montant
# ---------------------------------------------------------
def safe_float(x, default=0.0):
    """
    Convertit proprement n'importe quelle valeur Excel/JSON en float.
    Évite les crashs sur "", None, "N/A", "—", etc.
    """
    try:
        if x is None:
            return default
        if isinstance(x, (int, float)):
            return float(x)

        x = str(x).replace(",", ".").strip()

        if x == "":
            return default

        return float(x)
    except:
        return default

# ---------------------------------------------------------
# Charger base Dropbox
# ---------------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

compta_entries = db.get("compta", [])

# ---------------------------------------------------------
# Tableau principal
# ---------------------------------------------------------
st.subheader("📌 Liste des opérations comptables")

if compta_entries:
    df = pd.DataFrame(compta_entries)
else:
    df = pd.DataFrame(columns=[
        "Date", "Type", "Dossier N", "Nom", 
        "Montant", "Mode Paiement", "Catégorie", "Commentaires"
    ])

st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")

# ---------------------------------------------------------
# AJOUTER une opération comptable
# ---------------------------------------------------------
st.subheader("➕ Ajouter une opération")

col1, col2 = st.columns(2)

with col1:
    date_op = st.date_input("Date de l'opération")
    type_op = st.selectbox("Type d'opération", ["Encaissement", "Décaissement"])
    dossier_num = st.text_input("Dossier N")
    nom = st.text_input("Nom du client")

with col2:
    montant = st.number_input("Montant (USD)", min_value=0.0, format="%.2f")
    mode = st.selectbox("Mode de paiement", ["Virement", "Carte", "Espèces", "Chèque", "Autre"])
    categorie = st.text_input("Catégorie")

comment = st.text_area("Commentaires")

if st.button("Ajouter l'opération", type="primary"):
    new_entry = {
        "Date": str(date_op),
        "Type": type_op,
        "Dossier N": dossier_num,
        "Nom": nom,
        "Montant": montant,
        "Mode Paiement": mode,
        "Catégorie": categorie,
        "Commentaires": comment
    }
    compta_entries.append(new_entry)
    db["compta"] = compta_entries
    save_database(db)
    st.success("Opération ajoutée ✔")
    st.balloons()

st.markdown("---")

# ---------------------------------------------------------
# MODIFIER une opération existante
# ---------------------------------------------------------
st.subheader("✏️ Modifier une opération")

if not compta_entries:
    st.info("Aucune opération à modifier.")
    st.stop()

liste = [
    f"{c.get('Date', '')} – {c.get('Nom', '')} – ${c.get('Montant', '')}"
    for c in compta_entries
]

selection = st.selectbox("Sélectionner une opération", liste)

index = liste.index(selection)
entry = compta_entries[index]

colA, colB = st.columns(2)

with colA:
    mod_date = st.text_input("Date", value=str(entry.get("Date", "")))
    mod_type = st.selectbox(
        "Type",
        ["Encaissement", "Décaissement"],
        index=["Encaissement", "Décaissement"].index(entry.get("Type", "Encaissement"))
    )
    mod_dossier = st.text_input("Dossier N", value=str(entry.get("Dossier N", "")))
    mod_nom = st.text_input("Nom", value=str(entry.get("Nom", "")))

with colB:
    mod_montant = st.number_input(
        "Montant (USD)",
        value=safe_float(entry.get("Montant", 0)),
        format="%.2f"
    )
    mod_mode = st.selectbox(
        "Mode Paiement",
        ["Virement", "Carte", "Espèces", "Chèque", "Autre"],
        index=0
    )
    mod_categorie = st.text_input("Catégorie", value=str(entry.get("Catégorie", "")))

mod_comment = st.text_area("Commentaires", value=str(entry.get("Commentaires", "")))

if st.button("💾 Enregistrer les modifications"):
    compta_entries[index] = {
        "Date": mod_date,
        "Type": mod_type,
        "Dossier N": mod_dossier,
        "Nom": mod_nom,
        "Montant": mod_montant,
        "Mode Paiement": mod_mode,
        "Catégorie": mod_categorie,
        "Commentaires": mod_comment
    }
    db["compta"] = compta_entries
    save_database(db)
    st.success("Opération mise à jour ✔")

st.markdown("---")

# ---------------------------------------------------------
# SUPPRIMER une opération
# ---------------------------------------------------------
if st.button("🗑️ Supprimer cette opération"):
    del compta_entries[index]
    db["compta"] = compta_entries
    save_database(db)
    st.success("Opération supprimée ✔")
