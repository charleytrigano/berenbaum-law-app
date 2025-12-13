import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="➕ Nouveau dossier",
    page_icon="➕",
    layout="wide"
)
render_sidebar()
st.title("➕ Création d’un nouveau dossier")

# =========================================================
# LOAD DATABASE
# =========================================================
db = load_database()
clients = db.get("clients", [])
df = pd.DataFrame(clients)

# =========================================================
# UTILS DOSSIER NUMBER
# =========================================================
def split_dossier(n):
    if isinstance(n, str) and "-" in n:
        p, i = n.split("-", 1)
        return int(p), int(i)
    return int(n), 0

parents = []
children_map = {}

for n in df["Dossier N"]:
    try:
        p, i = split_dossier(str(n))
        parents.append(p)
        children_map.setdefault(p, []).append(i)
    except:
        pass

parents = sorted(set(parents))

def next_parent_number():
    return max(parents) + 1 if parents else 13000

def next_child_number(parent):
    used = children_map.get(parent, [])
    return max(used) + 1 if used else 1

# =========================================================
# TYPE DE DOSSIER
# =========================================================
st.subheader("📁 Type de dossier")

type_dossier = st.radio(
    "Choisir le type de dossier à créer",
    ["Dossier principal", "Sous-dossier"],
    horizontal=True
)

# =========================================================
# NUMÉRO DOSSIER
# =========================================================
st.subheader("🔢 Numéro du dossier")

if type_dossier == "Dossier principal":
    dossier_parent = next_parent_number()
    dossier_n = str(dossier_parent)
    st.info(f"📁 Nouveau dossier principal : **{dossier_n}**")

else:
    parent_selected = st.selectbox(
        "Choisir le dossier parent",
        parents
    )
    child_index = next_child_number(parent_selected)
    dossier_n = f"{parent_selected}-{child_index}"
    st.info(f"📂 Nouveau sous-dossier : **{dossier_n}**")

# =========================================================
# FORMULAIRE
# =========================================================
st.subheader("📄 Informations générales")

c1, c2, c3 = st.columns(3)
c1.text_input("Dossier N", value=dossier_n, disabled=True)
nom = c2.text_input("Nom du client *")
date_dossier = c3.date_input("Date de création")

# =========================================================
# CATÉGORIES & VISA
# =========================================================
st.subheader("🧩 Catégorisation")

visa_df = pd.DataFrame(db.get("visa", []))

def souscats(cat):
    return sorted(
        visa_df[visa_df["Categories"] == cat]["Sous-categories"]
        .dropna()
        .unique()
        .tolist()
    )

def visas(sc):
    return sorted(
        visa_df[visa_df["Sous-categories"] == sc]["Visa"]
        .dropna()
        .unique()
        .tolist()
    )

colA, colB, colC = st.columns(3)

cat_list = ["Choisir…"] + sorted(visa_df["Categories"].dropna().unique())
categorie = colA.selectbox("Catégorie *", cat_list)

if categorie != "Choisir…":
    sous_list = ["Choisir…"] + souscats(categorie)
else:
    sous_list = ["Choisir…"]

sous_categorie = colB.selectbox("Sous-catégorie *", sous_list)

if sous_categorie != "Choisir…":
    visa_list = ["Choisir…"] + visas(sous_categorie)
else:
    visa_list = ["Choisir…"]

visa = colC.selectbox("Visa *", visa_list)

# =========================================================
# FACTURATION
# =========================================================
st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)
honoraires = f1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
autres_frais = f2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
f3.number_input("Total facturé", value=honoraires + autres_frais, disabled=True)

# =========================================================
# ACOMPTES
# =========================================================
st.subheader("🏦 Acomptes")

a1, a2, a3, a4 = st.columns(4)
ac1 = a1.number_input("Acompte 1", min_value=0.0, step=50.0)
ac2 = a2.number_input("Acompte 2", min_value=0.0, step=50.0)
ac3 = a3.number_input("Acompte 3", min_value=0.0, step=50.0)
ac4 = a4.number_input("Acompte 4", min_value=0.0, step=50.0)

solde = (honoraires + autres_frais) - (ac1 + ac2 + ac3 + ac4)
st.info(f"💵 Solde restant : **${solde:,.2f}**")

mode_paiement = st.selectbox(
    "Mode de règlement",
    ["", "Chèque", "CB", "Virement", "Venmo"]
)

# =========================================================
# ESCROW & COMMENTAIRE
# =========================================================
escrow = st.checkbox("Mettre en Escrow (Acompte 1 uniquement)")
commentaire = st.text_area("📝 Commentaire")

# =========================================================
# ENREGISTREMENT
# =========================================================
if st.button("💾 Enregistrer le dossier", type="primary"):

    if not nom.strip():
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if "Choisir" in [categorie, sous_categorie, visa]:
        st.error("❌ Catégorie, Sous-catégorie et Visa sont obligatoires.")
        st.stop()

    new_entry = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,

        "Acompte 1": ac1,
        "Acompte 2": ac2,
        "Acompte 3": ac3,
        "Acompte 4": ac4,
        "mode de paiement": mode_paiement,

        # ESCROW (logique validée)
        "Escrow": bool(escrow),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        # STATUTS
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

    st.success(f"✔ Dossier **{dossier_n}** créé avec succès.")
    st.balloons()