import streamlit as st
import pandas as pd

from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

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
# HELPERS
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

def nouveau_dossier_numero(parent=None):
    nums = [str(c.get("Dossier N", "")) for c in clients]

    # Dossier principal
    if parent is None:
        racines = []
        for n in nums:
            if "-" not in n:
                try:
                    racines.append(int(n))
                except:
                    pass
        return str(max(racines) + 1 if racines else 13000)

    # Sous-dossier
    suffixes = []
    for n in nums:
        if n.startswith(f"{parent}-"):
            try:
                suffixes.append(int(n.split("-")[1]))
            except:
                pass

    next_suffix = max(suffixes) + 1 if suffixes else 1
    return f"{parent}-{next_suffix}"

# ---------------------------------------------------------
# TYPE DE DOSSIER
# ---------------------------------------------------------
st.subheader("🧬 Type de dossier")

type_dossier = st.radio(
    "Créer :",
    ["Dossier principal", "Sous-dossier"],
    horizontal=True
)

if type_dossier == "Dossier principal":
    dossier_n = nouveau_dossier_numero()
    dossier_racine = dossier_n
else:
    parents = sorted(
        {c["Dossier N"].split("-")[0] for c in clients}
    )
    dossier_racine = st.selectbox("📂 Dossier parent", parents)
    dossier_n = nouveau_dossier_numero(dossier_racine)

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations dossier")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=dossier_n, disabled=True)
nom = col2.text_input("Nom du client")
date_dossier = col3.date_input("Date de création")

# ---------------------------------------------------------
# CATEGORIES / VISA
# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

categories = ["Choisir..."] + sorted(visa_raw["Categories"].dropna().unique().tolist())
categorie = colA.selectbox("Catégorie", categories)

if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_raw, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

if sous_categorie != "Choisir...":
    visas = ["Choisir..."] + get_visas(visa_raw, sous_categorie)
else:
    visas = ["Choisir..."]

visa = colC.selectbox("Visa", visas)

# ---------------------------------------------------------
# FINANCES
# ---------------------------------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
montant_hon = colF1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
autres_frais = colF2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
colF3.number_input("Total facturé", value=montant_hon + autres_frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

colA1, colA2, colA3, colA4 = st.columns(4)
a1 = colA1.number_input("Acompte 1", min_value=0.0, step=50.0)
a2 = colA2.number_input("Acompte 2", min_value=0.0, step=50.0)
a3 = colA3.number_input("Acompte 3", min_value=0.0, step=50.0)
a4 = colA4.number_input("Acompte 4", min_value=0.0, step=50.0)

total_encaisse = a1 + a2 + a3 + a4
solde = (montant_hon + autres_frais) - total_encaisse
st.info(f"💵 Solde restant : **${solde:,.2f}**")

mode_paiement = st.selectbox("Mode de paiement", ["", "Chèque", "CB", "Virement", "Venmo"])

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_actif = st.checkbox("Mettre en Escrow (Acompte 1 uniquement)")

# ---------------------------------------------------------
# COMMENTAIRE
# ---------------------------------------------------------
commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if not nom.strip():
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if categorie == "Choisir..." or sous_categorie == "Choisir..." or visa == "Choisir...":
        st.error("❌ Catégorie, Sous-catégorie et Visa sont obligatoires.")
        st.stop()

    new_entry = {
        # IDENTITÉ
        "Dossier ID": dossier_n,
        "Dossier Racine": dossier_racine,
        "Dossier N": dossier_n,

        # INFOS
        "Nom": nom,
        "Date": str(date_dossier),
        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,
        "Commentaire": commentaire,

        # FINANCES
        "Montant honoraires (US $)": montant_hon,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "mode de paiement": mode_paiement,

        # ESCROW (LOGIQUE OFFICIELLE)
        "Escrow": bool(escrow_actif),
        "Escrow_a_reclamer": False,
        "Escrow_reclame": False,

        # STATUTS
        "Dossier envoye": False,
        "Dossier accepte": False,
        "Dossier refuse": False,
        "Dossier Annule": False,
        "RFE": False,

        # DATES STATUTS
        "Date envoi": "",
        "Date acceptation": "",
        "Date refus": "",
        "Date annulation": "",
        "Date reclamation": "",
    }

    clients.append(new_entry)
    db["clients"] = clients
    save_database(db)

    st.success(f"✔ Dossier **{dossier_n}** créé avec succès.")
    st.balloons()