import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database
from utils.visa_filters import clean_visa_df

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# CHARGEMENT DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])
visa_raw = pd.DataFrame(db.get("visa", []))

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)
visa_table = clean_visa_df(visa_raw)

# ---------------------------------------------------------
# SELECTION DOSSIER
# ---------------------------------------------------------
st.subheader("📁 Sélectionner un dossier")

liste_dossiers = sorted(df["Dossier N"].astype(str).tolist())
dossier_id = st.selectbox("Choisir un dossier", liste_dossiers)

dossier = df[df["Dossier N"].astype(str) == dossier_id].iloc[0].copy()

# ---------------------------------------------------------
# FORMULAIRE DE MODIFICATION
# ---------------------------------------------------------
st.subheader("📌 Informations principales")

col1, col2, col3 = st.columns(3)
dossier_num = col1.text_input("Dossier N", value=dossier["Dossier N"])
nom = col2.text_input("Nom", value=dossier["Nom"])
date_creation = col3.date_input("Date de création",
                                value=pd.to_datetime(dossier.get("Date", None)))

# ---------------------------------------------------------
# FILTRES INTELLIGENTS POUR VISA
# ---------------------------------------------------------
st.subheader("🧩 Catégories & Visa")

real_categories = sorted(
    set(visa_table["Categories"]) - set(visa_table["Sous-categories"])
)

colA, colB, colC = st.columns(3)

categorie = colA.selectbox(
    "Catégorie",
    [""] + real_categories,
    index=([""] + real_categories).index(dossier.get("Categories", "")) 
      if dossier.get("Categories", "") in [""] + real_categories else 0
)

if categorie:
    souscat_list = [""] + sorted(
        visa_table.loc[visa_table["Categories"] == categorie, "Sous-categories"].unique()
    )
else:
    souscat_list = [""]

souscat = colB.selectbox(
    "Sous-catégorie",
    souscat_list,
    index=souscat_list.index(dossier.get("Sous-categories", "")) 
      if dossier.get("Sous-categories", "") in souscat_list else 0
)

if souscat:
    visas = [""] + sorted(
        visa_table.loc[visa_table["Sous-categories"] == souscat, "Visa"].unique()
    )
elif categorie:
    visas = [""] + sorted(
        visa_table.loc[visa_table["Categories"] == categorie, "Visa"].unique()
    )
else:
    visas = [""]

visa_choice = colC.selectbox(
    "Visa",
    visas,
    index=visas.index(dossier.get("Visa", "")) if dossier.get("Visa", "") in visas else 0
)

# ---------------------------------------------------------
# HONORAIRES & FRAIS
# ---------------------------------------------------------
st.subheader("💰 Honoraires & Frais")

colH1, colH2, colH3 = st.columns(3)

honoraires = colH1.number_input(
    "Montant honoraires (US $)", 
    min_value=0.0, 
    step=100.0, 
    value=float(dossier.get("Montant honoraires (US $)", 0))
)

autres_frais = colH2.number_input(
    "Autres frais (US $)", 
    min_value=0.0, 
    step=50.0, 
    value=float(dossier.get("Autres frais (US $)", 0))
)

facture = honoraires + autres_frais
colH3.number_input("Total facturé", value=facture, disabled=True)

# ---------------------------------------------------------
# ACOMPTES + DATES
# ---------------------------------------------------------
st.subheader("💵 Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", value=float(dossier.get("Acompte 1", 0)))
a2 = colA2.number_input("Acompte 2", value=float(dossier.get("Acompte 2", 0)))
a3 = colA3.number_input("Acompte 3", value=float(dossier.get("Acompte 3", 0)))
a4 = colA4.number_input("Acompte 4", value=float(dossier.get("Acompte 4", 0)))

colD1, colD2, colD3, colD4 = st.columns(4)

def safe_date(value):
    try:
        return pd.to_datetime(value) if value not in ["", None] else None
    except:
        return None

date_a1 = colD1.date_input("Date Acompte 1", value=safe_date(dossier.get("Date Acompte 1")))
date_a2 = colD2.date_input("Date Acompte 2", value=safe_date(dossier.get("Date Acompte 2")))
date_a3 = colD3.date_input("Date Acompte 3", value=safe_date(dossier.get("Date Acompte 3")))
date_a4 = colD4.date_input("Date Acompte 4", value=safe_date(dossier.get("Date Acompte 4")))

# ---------------------------------------------------------
# STATUTS DU DOSSIER
# ---------------------------------------------------------
st.subheader("📌 Statut du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", bool(dossier.get("Dossier envoye", False)))
accepte = colS2.checkbox("Dossier accepté", bool(dossier.get("Dossier accepte", False)))
refuse = colS3.checkbox("Dossier refusé", bool(dossier.get("Dossier refuse", False)))
annule = colS4.checkbox("Dossier annulé", bool(dossier.get("Dossier Annule", False)))
rfe = colS5.checkbox("RFE", bool(dossier.get("RFE", False)))

colSD1, colSD2, colSD3, colSD4, colSD5 = st.columns(5)

date_env = colSD1.date_input("Date envoyé", value=safe_date(dossier.get("Date envoi")))
date_acc = colSD2.date_input("Date accepté", value=safe_date(dossier.get("Date acceptation")))
date_ref = colSD3.date_input("Date refus", value=safe_date(dossier.get("Date refus")))
date_ann = colSD4.date_input("Date annulation", value=safe_date(dossier.get("Date annulation")))
date_rfe = colSD5.date_input("Date RFE", value=safe_date(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("Escrow ?", bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):

    new_data = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_creation),

        "Categories": categorie,
        "Sous-categories": souscat,
        "Visa": visa_choice,

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,

        "Date Acompte 1": str(date_a1) if date_a1 else "",
        "Date Acompte 2": str(date_a2) if date_a2 else "",
        "Date Acompte 3": str(date_a3) if date_a3 else "",
        "Date Acompte 4": str(date_a4) if date_a4 else "",

        "Dossier envoye": envoye,
        "Date envoi": str(date_env) if date_env else "",

        "Dossier accepte": accepte,
        "Date acceptation": str(date_acc) if date_acc else "",

        "Dossier refuse": refuse,
        "Date refus": str(date_ref) if date_ref else "",

        "Dossier Annule": annule,
        "Date annulation": str(date_ann) if date_ann else "",

        "RFE": rfe,
        "Date reclamation": str(date_rfe) if date_rfe else "",

        "Escrow": escrow,

        "Total facturé": facture,
        "Montant encaissé": a1 + a2 + a3 + a4,
        "Solde": facture - (a1 + a2 + a3 + a4)
    }

    # Remplacer l’ancien dossier
    for i, c in enumerate(clients):
        if str(c["Dossier N"]) == str(dossier_id):
            clients[i] = new_data
            break

    db["clients"] = clients
    save_database(db)

    st.success("✅ Dossier mis à jour avec succès !")
    st.balloons()
