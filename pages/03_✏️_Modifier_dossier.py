import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database


# ---------------------------------------------------------
# SAFE FLOAT (NE PLANTE JAMAIS)
# ---------------------------------------------------------
def safe_float(x):
    try:
        if x in ("", None, "nan", "NaN"):
            return 0.0
        return float(x)
    except:
        return 0.0


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")

st.title("✏️ Modifier un dossier")


# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients)


# ---------------------------------------------------------
# SELECT DOSSIER
# ---------------------------------------------------------
st.subheader("Sélectionner un dossier")

liste_dossiers = df["Dossier N"].astype(str).tolist()

selected = st.selectbox("Choisir un dossier", liste_dossiers)

dossier = df[df["Dossier N"].astype(str) == selected].iloc[0]


# ---------------------------------------------------------
# LIGNE 1 : Dossier N – Nom – Date création
# ---------------------------------------------------------
st.subheader("Informations générales")

col1, col2, col3 = st.columns(3)

dossier_n = col1.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
nom = col2.text_input("Nom", value=str(dossier.get("Nom", "")))
date_creation = col3.date_input("Date création", value=pd.to_datetime(dossier.get("Date", None)))


# ---------------------------------------------------------
# LIGNE 2 : Honoraires / Frais / Facturé
# ---------------------------------------------------------
st.subheader("Montants")

colA, colB, colC = st.columns(3)

honoraires = colA.number_input(
    "Montant honoraires (US $)",
    value=safe_float(dossier.get("Montant honoraires (US $)", 0))
)

autres_frais = colB.number_input(
    "Autres frais (US $)",
    value=safe_float(dossier.get("Autres frais (US $)", 0))
)

facture = honoraires + autres_frais
colC.number_input("Facturé (US $)", value=facture, disabled=True)


# ---------------------------------------------------------
# LIGNE 3 : Acomptes + Solde
# ---------------------------------------------------------
st.subheader("Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", value=safe_float(dossier.get("Acompte 1", 0)))
a2 = colA2.number_input("Acompte 2", value=safe_float(dossier.get("Acompte 2", 0)))
a3 = colA3.number_input("Acompte 3", value=safe_float(dossier.get("Acompte 3", 0)))
a4 = colA4.number_input("Acompte 4", value=safe_float(dossier.get("Acompte 4", 0)))

solde = facture - (a1 + a2 + a3 + a4)
st.number_input("Solde (US $)", value=solde, disabled=True)


# ---------------------------------------------------------
# LIGNE 4 : Dates des acomptes
# ---------------------------------------------------------
st.subheader("Dates des acomptes")

colD1, colD2, colD3, colD4 = st.columns(4)

date_a1 = colD1.date_input("Date Acompte 1", value=pd.to_datetime(dossier.get("Date Acompte 1", None)))
date_a2 = colD2.date_input("Date Acompte 2", value=pd.to_datetime(dossier.get("Date Acompte 2", None)))
date_a3 = colD3.date_input("Date Acompte 3", value=pd.to_datetime(dossier.get("Date Acompte 3", None)))
date_a4 = colD4.date_input("Date Acompte 4", value=pd.to_datetime(dossier.get("Date Acompte 4", None)))


# ---------------------------------------------------------
# LIGNE 5 : Statuts du dossier
# ---------------------------------------------------------
st.subheader("Statut du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=dossier.get("Dossier envoyé", False))
accepte = colS2.checkbox("Dossier accepté", value=dossier.get("Dossier accepté", False))
refuse = colS3.checkbox("Dossier refusé", value=dossier.get("Dossier refusé", False))
annule = colS4.checkbox("Dossier annulé", value=dossier.get("Dossier annulé", False))
rfe = colS5.checkbox("RFE", value=dossier.get("RFE", False))


# ---------------------------------------------------------
# LIGNE 6 : Dates des statuts
# ---------------------------------------------------------
st.subheader("Dates des statuts")

colT1, colT2, colT3, colT4, colT5 = st.columns(5)

date_envoye = colT1.date_input("Date envoyé", value=pd.to_datetime(dossier.get("Date envoyé", None)))
date_accepte = colT2.date_input("Date accepté", value=pd.to_datetime(dossier.get("Date accepté", None)))
date_refuse = colT3.date_input("Date refusé", value=pd.to_datetime(dossier.get("Date refusé", None)))
date_annule = colT4.date_input("Date annulé", value=pd.to_datetime(dossier.get("Date annulé", None)))
date_rfe = colT5.date_input("Date RFE", value=pd.to_datetime(dossier.get("Date RFE", None)))


# ---------------------------------------------------------
# LIGNE 7 : Escrow
# ---------------------------------------------------------
escrow = st.checkbox("Escrow", value=dossier.get("Escrow", False))


# ---------------------------------------------------------
# BOUTON SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    idx = df[df["Dossier N"].astype(str) == selected].index[0]

    df.loc[idx] = {
        "Dossier N": dossier_n,
        "Nom": nom,
        "Date": str(date_creation),
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,
        "Total facturé": facture,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "Solde": solde,
        "Date Acompte 1": str(date_a1),
        "Date Acompte 2": str(date_a2),
        "Date Acompte 3": str(date_a3),
        "Date Acompte 4": str(date_a4),
        "Dossier envoyé": envoye,
        "Dossier accepté": accepte,
        "Dossier refusé": refuse,
        "Dossier annulé": annule,
        "RFE": rfe,
        "Date envoyé": str(date_envoye),
        "Date accepté": str(date_accepte),
        "Date refusé": str(date_refuse),
        "Date annulé": str(date_annule),
        "Date RFE": str(date_rfe),
        "Escrow": escrow,
    }

    db["clients"] = df.to_dict(orient="records")
    save_database(db)

    st.success("Modifications enregistrées ✔")
    st.balloons()
