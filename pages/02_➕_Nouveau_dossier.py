import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# Charger base
db = load_database()
clients = db.get("clients", [])
visa_table = pd.DataFrame(db.get("visa", []))

# Sécuriser colonnes Visa
if not visa_table.empty:
    visa_table = visa_table.rename(columns={
        "Categories": "Categories",
        "Sous-categories": "Sous-categories",
        "Visa": "Visa"
    })

# ------------------------------------------------
# GÉNÉRER UN NUMÉRO DE DOSSIER
# ------------------------------------------------
def nouveau_numero():
    nums = []
    for c in clients:
        n = c.get("Dossier N")
        try:
            if isinstance(n, str) and n.isdigit():
                nums.append(int(n))
            elif isinstance(n, (int, float)):
                nums.append(int(n))
        except:
            pass
    return str(max(nums) + 1 if nums else 10000)

num_dossier = nouveau_numero()

# ------------------------------------------------
# FORMULAIRE
# ------------------------------------------------
st.subheader("Informations du dossier")

col1, col2 = st.columns(2)

with col1:
    dossier_num = st.text_input("Dossier N", num_dossier)
    nom = st.text_input("Nom du client").strip()

    # FILTRE INTELLIGENT — Catégories
    cat_list = [""] + sorted(visa_table["Categories"].dropna().unique().tolist())
    categorie = st.selectbox("Catégorie", cat_list)

    # FILTRE — Sous-catégories dépendantes
    if categorie:
        scat_list = [""] + sorted(
            visa_table[visa_table["Categories"] == categorie]["Sous-categories"].dropna().unique()
        )
    else:
        scat_list = [""]

    sous_categorie = st.selectbox("Sous-catégorie", scat_list)

with col2:
    # FILTRE — Visa dépendant
    if sous_categorie:
        visa_list = [""] + sorted(
            visa_table[visa_table["Sous-categories"] == sous_categorie]["Visa"].dropna().unique()
        )
    elif categorie:
        visa_list = [""] + sorted(
            visa_table[visa_table["Categories"] == categorie]["Visa"].dropna().unique()
        )
    else:
        visa_list = [""]

    visa = st.selectbox("Visa", visa_list)

    date = st.date_input("Date du dossier")
    commentaires = st.text_area("Commentaires")

st.markdown("---")

# ------------------------------------------------
# VALIDATION
# ------------------------------------------------
if st.button("Créer le dossier", type="primary"):
    if not nom:
        st.error("Le nom du client est obligatoire.")
        st.stop()

    new_entry = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Catégories": categorie,
        "Sous-catégories": sous_categorie,
        "Visa": visa,
        "Date": str(date),
        "Commentaires": commentaires,
        "Montant honoraires (US $)": 0,
        "Autres frais (US $)": 0,
        "Acompte 1": 0,
        "Acompte 2": 0,
        "Acompte 3": 0,
        "Acompte 4": 0
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"Dossier #{dossier_num} créé ✔")
    st.balloons()
