import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("🛂 Gestion des visas")

# --------------------------------------
# Chargement JSON
# --------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

raw_visa = db.get("visa", [])

# --------------------------------------
# Normalisation automatique des anciennes colonnes
# --------------------------------------
visa_list = []
for v in raw_visa:
    if not isinstance(v, dict):
        continue

    # Correction automatique :
    cat = v.get("Categories") or v.get("Catégories")
    souscat = v.get("Sous-categories") or v.get("Sous-categorie") or v.get("Sous-catégories")
    visa_code = v.get("Visa")

    if cat and souscat and visa_code:
        visa_list.append({
            "Categories": str(cat).strip(),
            "Sous-categories": str(souscat).strip(),
            "Visa": str(visa_code).strip()
        })

# Replace bad data
db["visa"] = visa_list

# --------------------------------------
# Tableau affichage
# --------------------------------------
st.subheader("📋 Référentiel des visas")

df = pd.DataFrame(visa_list)
st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")

# --------------------------------------
# Ajouter un visa
# --------------------------------------
st.subheader("➕ Ajouter un type de visa")

col1, col2, col3 = st.columns(3)

with col1:
    new_cat = st.text_input("Catégorie")

with col2:
    new_souscat = st.text_input("Sous-catégorie")

with col3:
    new_visa = st.text_input("Visa")

if st.button("Ajouter le visa", type="primary"):
    if not new_cat or not new_souscat or not new_visa:
        st.error("Tous les champs doivent être renseignés.")
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
