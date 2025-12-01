import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.title("➕ Nouveau dossier")

# ----------------------------
# Charger la base + Visa.xlsx
# ----------------------------
db = load_database()
clients = db.get("clients", [])
visa_ref = db.get("visa", [])

df_visa = pd.DataFrame(visa_ref)

# ----------------------------
# DEBUG — Colonnes Visa.xlsx
# ----------------------------
st.write("Colonnes trouvées dans Visa.xlsx :", df_visa.columns.tolist())

# ----------------------------
# Normalisation automatique
# ----------------------------
rename_map = {}

for col in df_visa.columns:
    c = col.lower().replace("-", "").replace("_", "").strip()

    if "categorie" in c and "sous" not in c:
        rename_map[col] = "Categories"
    elif "sous" in c:
        rename_map[col] = "Sous-categories"
    elif "visa" in c:
        rename_map[col] = "Visa"

df_visa = df_visa.rename(columns=rename_map)

required_cols = ["Categories", "Sous-categories", "Visa"]

for col in required_cols:
    if col not in df_visa.columns:
        st.error(f"❌ Colonne manquante dans Visa.xlsx : {col}")
        st.stop()

# ----------------------------
# Fonction : Dossier N
# ----------------------------
def nouveau_numero():
    nums = []
    for c in clients:
        n = c.get("Dossier N")
        try:
            n = int(str(n).split("-")[0])
            nums.append(n)
        except:
            pass
    return str(max(nums) + 1 if nums else 1)

# ----------------------------
# FORMULAIRE
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", nouveau_numero())
    nom = st.text_input("Nom")

    cat_list = sorted(df_visa["Categories"].dropna().unique())
    categorie = st.selectbox("Catégorie", cat_list)

    souscat_list = sorted(
        df_visa[df_visa["Categories"] == categorie]["Sous-categories"].dropna().unique()
    )
    sous_categorie = st.selectbox("Sous-catégorie", souscat_list)

with col2:
    visa_list = df_visa[
        (df_visa["Categories"] == categorie) &
        (df_visa["Sous-categories"] == sous_categorie)
    ]["Visa"].dropna().unique().tolist()

    visa = st.selectbox("Visa", visa_list)

    montant_hon = st.number_input("Montant honoraires (US $)", min_value=0.0)
    autres_frais = st.number_input("Autres frais (US $)", min_value=0.0)

commentaires = st.text_area("Commentaires")

# ----------------------------
# SAUVEGARDE
# ----------------------------
if st.button("Créer le dossier", type="primary"):
    new_client = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,
        "Commentaires": commentaires
    }

    clients.append(new_client)
    db["clients"] = clients
    save_database(db)

    st.success("Dossier créé ✔")
    st.balloons()
