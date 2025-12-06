import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df, get_souscats, get_visas

st.set_page_config(page_title="Nouveau dossier", page_icon="➕", layout="wide")
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# FONCTION : Génération automatique du numéro
# ---------------------------------------------------------
def nouveau_numero():
    """Retourne le prochain numéro disponible en se basant sur le plus grand existant."""
    nums = []

    for item in clients:
        try:
            n = float(item.get("Dossier N", 0))
            if n > 0:
                nums.append(int(n))
        except:
            pass

    # Si aucun numéro existant → on démarre à 13057
    if not nums:
        return 13057

    return max(nums) + 1


# Numéro généré en temps réel
new_id = nouveau_numero()

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)

with col1:
    st.text_input("Dossier N", value=str(new_id), disabled=True)

with col2:
    nom = st.text_input("Nom")

with col3:
    date_dossier = st.date_input("Date de création")

# ---------------- CATEGORIES & VISA ---------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

# Catégories
cat_list = ["Choisir..."] + sorted(visa_table["Categories"].unique())
categorie = colA.selectbox("Catégorie", cat_list)

# Sous-catégories dépendantes
if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_table, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

# Visa dépendant
if sous_categorie != "Choisir...":
    visa_list = ["Choisir..."] + get_visas(visa_table, sous_categorie)
else:
    visa_list = ["Choisir..."]

visa = colC.selectbox("Visa", visa_list)

# ---------------- FINANCES ------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)

with colF1:
    montant_hon = st.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)

with colF2:
    autres_frais = st.number_input("Autres frais (US $)", min_value=0.0, step=10.0)

with colF3:
    total_facture = montant_hon + autres_frais
    st.number_input("Total facturé", value=total_facture, disabled=True)

# ---------------- ACOMPTES ------------------------------
st.subheader("🏦 Paiements")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", min_value=0.0, step=50.0)
a2 = colA2.number_input("Acompte 2", min_value=0.0, step=50.0)
a3 = colA3.number_input("Acompte 3", min_value=0.0, step=50.0)
a4 = colA4.number_input("Acompte 4", min_value=0.0, step=50.0)

solde = total_facture - (a1 + a2 + a3 + a4)
st.info(f"💵 Solde restant : **${solde:,.2f}**")

colP = st.columns(3)[0]
mode_paiement = colP.selectbox("Mode de paiement", ["", "Chèque", "CB", "Virement", "Venmo"])

escrow = st.checkbox("Mettre en Escrow")

# ---------------------------------------------------------
# VALIDATION & ENREGISTREMENT
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
        "Escrow": escrow,
        "Dossier envoye": 0,
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier **{new_id}** enregistré avec succès !")
    st.balloons()
