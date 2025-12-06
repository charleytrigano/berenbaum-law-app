import streamlit as st
import pandas as pd
from backend.dropbox_utils import load_database, save_database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Modifier dossier", page_icon="✏️", layout="wide")
st.title("✏️ Modifier un dossier")

DOSSIER_COL = "Dossier N"

# ---------------------------------------------------------
# LOAD DB
# ---------------------------------------------------------
db = load_database()
clients = db.get("clients", [])

if not clients:
    st.error("Aucun dossier dans la base Dropbox.")
    st.stop()

df = pd.DataFrame(clients)

# ---------------------------------------------------------
# CLEAN DOSSIER NUMBERS
# ---------------------------------------------------------
def safe_int(x):
    try:
        return int(str(x).strip())
    except:
        return None

df[DOSSIER_COL] = df[DOSSIER_COL].apply(safe_int)
df = df.dropna(subset=[DOSSIER_COL])

if df.empty:
    st.error("Aucun numéro de dossier valide trouvé.")
    st.stop()

df = df.sort_values(DOSSIER_COL)

nums = df[DOSSIER_COL].unique().tolist()
selected_num = st.selectbox("Sélectionner un dossier", nums)

selection = df[df[DOSSIER_COL] == selected_num]

if selection.empty:
    st.error("Erreur interne : dossier introuvable.")
    st.stop()

dossier = selection.iloc[0].copy()

# ---------------------------------------------------------
# UTILITAIRE DATES
# ---------------------------------------------------------
def date_or_none(v):
    if v in ("", None, "nan"):
        return None
    try:
        return pd.to_datetime(v).date()
    except:
        return None

# ---------------------------------------------------------
# FORMULAIRE
# ---------------------------------------------------------
st.markdown("## Informations principales")

col1, col2, col3 = st.columns(3)

with col1:
    num = st.number_input("Dossier N", value=int(dossier[DOSSIER_COL]), step=1)

with col2:
    nom = st.text_input("Nom", value=str(dossier.get("Nom", "")))

with col3:
    date_dossier = st.date_input("Date dossier", value=date_or_none(dossier.get("Date")))

# ---------------------------------------------------------
# FINANCIER
# ---------------------------------------------------------
st.markdown("## Données financières")

colA, colB, colC = st.columns(3)

with colA:
    honoraires = st.number_input(
        "Montant honoraires (US $)",
        value=float(dossier.get("Montant honoraires (US $)", 0))
    )
with colB:
    frais = st.number_input(
        "Autres frais (US $)",
        value=float(dossier.get("Autres frais (US $)", 0))
    )
with colC:
    facture = honoraires + frais
    st.number_input("Total facturé", value=facture, disabled=True)

# ---------------------------------------------------------
# ACOMPTES
# ---------------------------------------------------------
st.markdown("## Acomptes")

colA1, colA2, colA3, colA4 = st.columns(4)

a1 = colA1.number_input("Acompte 1", value=float(dossier.get("Acompte 1", 0)))
a2 = colA2.number_input("Acompte 2", value=float(dossier.get("Acompte 2", 0)))
a3 = colA3.number_input("Acompte 3", value=float(dossier.get("Acompte 3", 0)))
a4 = colA4.number_input("Acompte 4", value=float(dossier.get("Acompte 4", 0)))

colD1, colD2, colD3, colD4 = st.columns(4)

da1 = colD1.date_input("Date Acompte 1", value=date_or_none(dossier.get("Date Acompte 1")))
da2 = colD2.date_input("Date Acompte 2", value=date_or_none(dossier.get("Date Acompte 2")))
da3 = colD3.date_input("Date Acompte 3", value=date_or_none(dossier.get("Date Acompte 3")))
da4 = colD4.date_input("Date Acompte 4", value=date_or_none(dossier.get("Date Acompte 4")))

montant_encaisse = a1 + a2 + a3 + a4
solde = facture - montant_encaisse

