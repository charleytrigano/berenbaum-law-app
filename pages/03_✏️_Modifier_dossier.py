import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

# ---------------------------------------------------------
# LOAD DATABASE
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# Sélection du dossier
# ---------------------------------------------------------
st.subheader("Sélectionner un dossier")

liste = df["Dossier N"].astype(str) + " - " + df["Nom"]
selection = st.selectbox("Choisir un dossier à modifier", liste)

index = liste.tolist().index(selection)
dossier = clients[index]

# ---------------------------------------------------------
# LIGNE 1 — Dossier N / Nom / Date de création
# ---------------------------------------------------------
st.subheader("Informations du dossier")

col1, col2, col3 = st.columns(3)

dossier_num = col1.number_input("Dossier N", value=int(dossier.get("Dossier N", 0)))
nom = col2.text_input("Nom", value=dossier.get("Nom", ""))
date_creation = col3.date_input("Date de création", value=pd.to_datetime(dossier.get("Date")))

# ---------------------------------------------------------
# LIGNE 2 — Honoraires / Frais / Facturé
# ---------------------------------------------------------
st.subheader("Montants")

colH1, colH2, colH3 = st.columns(3)

honoraires = colH1.number_input(
    "Montant honoraires (US $)",
    value=float(dossier.get("Montant honoraires (US $)", 0) or 0)
)

autres_frais = colH2.number_input(
    "Autres frais (US $)",
    value=float(dossier.get("Autres frais (US $)", 0) or 0)
)

facture = honoraires + autres_frais
colH3.number_input("Total facturé (US $)", value=facture, disabled=True)


# ---------------------------------------------------------
# LIGNE 3 — Acomptes + Solde
# ---------------------------------------------------------
st.subheader("Paiements")

colA1, colA2, colA3, colA4, colA5 = st.columns(5)

a1 = colA1.number_input("Acompte 1", value=float(dossier.get("Acompte 1", 0)))
a2 = colA2.number_input("Acompte 2", value=float(dossier.get("Acompte 2", 0)))
a3 = colA3.number_input("Acompte 3", value=float(dossier.get("Acompte 3", 0)))
a4 = colA4.number_input("Acompte 4", value=float(dossier.get("Acompte 4", 0)))

solde = facture - (a1 + a2 + a3 + a4)
colA5.number_input("Solde (US $)", value=solde, disabled=True)

# ---------------------------------------------------------
# LIGNE 4 — Dates d’acomptes
# ---------------------------------------------------------
st.subheader("Dates des acomptes")

colD1, colD2, colD3, colD4 = st.columns(4)

date_a1 = colD1.date_input("Date acompte 1", value=pd.to_datetime(dossier.get("Date Acompte 1", None)) if dossier.get("Date Acompte 1") else None)
date_a2 = colD2.date_input("Date acompte 2", value=pd.to_datetime(dossier.get("Date Acompte 2", None)) if dossier.get("Date Acompte 2") else None)
date_a3 = colD3.date_input("Date acompte 3", value=pd.to_datetime(dossier.get("Date Acompte 3", None)) if dossier.get("Date Acompte 3") else None)
date_a4 = colD4.date_input("Date acompte 4", value=pd.to_datetime(dossier.get("Date Acompte 4", None)) if dossier.get("Date Acompte 4") else None)

# ---------------------------------------------------------
# LIGNE 5 — États du dossier
# ---------------------------------------------------------
st.subheader("Statut du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=dossier.get("Dossier envoyé", False))
accepte = colS2.checkbox("Dossier accepté", value=dossier.get("Dossier accepté", False))
refuse = colS3.checkbox("Dossier refusé", value=dossier.get("Dossier refusé", False))
annule = colS4.checkbox("Dossier annulé", value=dossier.get("Dossier annulé", False))
rfe = colS5.checkbox("RFE", value=dossier.get("RFE", False))

# ---------------------------------------------------------
# LIGNE 6 — Dates des statuts
# ---------------------------------------------------------
st.subheader("Dates des statuts")

colT1, colT2, colT3, colT4, colT5 = st.columns(5)

date_envoye = colT1.date_input("Date envoyé", value=pd.to_datetime(dossier.get("Date envoyé", None)) if dossier.get("Date envoyé") else None)
date_accepte = colT2.date_input("Date accepté", value=pd.to_datetime(dossier.get("Date accepté", None)) if dossier.get("Date accepté") else None)
date_refuse = colT3.date_input("Date refusé", value=pd.to_datetime(dossier.get("Date refusé", None)) if dossier.get("Date refusé") else None)
date_annule = colT4.date_input("Date annulé", value=pd.to_datetime(dossier.get("Date annulé", None)) if dossier.get("Date annulé") else None)
date_rfe = colT5.date_input("Date RFE", value=pd.to_datetime(dossier.get("Date RFE", None)) if dossier.get("Date RFE") else None)

# ---------------------------------------------------------
# LIGNE 7 — Escrow
# ---------------------------------------------------------
escrow = st.checkbox("Escrow", value=dossier.get("Escrow", False))

# ---------------------------------------------------------
# ENREGISTREMENT
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    dossier.update({
        "Dossier N": dossier_num,
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

        "Date Acompte 1": str(date_a1) if date_a1 else "",
        "Date Acompte 2": str(date_a2) if date_a2 else "",
        "Date Acompte 3": str(date_a3) if date_a3 else "",
        "Date Acompte 4": str(date_a4) if date_a4 else "",

        "Dossier envoyé": envoye,
        "Dossier accepté": accepte,
        "Dossier refusé": refuse,
        "Dossier annulé": annule,
        "RFE": rfe,

        "Date envoyé": str(date_envoye) if date_envoye else "",
        "Date accepté": str(date_accepte) if date_accepte else "",
        "Date refusé": str(date_refuse) if date_refuse else "",
        "Date annulé": str(date_annule) if date_annule else "",
        "Date RFE": str(date_rfe) if date_rfe else "",

        "Escrow": escrow,
    })

    save_database(db)
    st.success("✔ Dossier mis à jour avec succès !")
    st.balloons()
