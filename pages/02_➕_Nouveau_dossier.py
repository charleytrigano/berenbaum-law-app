import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

if "parent_dossier" in st.session_state:
    mode = "Sous-dossier"
    parent_id = st.session_state["parent_dossier"]
    new_id = prochain_sous_dossier(parent_id)
    del st.session_state["parent_dossier"]

if "parent_dossier" in st.session_state:
    mode = "Sous-dossier"
    parent_id = st.session_state["parent_dossier"]
    new_id = prochain_sous_dossier(parent_id)
    del st.session_state["parent_dossier"]



# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Nouveau dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------
def nouveau_numero():
    nums = []
    for c in clients:
        dn = str(c.get("Dossier N", ""))
        if "-" not in dn:
            try:
                nums.append(int(dn))
            except:
                pass
    return max(nums) + 1 if nums else 13000


def prochain_sous_dossier(parent_id):
    indices = []
    for c in clients:
        dn = str(c.get("Dossier N", ""))
        if dn.startswith(f"{parent_id}-"):
            try:
                indices.append(int(dn.split("-")[1]))
            except:
                pass
    return f"{parent_id}-{max(indices)+1 if indices else 1}"


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
# MODE DE CREATION
# ---------------------------------------------------------
st.markdown("### 🔁 Mode de création")

mode = st.radio(
    "Type de dossier",
    ["Dossier principal", "Sous-dossier"],
    horizontal=True
)

parent_id = None

if mode == "Dossier principal":
    new_id = str(nouveau_numero())
else:
    parents = sorted(
        {str(c["Dossier N"]).split("-")[0] for c in clients}
    )
    parent_id = st.selectbox("Dossier parent", parents)
    new_id = prochain_sous_dossier(parent_id)

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=new_id, disabled=True)
nom = col2.text_input("Nom")
date_dossier = col3.date_input("Date de création")

# ---------------------------------------------------------
# CATEGORIES / VISA
# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

if mode == "Sous-dossier":
    parent = next(c for c in clients if str(c["Dossier N"]) == parent_id)
    categorie = parent["Categories"]
    sous_categorie = parent["Sous-categories"]
    visa = parent["Visa"]

    st.info("Catégorisation héritée du dossier parent")
    st.write(f"**Catégorie :** {categorie}")
    st.write(f"**Sous-catégorie :** {sous_categorie}")
    st.write(f"**Visa :** {visa}")

else:
    colA, colB, colC = st.columns(3)

    cat_list = ["Choisir..."] + sorted(visa_raw["Categories"].dropna().unique())
    categorie = colA.selectbox("Catégorie", cat_list)

    souscats = ["Choisir..."]
    if categorie != "Choisir...":
        souscats += get_souscats(visa_raw, categorie)
    sous_categorie = colB.selectbox("Sous-catégorie", souscats)

    visas = ["Choisir..."]
    if sous_categorie != "Choisir...":
        visas += get_visas(visa_raw, sous_categorie)
    visa = colC.selectbox("Visa", visas)

# ---------------------------------------------------------
# FINANCES
# ---------------------------------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
hon = colF1.number_input("Montant honoraires (US $)", min_value=0.0)
frais = colF2.number_input("Autres frais (US $)", min_value=0.0)
colF3.number_input("Total facturé", value=hon + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

colA1, colA2, colA3, colA4 = st.columns(4)
a1 = colA1.number_input("Acompte 1", min_value=0.0)
a2 = colA2.number_input("Acompte 2", min_value=0.0)
a3 = colA3.number_input("Acompte 3", min_value=0.0)
a4 = colA4.number_input("Acompte 4", min_value=0.0)

solde = (hon + frais) - (a1 + a2 + a3 + a4)
st.info(f"💵 Solde restant : ${solde:,.2f}")

mode_paiement = st.selectbox("Mode de paiement", ["", "Chèque", "CB", "Virement", "Venmo"])
escrow = st.checkbox("Escrow actif")
commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if not nom.strip():
        st.error("Nom obligatoire")
        st.stop()

    if mode == "Dossier principal":
        if "Choisir..." in [categorie, sous_categorie, visa]:
            st.error("Catégorie / Sous-catégorie / Visa obligatoires")
            st.stop()

    new_entry = {
        "Dossier N": new_id,
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,
        "Montant honoraires (US $)": hon,
        "Autres frais (US $)": frais,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "mode de paiement": mode_paiement,
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,
        "Date envoi": "",
        "Date acceptation": "",
        "Date refus": "",
        "Date annulation": "",
        "Date reclamation": "",
        "Commentaire": commentaire,
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier {new_id} créé avec succès")
    st.rerun()