st.markdown(f"### 💰 Solde restant : **${solde:,.2f}**")

# ---------------------------------------------------------
# STATUTS
# ---------------------------------------------------------
st.markdown("## Statuts du dossier")

colS1, colS2, colS3, colS4, colS5 = st.columns(5)

envoye = colS1.checkbox("Dossier envoyé", value=bool(dossier.get("Dossier envoye", 0)))
accepte = colS2.checkbox("Dossier accepté", value=bool(dossier.get("Dossier accepte", 0)))
refuse = colS3.checkbox("Dossier refusé", value=bool(dossier.get("Dossier refuse", 0)))
annule = colS4.checkbox("Dossier annulé", value=bool(dossier.get("Dossier Annule", 0)))
rfe = colS5.checkbox("RFE", value=bool(dossier.get("RFE", 0)))

colT1, colT2, colT3, colT4, colT5 = st.columns(5)

date_env = colT1.date_input("Date envoi", value=date_or_none(dossier.get("Date envoi")))
date_acc = colT2.date_input("Date acceptation", value=date_or_none(dossier.get("Date acceptation")))
date_ref = colT3.date_input("Date refus", value=date_or_none(dossier.get("Date refus")))
date_ann = colT4.date_input("Date annulation", value=date_or_none(dossier.get("Date annulation")))
date_rfe = colT5.date_input("Date RFE", value=date_or_none(dossier.get("Date reclamation")))

# ---------------------------------------------------------
# ESCROW
# ---------------------------------------------------------
escrow = st.checkbox("Escrow actif ?", value=bool(dossier.get("Escrow", False)))

# ---------------------------------------------------------
# ENREGISTRER LES MODIFICATIONS
# ---------------------------------------------------------
if st.button("💾 Enregistrer les modifications", type="primary"):
    new_values = {
        DOSSIER_COL: num,
        "Nom": nom,
        "Date": str(date_dossier) if date_dossier else "",
        "Montant honoraires (US $)": honoraires,
        "Autres frais (US $)": frais,
        "Acompte 1": a1,
        "Acompte 2": a2,
        "Acompte 3": a3,
        "Acompte 4": a4,
        "Date Acompte 1": str(da1) if da1 else "",
        "Date Acompte 2": str(da2) if da2 else "",
        "Date Acompte 3": str(da3) if da3 else "",
        "Date Acompte 4": str(da4) if da4 else "",
        "Dossier envoye": int(envoye),
        "Date envoi": str(date_env) if date_env else "",
        "Dossier accepte": int(accepte),
        "Date acceptation": str(date_acc) if date_acc else "",
        "Dossier refuse": int(refuse),
        "Date refus": str(date_ref) if date_ref else "",
        "Dossier Annule": int(annule),
        "Date annulation": str(date_ann) if date_ann else "",
        "RFE": int(rfe),
        "Date reclamation": str(date_rfe) if date_rfe else "",
        "Escrow": bool(escrow),
        "Total facturé": facture,
        "Montant encaissé": montant_encaisse,
        "Solde": solde,
    }

    # mettre à jour dans db
    for i, item in enumerate(db["clients"]):
        if safe_int(item.get(DOSSIER_COL)) == selected_num:
            db["clients"][i] = new_values
            break

    save_database(db)
    st.success("Modifications enregistrées ✔")

# ---------------------------------------------------------
# SUPPRESSION
# ---------------------------------------------------------
st.markdown("---")
st.markdown("## ❌ Supprimer ce dossier")

if st.button("🗑️ Supprimer le dossier", type="secondary"):
    # ajouter à l’historique
    if "deleted" not in db:
        db["deleted"] = []

    db["deleted"].append(dossier.to_dict())

    # supprimer des clients
    db["clients"] = [
        item for item in db["clients"]
        if safe_int(item.get(DOSSIER_COL)) != selected_num
    ]

    save_database(db)
    st.success("Dossier supprimé et archivé ✔")
    st.experimental_rerun()
