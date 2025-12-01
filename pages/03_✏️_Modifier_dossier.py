import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("✏️ Modifier un dossier")

# --------------------------------------------------
# Chargement base Dropbox
# --------------------------------------------------
db = load_database()
clients = db.get("clients", [])
df_visa = pd.DataFrame(db.get("visa", []))   # ⚠ issu du fichier Visa.xlsx

if not clients:
    st.warning("Aucun dossier à modifier.")
    st.stop()

# --------------------------------------------------
# Sélection du dossier
# --------------------------------------------------
liste_dossiers = [
    f"{c.get('Dossier N', '')} - {c.get('Nom', '')}"
    for c in clients
]

selection = st.selectbox("Choisir un dossier", liste_dossiers)
index = liste_dossiers.index(selection)
dossier = clients[index]

# --------------------------------------------------
# FORMULAIRE DE MODIFICATION
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
    nom = st.text_input("Nom", value=dossier.get("Nom", ""))

    # ---------------- CATEGORIES ----------------
    categories = [""] + sorted(df_visa["Categories"].dropna().unique().tolist())
    categorie = st.selectbox(
        "Catégorie",
        categories,
        index=categories.index(dossier.get("Catégories", "")) if dossier.get("Catégories") in categories else 0
    )

    # ---------------- SOUS-CATEGORIES filtrées ----------------
    if categorie:
        sous_categories = df_visa[df_visa["Categories"] == categorie]["Sous-categorie"].dropna().unique().tolist()
    else:
        sous_categories = []

    souscat = st.selectbox(
        "Sous-catégorie",
        [""] + sous_categories,
        index=([""] + sous_categories).index(dossier.get("Sous-catégories", "")) 
        if dossier.get("Sous-catégories", "") in ([""] + sous_categories) else 0
    )

with col2:

    # ---------------- VISA filtré ----------------
    if categorie and souscat:
        visas = df_visa[
            (df_visa["Categories"] == categorie) &
            (df_visa["Sous-categorie"] == souscat)
        ]["Visa"].dropna().unique().tolist()
    else:
        visas = []

    visa = st.selectbox(
        "Visa",
        [""] + visas,
        index=([""] + visas).index(dossier.get("Visa", "")) 
        if dossier.get("Visa", "") in ([""] + visas) else 0
    )

    montant = st.number_input(
        "Montant honoraires (US $)",
        value=float(dossier.get("Montant honoraires (US $)", 0)),
        min_value=0.0,
        format="%.2f"
    )

    autres = st.number_input(
        "Autres frais (US $)",
        value=float(dossier.get("Autres frais (US $)", 0)),
        min_value=0.0,
        format="%.2f"
    )

commentaires = st.text_area(
    "Commentaires",
    value=dossier.get("Commentaires", "")
)

# --------------------------------------------------
# BOUTON ENREGISTRER
# --------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    clients[index] = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": souscat,
        "Visa": visa,
        "Montant honoraires (US $)": montant,
        "Autres frais (US $)": autres,
        "Commentaires": commentaires
    }

    db["clients"] = clients
    save_database(db)

    st.success("Modifications enregistrées ✔")
    st.balloons()

# --------------------------------------------------
# SUPPRESSION
# --------------------------------------------------
st.markdown("---")
st.subheader("❌ Supprimer ce dossier")

if st.button("🗑️ Supprimer définitivement le dossier"):
    del clients[index]
    db["clients"] = clients
    save_database(db)
    st.success("Dossier supprimé ✔")
    st.stop()
