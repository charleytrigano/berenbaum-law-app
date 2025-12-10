import streamlit as st
from utils.sidebar import render_sidebar
render_sidebar()
import pandas as pd
from backend.dropbox_utils import load_database, save_database




st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

visa_raw = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# FILTRES SIMPLES ET ROBUSTES
# ---------------------------------------------------------

def get_souscats(df, categorie):
    return sorted(
        df[df["Categories"] == categorie]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )

def get_visas(df, souscat):
    return sorted(
        df[df["Sous-categories"] == souscat]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )

# ---------------------------------------------------------
# NUMÉRO DOSSIER
# ---------------------------------------------------------

def nouveau_numero():
    nums = []
    for item in clients:
        try:
            n = int(float(item.get("Dossier N", 0)))
            if n > 0:
                nums.append(n)
        except:
            pass
    return max(nums) + 1 if nums else 13057

new_id = nouveau_numero()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------

st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=str(new_id), disabled=True)
nom = col2.text_input("Nom")
date_dossier = col3.date_input("Date de création")

# ---------------- CATEGORIES & VISA ----------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

# Catégories
cat_list = ["Choisir..."] + sorted(visa_raw["Categories"].dropna().unique().tolist())
categorie = colA.selectbox("Catégorie", cat_list)

# Sous-catégories
if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_raw, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

# Visa
if sous_categorie != "Choisir...":
    visa_list = ["Choisir..."] + get_visas(visa_raw, sous_categorie)
else:
    visa_list = ["Choisir..."]

visa = colC.selectbox("Visa", visa_list)

# ---------------- FINANCES ------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
montant_hon = colF1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
autres_frais = colF2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
colF3.number_input("Total facturé", value=montant_hon + autres_frais, disabled=True)

# ---------------- ACOMPTES ------------------------------
st.subheader("🏦 Paiements")

colA1, colA2, colA3, colA4 = st.columns(4)
a1 = colA1.number_input("Acompte 1", min_value=0.0, step=50.0)
a2 = colA2.number_input("Acompte 2", min_value=0.0, step=50.0)
a3 = colA3.number_input("Acompte 3", min_value=0.0, step=50.0)
a4 = colA4.number_input("Acompte 4", min_value=0.0, step=50.0)

solde = (montant_hon + autres_frais) - (a1 + a2 + a3 + a4)
st.info(f"💵 Solde restant : **${solde:,.2f}**")

mode_paiement = st.selectbox("Mode de paiement", ["", "Chèque", "CB", "Virement", "Venmo"])

escrow = st.checkbox("Mettre en Escrow")

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if nom.strip() == "":
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if categorie == "Choisir..." or sous_categorie == "Choisir..." or visa == "Choisir...":
        st.error("❌ Veuillez sélectionner Catégorie, Sous-catégorie et Visa.")
        st.stop()

    new_entry = {
        "Dossier N": new_id,
        "Nom": nom,
        "Date": str(date_dossier),

        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "mode de paiement": mode_paiement,

        # ESCROW EN 3 ÉTATS
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        # STATUTS
        "Dossier envoye": 0,
        "Dossier accepte": 0,
        "Dossier refuse": 0,
        "Dossier Annule": 0,
        "RFE": 0,

        "Date envoi": "",
        "Date acceptation": "",
        "Date refus": "",
        "Date annulation": "",
        "Date reclamation": "",
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier **{new_id}** enregistré avec succès !")
    st.balloons()
