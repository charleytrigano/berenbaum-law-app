import streamlit as st
import pandas as pd
import datetime
from backend.dropbox_utils import load_database, save_database


# ---------------------------------------------------------
# Sécurisation des conversions
# ---------------------------------------------------------
def safe_float(x):
    try:
        if x is None:
            return 0.0
        return float(x)
    except:
        return 0.0


def safe_date(x):
    """Convertit vers datetime.date ou None pour éviter les plantages Streamlit."""
    try:
        d = pd.to_datetime(x, errors="coerce")
        if pd.isna(d):
            return None
        return d.date()
    except:
        return None


# ---------------------------------------------------------
# Chargement de la base
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

st.title("✏️ Modifier un dossier")

if not clients:
    st.warning("Aucun dossier disponible.")
    st.stop()

# Liste des dossiers
liste = [f"{c['Dossier N']} - {c['Nom']}" for c in clients]
selection = st.selectbox("Sélectionner un dossier", liste)

index = liste.index(selection)
dossier = clients[index]


# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.subheader("Informations principales")

colA, colB, colC = st.columns(3)

with colA:
    dossier_num = st.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))

with colB:
    nom = st.text_input("Nom", value=str(dossier.get("Nom", "")))

with colC:
    date_crea = st.date_input("Date dossier", value=safe_date(dossier.get("Date")))


# ---------------------------------------------------------
# LIGNE FINANCIÈRE
# ---------------------------------------------------------
st.subheader("Données financières")

col1, col2, col3 = st.columns(3)

with col1:
    honoraires = st.number_input(
        "Montant honoraires (US $)",
        value=safe_float(dossier.get("Montant honoraires (US $)", 0)),
        min_value=0.0,
        format="%.2f"
    )

with col2:
    autres = st.number_input(
        "Autres frais (US $)",
        value=safe_float(dossier.get("Autres frais (US $)", 0)),
        min_value=0.0,
        format="%.2f"
    )

with col3:
    facture = honoraires + autres
    st.number_input("Total facturé", value=facture, disabled=True, format="%.2f")


# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.subheader("Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

with colA1:
    a1 = st.number_input("Acompte 1", value=safe_float(dossier.get("Acompte 1", 0)))
with colA2:
    a2 = st.number_input("Acompte 2", value=safe_float(dossier.get("Acompte 2", 0)))
with colA3:
    a3 = st.number_input("Acompte 3", value=safe_float(dossier.get("Acompte 3", 0)))
with colA4:
    a4 = st.number_input("Acompte 4", value=safe_float(dossier.get("Acompte 4", 0)))

total_encaissé = a1 + a2 + a3 + a4
solde = facture - total_encaissé

st.write(f"**💵 Solde restant : {solde:.2f} $**")


# ---------------------------------------------------------
# DATES ACOMPTES
# ---------------------------------------------------------
st.subheader("Dates des acomptes")

colD1, colD2, colD3, colD4 = st.columns(4)

date_a1 = colD1.date_input("Date Acompte 1", value=safe_date(dossier.get("Date Acompte 1")))
date_a2 = colD2.date_input("Date Acompte 2", value=safe_date(dossier.get("Date Acompte 2")))
date_a3 = colD3.date_input("Date Acompte 3", value=safe_date(dossier.get("Date Acompte 3")))
date_a4 = colD4.date_input("Date Acompte 4", value=safe_date(dossier.get("Date Acompte 4")))


# ---------------------------------------------------------
# STATUTS DOSSIER
# ---------------------------------------------------------
st.subheader("Statut du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye  = colS1.checkbox("Dossier envoyé", dossier.get("Envoye", False))
accepte = colS2.checkbox("Dossier accepté", dossier.get("Accepte", False))
refuse  = colS3.checkbox("Dossier refusé", dossier.get("Refuse", False))
annule  = colS4.checkbox("Dossier annulé", dossier.get("Annule", False))
rfe     = colS5.checkbox("RFE", dossier.get("RFE", False))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)

date_envoye  = colT1.date_input("Date envoyé", value=safe_date(dossier.get("Date envoyé")))
date_accepte = colT2.date_input("Date accepté", value=safe_date(dossier.get("Date accepté")))
date_refuse  = colT3.date_input("Date refusé", value=safe_date(dossier.get("Date refusé")))
date_annule  = colT4.date_input("Date annulé", value=safe_date(dossier.get("Date annulé")))
date_rfe     = colT5.date_input("Date RFE", value=safe_date(dossier.get("Date RFE")))


# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("Escrow ?", dossier.get("Escrow", False))


# ---------------------------------------------------------
# SAUVEGARDE
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    clients[index] = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_crea),
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "Date Acompte 1": str(date_a1) if date_a1 else "",
        "Date Acompte 2": str(date_a2) if date_a2 else "",
        "Date Acompte 3": str(date_a3) if date_a3 else "",
        "Date Acompte 4": str(date_a4) if date_a4 else "",
        "Envoye": envoye,
        "Accepte": accepte,
        "Refuse": refuse,
        "Annule": annule,
        "RFE": rfe,
        "Date envoyé": str(date_envoye) if date_envoye else "",
        "Date accepté": str(date_accepte) if date_accepte else "",
        "Date refusé": str(date_refuse) if date_refuse else "",
        "Date annulé": str(date_annule) if date_annule else "",
        "Date RFE": str(date_rfe) if date_rfe else "",
        "Escrow": escrow,
    }

    db["clients"] = clients
    save_database(db)

    st.success("Modifications enregistrées avec succès ✔")
    st.balloons()
