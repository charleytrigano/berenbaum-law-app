import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database


# =========================================================
# 🔧 Fonction safe_float — empêche les crash float("") !
# =========================================================
def safe_float(x):
    try:
        if x in ["", None]:
            return 0.0
        return float(x)
    except:
        return 0.0


# =========================================================
# 🔧 Fonction safe_date — convertit "" → None proprement
# =========================================================
def safe_date(x):
    try:
        if x in ["", None]:
            return None
        return pd.to_datetime(x).date()
    except:
        return None


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")


# =========================================================
# CHARGEMENT BASE
# =========================================================
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.warning("Aucun dossier trouvé.")
    st.stop()

df = pd.DataFrame(clients)

# Sélection dossier
liste = df["Dossier N"].astype(str) + " – " + df["Nom"].astype(str)
selection = st.selectbox("Sélectionner un dossier", liste)

index = liste.tolist().index(selection)
dossier = clients[index]


# =========================================================
# FORMULAIRE
# =========================================================

st.subheader("📄 Informations générales")

col1, col2, col3 = st.columns(3)

dossier_num = col1.text_input("Dossier N", value=str(dossier.get("Dossier N", "")))
nom = col2.text_input("Nom", value=str(dossier.get("Nom", "")))
date_dossier = col3.date_input(
    "Date",
    value=safe_date(dossier.get("Date")),
)


# =========================================================
# MONTANTS
# =========================================================
st.subheader("💵 Montants")

colH1, colH2, colH3 = st.columns(3)

honoraires = colH1.number_input(
    "Montant honoraires (US $)",
    value=safe_float(dossier.get("Montant honoraires (US $)", 0))
)

autres_frais = colH2.number_input(
    "Autres frais (US $)",
    value=safe_float(dossier.get("Autres frais (US $)", 0))
)

facture_total = honoraires + autres_frais
colH3.metric("Total facturé", f"${facture_total:,.2f}")


# =========================================================
# ACOMPTES
# =========================================================
st.subheader("💳 Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", value=safe_float(dossier.get("Acompte 1", 0)))
a2 = colA2.number_input("Acompte 2", value=safe_float(dossier.get("Acompte 2", 0)))
a3 = colA3.number_input("Acompte 3", value=safe_float(dossier.get("Acompte 3", 0)))
a4 = colA4.number_input("Acompte 4", value=safe_float(dossier.get("Acompte 4", 0)))

solde = facture_total - (a1 + a2 + a3 + a4)
st.metric("💰 Solde", f"${solde:,.2f}")


# =========================================================
# DATES DES ACOMPTES
# =========================================================
st.subheader("📅 Dates des acomptes")

colD1, colD2, colD3, colD4 = st.columns(4)

date_a1 = colD1.date_input(
    "Date Acompte 1",
    value=safe_date(dossier.get("Date Acompte 1"))
)

date_a2 = colD2.date_input(
    "Date Acompte 2",
    value=safe_date(dossier.get("Date Acompte 2"))
)

date_a3 = colD3.date_input(
    "Date Acompte 3",
    value=safe_date(dossier.get("Date Acompte 3"))
)

date_a4 = colD4.date_input(
    "Date Acompte 4",
    value=safe_date(dossier.get("Date Acompte 4"))
)


# =========================================================
# STATUTS DU DOSSIER
# =========================================================
st.subheader("📌 Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=bool(dossier.get("Dossier envoye")))
accepte = colS2.checkbox("Dossier accepté", value=bool(dossier.get("Dossier accepte")))
refuse = colS3.checkbox("Dossier refusé", value=bool(dossier.get("Dossier refuse")))
annule = colS4.checkbox("Dossier annulé", value=bool(dossier.get("Dossier Annule")))
rfe = colS5.checkbox("RFE", value=bool(dossier.get("RFE")))

# Dates correspondantes
colDS1, colDS2, colDS3, colDS4, colDS5 = st.columns(5)

date_envoye = colDS1.date_input("Date envoi", value=safe_date(dossier.get("Date envoi")))
date_accepte = colDS2.date_input("Date acceptation", value=safe_date(dossier.get("Date acceptation")))
date_refuse = colDS3.date_input("Date refus", value=safe_date(dossier.get("Date refus")))
date_annule = colDS4.date_input("Date annulation", value=safe_date(dossier.get("Date annulation")))
date_rfe = colDS5.date_input("Date RFE", value=safe_date(dossier.get("Date reclamation")))


# =========================================================
# ESCROW
# =========================================================
st.subheader("🏦 Escrow")

escrow = st.checkbox("Escrow", value=bool(dossier.get("Escrow")))


# =========================================================
# BOUTON SAUVEGARDE
# =========================================================
if st.button("💾 Enregistrer les modifications", type="primary"):
    clients[index] = {
        "Dossier N": dossier_num,
        "Nom": nom,
        "Date": str(date_dossier),

        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": autres_frais,

        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,

        "Date Acompte 1": str(date_a1 or ""),
        "Date Acompte 2": str(date_a2 or ""),
        "Date Acompte 3": str(date_a3 or ""),
        "Date Acompte 4": str(date_a4 or ""),

        "Dossier envoye": envoye,
        "Date envoi": str(date_envoye or ""),
        "Dossier accepte": accepte,
        "Date acceptation": str(date_accepte or ""),
        "Dossier refuse": refuse,
        "Date refus": str(date_refuse or ""),
        "Dossier Annule": annule,
        "Date annulation": str(date_annule or ""),
        "RFE": rfe,
        "Date reclamation": str(date_rfe or ""),

        "Escrow": escrow,
    }

    db["clients"] = clients
    save_database(db)

    st.success("✔ Dossier mis à jour avec succès !")
    st.balloons()
