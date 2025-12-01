import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("🛂 Gestion des visas")

# -----------------------------------------------
# Charger la base Dropbox
# -----------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

visa_list = db.get("visa", [])

# Convertir en DataFrame
if len(visa_list) > 0:
    df = pd.DataFrame(visa_list)
else:
    df = pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])


# -----------------------------------------------
# Tableau Visa
# -----------------------------------------------
st.subheader("📋 Table des visas")
st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")

# -----------------------------------------------
# Formulaire d'ajout
# -----------------------------------------------
st.subheader("➕ Ajouter un visa")

col1, col2, col3 = st.columns(3)

with col1:
    new_cat = st.text_input("Catégorie")

with col2:
    new_souscat = st.text_input("Sous-catégorie")

with col3:
    new_visa = st.text_input("Visa")


if st.button("Ajouter le visa", type="primary"):
    if new_cat.strip() == "" or new_souscat.strip() == "" or new_visa.strip() == "":
        st.error("Tous les champs sont obligatoires.")
    else:
        entry = {
            "Categories": new_cat.strip(),
            "Sous-categories": new_souscat.strip(),
            "Visa": new_visa.strip()
        }
        visa_list.append(entry)
        db["visa"] = visa_list
        save_database(db)
        st.success("Visa ajouté ✔")
        st.experimental_rerun()


st.markdown("---")

# -----------------------------------------------
# Modification & suppression
# -----------------------------------------------
st.subheader("✏️ Modifier / Supprimer un visa")

if len(visa_list) == 0:
    st.info("Aucun visa enregistré.")
    st.stop()

# Liste déroulante
select_label = [
    f"{v['Categories']} → {v['Sous-categories']} → {v['Visa']}"
    for v in visa_list
]
selected = st.selectbox("Sélectionner un visa", select_label)

index = select_label.index(selected)
entry = visa_list[index]

colA, colB, colC = st.columns(3)

with colA:
    mod_cat = st.text_input("Catégorie", value=entry["Categories"])

with colB:
    mod_souscat = st.text_input("Sous-catégorie", value=entry["Sous-categories"])

with colC:
    mod_visa = st.text_input("Visa", value=entry["Visa"])


# Bouton enregistrer
if st.button("💾 Enregistrer les modifications"):
    visa_list[index] = {
        "Categories": mod_cat.strip(),
        "Sous-categories": mod_souscat.strip(),
        "Visa": mod_visa.strip()
    }
    db["visa"] = visa_list
    save_database(db)
    st.success("Modifications enregistrées ✔")
    st.experimental_rerun()

# Bouton supprimer
if st.button("🗑️ Supprimer"):
    del visa_list[index]
    db["visa"] = visa_list
    save_database(db)
    st.success("Visa supprimé ✔")
    st.experimental_rerun()
