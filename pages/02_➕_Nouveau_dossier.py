import streamlit as st
import pandas as pd
from utils.sidebar import render_sidebar
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG & SIDEBAR
# ---------------------------------------------------------
st.set_page_config(page_title="➕ Nouveau dossier", page_icon="➕", layout="wide")
render_sidebar()
st.title("➕ Création d’un dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# OUTILS
# ---------------------------------------------------------
def normalize_str(x):
    return "" if x is None else str(x)

def get_base_numbers():
    """Retourne les numéros principaux existants (sans suffixe)."""
    bases = set()
    for v in df["Dossier N"].astype(str):
        base = v.split("-")[0]
        if base.isdigit():
            bases.add(base)
    return sorted(bases, key=int)

def next_main_number():
    bases = get_base_numbers()
    return str(int(bases[-1]) + 1) if bases else "13000"

def next_sub_number(base):
    subs = []
    for v in df["Dossier N"].astype(str):
        if v.startswith(f"{base}-"):
            try:
                subs.append(int(v.split("-")[1]))
            except:
                pass
    return f"{base}-{max(subs) + 1}" if subs else f"{base}-1"

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
# TYPE DE DOSSIER
# ---------------------------------------------------------
st.subheader("📌 Type de dossier")

colT1, colT2 = st.columns(2)
mode = colT1.radio(
    "Créer :",
    ["Dossier principal", "Sous-dossier (suffixe -1, -2, …)"]
)

if mode == "Dossier principal":
    dossier_id = next_main_number()
else:
    base_choices = get_base_numbers()
    base_selected = colT2.selectbox(
        "Dossier parent",
        base_choices
    )
    dossier_id = next_sub_number(base_selected)

st.info(f"📁 Numéro attribué : **{dossier_id}**")

# ---------------------------------------------------------
# INFORMATIONS GÉNÉRALES
# ---------------------------------------------------------
st.subheader("📄 Informations générales")

col1, col2, col3 = st.columns(3)
col1.text_input("Dossier N", value=dossier_id, disabled=True)
nom = col2.text_input("Nom du client")
date_dossier = col3.date_input("Date de création")

# ---------------------------------------------------------
# CATÉGORISATION
# ---------------------------------------------------------
st.subheader("🧩 Catégorisation")

colA, colB, colC = st.columns(3)

cat_list = ["Choisir..."] + sorted(visa_raw["Categories"].dropna().unique())
categorie = colA.selectbox("Catégorie", cat_list)

if categorie != "Choisir...":
    souscats = ["Choisir..."] + get_souscats(visa_raw, categorie)
else:
    souscats = ["Choisir..."]

sous_categorie = colB.selectbox("Sous-catégorie", souscats)

if sous_categorie != "Choisir...":
    visa_list = ["Choisir..."] + get_visas(visa_raw, sous_categorie)
else:
    visa_list = ["Choisir..."]

visa = colC.selectbox("Visa", visa_list)

# ---------------------------------------------------------
# FACTURATION
# ---------------------------------------------------------
st.subheader("💰 Facturation")

colF1, colF2, colF3 = st.columns(3)
honoraires = colF1.number_input("Montant honoraires (US $)", min_value=0.0, step=50.0)
autres_frais = colF2.number_input("Autres frais (US $)", min_value=0.0, step=10.0)
colF3.number_input("Total facturé", value=honoraires + autres_frais, disabled=True)

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
solde = (honoraires + autres_frais) - total_encaisse
st.info(f"💵 Solde restant : **${solde:,.2f}**")

mode_paiement = st.selectbox(
    "Mode de paiement",
    ["", "Chèque", "CB", "Virement", "Venmo"]
)

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("💼 Mettre en Escrow (Acompte 1 uniquement)")

# ---------------------------------------------------------
# COMMENTAIRE
# ---------------------------------------------------------
commentaire = st.text_area("📝 Commentaire")

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer le dossier", type="primary"):

    if nom.strip() == "":
        st.error("❌ Le nom du client est obligatoire.")
        st.stop()

    if categorie == "Choisir..." or sous_categorie == "Choisir..." or visa == "Choisir...":
        st.error("❌ Catégorie, Sous-catégorie et Visa sont obligatoires.")
        st.stop()

    new_entry = {
        "Dossier N": dossier_id,
        "Nom": nom,
        "Date": str(date_dossier),

        "Categories": categorie,
        "Sous-categories": sous_categorie,
        "Visa": visa,

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,

        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,

        "mode de paiement": mode_paiement,

        # ESCROW – logique claire
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

    st.success(f"✔ Dossier **{dossier_id}** créé avec succès.")
    st.balloons()
