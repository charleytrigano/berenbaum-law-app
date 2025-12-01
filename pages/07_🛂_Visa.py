import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("🛂 Gestion des visas")

# -------------------------------------------------------
# Chargement base Dropbox
# -------------------------------------------------------
try:
    db = load_database()
except:
    db = {"clients": [], "visa": [], "escrow": [], "compta": []}

# Nettoyage des entrées legacy mal formées
visa_clean = []
for v in db.get("visa", []):
    if isinstance(v, dict) and all(k in v for k in ["Categories", "Sous-categories", "Visa"]):
        visa_clean.append(v)

db["visa"] = visa_clean
visa_list = visa_clean

# -------------------------------------------------------
# Tableau des visas
# -------------------------------------------------------
st.subheader("📋 Référentiel des visas")

if len(visa_list) > 0:
    df = pd.DataFrame(visa_list)
else:
    df = pd.DataFrame(columns=["Categories", "Sous-categories", "Visa"])

st.dataframe(df, use_container_width=True, height=350)

st.markdown("---")

# -------------------------------------------------------
# Ajouter un visa
# -------------------------------------------------------
st.subheader("➕ Ajouter un type de visa")

col1, col2, col3 = st.columns(3)

with col1:
    new_cat = st.text_input("Catégorie")

with col2:
    new_souscat = st.text_input("Sous-catégorie")

with col3:
    new_visa = st.text_input("Visa")


if st.button("Ajouter le visa", type="primary"):
    if new_cat.strip() == "" or new_souscat.strip() == "" or new_visa.strip() == "":
        st.error("Tous les champs doivent être remplis.")
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

