import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# Charger base
db = load_database()
clients = db.get("clients", [])
visa_table = pd.DataFrame(db.get("visa", []))

# Normalisation Visa
visa_table = visa_table.rename(columns={
    "Categories": "Categories",
    "Sous-categories": "Sous-categories",
    "Visa": "Visa"
})

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

# Sélection dossier
liste = [f"{c['Dossier N']} – {c['Nom']}" for c in clients]
selection = st.selectbox("Choisir un dossier", liste)

index = liste.index(selection)
dossier = clients[index]

# ------------------------------------------------
# FORMULAIRE
# ------------------------------------------------
st.subheader("Modifier les informations")

col1, col2 = st.columns(2)

with col1:
    num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

    # Catégorie
    cat_list = [""] + sorted(visa_table["Categories"].dropna().unique().tolist())
    categorie = st.selectbox("Catégorie", cat_list, index=cat_list.index(dossier.get("Catégories", "")))

    if categorie:
        scat_list = [""] + sorted(
            visa_table[visa_table["Categories"] == categorie]["Sous-categories"].unique()
        )
    else:
        scat_list = [""]

    sous_categorie = st.selectbox(
        "Sous-catégorie",
        scat_list,
        index=scat_list.index(dossier.get("Sous-catégories", "")) if dossier.get("Sous-catégories", "") in scat_list else 0
    )

with col2:
    # Visa dépendant
    if sous_categorie:
        visa_list = [""] + sorted(
            visa_table[visa_table["Sous-categories"] == sous_categorie]["Visa"].unique()
        )
    else:
        visa_list = [""]

    visa_valeur = dossier.get("Visa", "")
    visa = st.selectbox("Visa", visa_list, index=visa_list.index(visa_valeur) if visa_valeur in visa_list else 0)

    date = st.date_input("Date", value=pd.to_datetime(dossier.get("Date")))
    commentaires = st.text_area("Commentaires", value=dossier.get("Commentaires", ""))

# ------------------------------------------------
# MONTANTS
# ------------------------------------------------
st.subheader("💰 Montants")

colA, colB, colC = st.columns(3)

with colA:
    honoraires = st.number_input("Honoraires (US $)", value=float(dossier.get("Montant honoraires (US $)", 0)))
    autres = st.number_input("Autres frais (US $)", value=float(dossier.get("Autres frais (US $)", 0)))

with colB:
    a1 = st.number_input("Acompte 1", value=float(dossier.get("Acompte 1", 0)))
    a2 = st.number_input("Acompte 2", value=float(dossier.get("Acompte 2", 0)))

with colC:
    a3 = st.number_input("Acompte 3", value=float(dossier.get("Acompte 3", 0)))
    a4 = st.number_input("Acompte 4", value=float(dossier.get("Acompte 4", 0)))

st.markdown("---")

# ------------------------------------------------
# ENREGISTREMENT
# ------------------------------------------------
if st.button("💾 Enregistrer", type="primary"):
    clients[index] = {
        "Dossier N": num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Date": str(date),
        "Commentaires": commentaires,
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4
    }

    db["clients"] = clients
    save_database(db)

    st.success("Dossier mis à jour ✔")
    st.balloons()

# ------------------------------------------------
# SUPPRESSION
# ------------------------------------------------
st.markdown("---")
if st.button("🗑️ Supprimer ce dossier"):
    del clients[index]
    db["clients"] = clients
    save_database(db)
    st.success("Dossier supprimé ✔")
    st.stop()
