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
df = pd.DataFrame(clients)

# Toujours travailler Dossier N en STRING
if not df.empty:
    df["Dossier N"] = df["Dossier N"].astype(str)

# ---------------------------------------------------------
# GÉNÉRATION DOSSIER N (xxxxx / xxxxx-1 / xxxxx-2)
# ---------------------------------------------------------
def next_dossier_number(base_number: str) -> str:
    """
    Retourne le prochain suffixe disponible :
    13000 -> 13000
    13000 existe -> 13000-1
    13000-1 existe -> 13000-2
    """
    existing = df["Dossier N"].tolist() if not df.empty else []

    if base_number not in existing:
        return base_number

    i = 1
    while f"{base_number}-{i}" in existing:
        i += 1
    return f"{base_number}-{i}"

# Numéro parent proposé
base_number = st.text_input(
    "Dossier N (parent)",
    value=str(
        max(
            [int(x.split("-")[0]) for x in df["Dossier N"]] if not df.empty else [13000]
        ) + 1
    )
)

dossier_n = next_dossier_number(base_number)
st.info(f"📁 Dossier créé : **{dossier_n}**")

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("📄 Informations générales")

c1, c2, c3 = st.columns(3)
nom = c1.text_input("Nom du client")
date_dossier = c2.date_input("Date du dossier")
visa = c3.text_input("Visa")

c4, c5 = st.columns(2)
categorie = c4.text_input("Catégorie")
sous_categorie = c5.text_input("Sous-catégorie")

# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
st.subheader("💰 Facturation")

f1, f2, f3 = st.columns(3)
hon = f1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
frais = f2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
f3.number_input("Total facturé", hon + frais, disabled=True)

# ---------------------------------------------------------
# ACOMPTES COMPLETS
# ---------------------------------------------------------
st.subheader("🏦 Paiements")

modes = ["", "Chèque", "CB", "Virement", "Venmo"]
acomptes = {}
total_encaisse = 0.0

for i in range(1, 5):
    st.markdown(f"### Acompte {i}")
    a1, a2, a3 = st.columns(3)

    montant = a1.number_input(f"Montant Acompte {i}", min_value=0.0, step=50.0)
    date_paiement = a2.date_input(f"Date Acompte {i}", value=None)
    mode = a3.selectbox(f"Mode Acompte {i}", modes)

    acomptes[i] = {
        "montant": montant,
        "date": str(date_paiement) if date_paiement else "",
        "mode": mode,
    }

    total_encaisse += montant

solde = (hon + frais) - total_encaisse
st.info(f"💵 Total encaissé : ${total_encaisse:,.2f} — Solde dû : ${solde:,.2f}")

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
st.subheader("💼 Escrow")

escrow_actif = st.checkbox("Escrow actif")
st.caption("ℹ️ Le montant en escrow correspond uniquement à **Acompte 1**")

# ---------------------------------------------------------
# COMMENTAIRE
# ---------------------------------------------------------
commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if not nom.strip():
        st.error("❌ Le nom est obligatoire.")
        st.stop()

    new_entry = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Date": str(date_dossier),

        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": hon,
        "Autres frais (US $)": frais,

        "Acompte 1": acomptes[1]["montant"],
        "Acompte 2": acomptes[2]["montant"],
        "Acompte 3": acomptes[3]["montant"],
        "Acompte 4": acomptes[4]["montant"],

        "Date Acompte 1": acomptes[1]["date"],
        "Date Acompte 2": acomptes[2]["date"],
        "Date Acompte 3": acomptes[3]["date"],
        "Date Acompte 4": acomptes[4]["date"],

        "Mode Acompte 1": acomptes[1]["mode"],
        "Mode Acompte 2": acomptes[2]["mode"],
        "Mode Acompte 3": acomptes[3]["mode"],
        "Mode Acompte 4": acomptes[4]["mode"],

        # ESCROW (3 états)
        "Escrow": escrow_actif,
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

    st.success(f"✔ Dossier **{dossier_n}** créé avec succès")
    st.rerun()